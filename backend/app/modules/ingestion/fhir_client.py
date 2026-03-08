import structlog
from fhirpy import AsyncFHIRClient
from fhirpy.base.exceptions import ResourceNotFound

logger = structlog.get_logger(__name__)

FHIR_RESOURCE_TYPES = [
    "Patient",
    "Encounter",
    "Condition",
    "Procedure",
    "Observation",
    "MedicationRequest",
    "MedicationDispense",
    "Immunization",
    "Practitioner",
]


class FhirClient:
    def __init__(self, server_url: str, auth_type: str = "none", **auth_kwargs):
        self.server_url = server_url
        self.auth_type = auth_type
        self.auth_kwargs = auth_kwargs
        self._client: AsyncFHIRClient | None = None
        self.fhir_version: str | None = None

    def _build_authorization_header(self) -> dict:
        if self.auth_type == "bearer":
            return {"Authorization": f"Bearer {self.auth_kwargs.get('bearer_token', '')}"}
        if self.auth_type == "basic":
            import base64

            credentials = base64.b64encode(
                f"{self.auth_kwargs.get('username', '')}:{self.auth_kwargs.get('password', '')}".encode()
            ).decode()
            return {"Authorization": f"Basic {credentials}"}
        return {}

    async def connect(self) -> None:
        headers = self._build_authorization_header()
        self._client = AsyncFHIRClient(self.server_url, extra_headers=headers)
        self.fhir_version = await self._detect_fhir_version()
        logger.info("fhir_client_connected", server_url=self.server_url, version=self.fhir_version)

    async def _detect_fhir_version(self) -> str:
        try:
            capability = await self._client.reference("metadata").to_resource()
            fhir_version = getattr(capability, "fhirVersion", None)
            if fhir_version and fhir_version.startswith("5"):
                return "R5"
            return "R4"
        except Exception:
            return "R4"

    async def test_connection(self) -> bool:
        try:
            await self.connect()
            return True
        except Exception as e:
            logger.warning("fhir_connection_test_failed", error=str(e))
            return False

    async def fetch_resources(
        self,
        resource_type: str,
        last_updated: str | None = None,
        page_size: int = 100,
    ):
        if self._client is None:
            await self.connect()

        search_params = {"_count": page_size}
        if last_updated:
            search_params["_lastUpdated"] = f"gt{last_updated}"

        resources = self._client.resources(resource_type)
        search = resources.search(**search_params)

        async for resource in search:
            yield resource

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
