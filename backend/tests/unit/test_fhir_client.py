"""
Unit tests for app.modules.ingestion.fhir_client.FhirClient

Tests focus on utility methods that don't require a real FHIR server:
- Authorization header construction for various auth types
- Version detection logic
- Connection test failure handling

Network-dependent tests (actual FHIR server connectivity) are not tested here —
those belong in integration tests.
"""
import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.ingestion.fhir_client import FHIR_RESOURCE_TYPES, FhirClient


class TestFhirResourceTypeList:
    def test_resource_types_includes_core_clinical(self):
        """Ensure all clinically relevant FHIR resource types are included."""
        assert "Patient" in FHIR_RESOURCE_TYPES
        assert "Encounter" in FHIR_RESOURCE_TYPES
        assert "Condition" in FHIR_RESOURCE_TYPES
        assert "Procedure" in FHIR_RESOURCE_TYPES
        assert "Observation" in FHIR_RESOURCE_TYPES
        assert "MedicationRequest" in FHIR_RESOURCE_TYPES
        assert "MedicationDispense" in FHIR_RESOURCE_TYPES
        assert "Immunization" in FHIR_RESOURCE_TYPES
        assert "Practitioner" in FHIR_RESOURCE_TYPES

    def test_resource_types_is_non_empty_list(self):
        assert isinstance(FHIR_RESOURCE_TYPES, list)
        assert len(FHIR_RESOURCE_TYPES) > 0


class TestFhirClientAuthHeaderBuilding:
    def test_no_auth_returns_empty_dict(self):
        client = FhirClient(server_url="https://fhir.example.com", auth_type="none")
        headers = client._build_authorization_header()
        assert headers == {}

    def test_bearer_auth_sets_authorization_header(self):
        token = "eyJhbGciOiJSUzI1NiJ9.testtoken"
        client = FhirClient(
            server_url="https://fhir.example.com",
            auth_type="bearer",
            bearer_token=token,
        )
        headers = client._build_authorization_header()
        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {token}"

    def test_basic_auth_encodes_credentials(self):
        client = FhirClient(
            server_url="https://fhir.example.com",
            auth_type="basic",
            username="myuser",
            password="mypassword",
        )
        headers = client._build_authorization_header()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")

        # Verify the base64-encoded credentials decode correctly.
        encoded = headers["Authorization"].split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode()
        assert decoded == "myuser:mypassword"

    def test_basic_auth_with_empty_credentials(self):
        client = FhirClient(
            server_url="https://fhir.example.com",
            auth_type="basic",
        )
        headers = client._build_authorization_header()
        assert "Authorization" in headers
        # Should still build a Basic header, just with empty credentials.
        assert headers["Authorization"].startswith("Basic ")

    def test_unknown_auth_type_returns_empty_dict(self):
        client = FhirClient(
            server_url="https://fhir.example.com",
            auth_type="client_credentials",
        )
        # client_credentials is not explicitly handled — returns empty dict
        headers = client._build_authorization_header()
        assert headers == {}


class TestFhirClientInit:
    def test_client_starts_disconnected(self):
        client = FhirClient(server_url="https://fhir.example.com")
        assert client._client is None
        assert client.fhir_version is None

    def test_server_url_stored(self):
        url = "https://fhir.example.com/R4"
        client = FhirClient(server_url=url)
        assert client.server_url == url

    def test_auth_type_defaults_to_none(self):
        client = FhirClient(server_url="https://fhir.example.com")
        assert client.auth_type == "none"

    @pytest.mark.asyncio
    async def test_close_on_unconnected_client_is_safe(self):
        """Calling close() on a never-connected client should not raise."""
        client = FhirClient(server_url="https://fhir.example.com")
        await client.close()
        assert client._client is None


class TestFhirVersionDetection:
    @pytest.mark.asyncio
    async def test_r5_version_detected_from_capability_statement(self):
        """When fhirVersion starts with '5', should return 'R5'."""
        client = FhirClient(server_url="https://fhir.example.com")
        mock_capability = MagicMock()
        mock_capability.fhirVersion = "5.0.0"

        mock_inner_client = AsyncMock()
        mock_ref = MagicMock()
        mock_ref.to_resource = AsyncMock(return_value=mock_capability)
        mock_inner_client.reference = MagicMock(return_value=mock_ref)
        client._client = mock_inner_client

        version = await client._detect_fhir_version()
        assert version == "R5"

    @pytest.mark.asyncio
    async def test_r4_version_detected_from_capability_statement(self):
        """When fhirVersion starts with '4', should return 'R4'."""
        client = FhirClient(server_url="https://fhir.example.com")
        mock_capability = MagicMock()
        mock_capability.fhirVersion = "4.0.1"

        mock_inner_client = AsyncMock()
        mock_ref = MagicMock()
        mock_ref.to_resource = AsyncMock(return_value=mock_capability)
        mock_inner_client.reference = MagicMock(return_value=mock_ref)
        client._client = mock_inner_client

        version = await client._detect_fhir_version()
        assert version == "R4"

    @pytest.mark.asyncio
    async def test_defaults_to_r4_on_exception(self):
        """If capability statement fetch fails, default to R4."""
        client = FhirClient(server_url="https://fhir.example.com")

        mock_inner_client = AsyncMock()
        mock_ref = MagicMock()
        mock_ref.to_resource = AsyncMock(side_effect=Exception("Connection refused"))
        mock_inner_client.reference = MagicMock(return_value=mock_ref)
        client._client = mock_inner_client

        version = await client._detect_fhir_version()
        assert version == "R4"

    @pytest.mark.asyncio
    async def test_defaults_to_r4_when_fhir_version_attribute_missing(self):
        """If capability statement doesn't have fhirVersion, default to R4."""
        client = FhirClient(server_url="https://fhir.example.com")
        mock_capability = MagicMock(spec=[])  # no fhirVersion attribute

        mock_inner_client = AsyncMock()
        mock_ref = MagicMock()
        mock_ref.to_resource = AsyncMock(return_value=mock_capability)
        mock_inner_client.reference = MagicMock(return_value=mock_ref)
        client._client = mock_inner_client

        version = await client._detect_fhir_version()
        assert version == "R4"
