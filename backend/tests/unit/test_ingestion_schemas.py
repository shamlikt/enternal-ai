"""
Unit tests for app.modules.ingestion.schemas — Pydantic validation of ingestion
request/response schemas.
"""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.ingestion.schemas import (
    FhirIntegrationConfig,
    IngestionRunResponse,
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
    QuarantineResponse,
    QuarantineStatsResponse,
    SnowflakeIntegrationConfig,
)


class TestFhirIntegrationConfig:
    def test_minimal_valid(self):
        config = FhirIntegrationConfig(server_url="https://fhir.example.com/R4")
        assert config.server_url == "https://fhir.example.com/R4"
        assert config.auth_type == "none"
        assert config.client_id is None

    def test_bearer_auth(self):
        config = FhirIntegrationConfig(
            server_url="https://fhir.example.com/R4",
            auth_type="bearer",
            bearer_token="eyJhbGciOiJSUzI1NiJ9.test",
        )
        assert config.auth_type == "bearer"
        assert config.bearer_token == "eyJhbGciOiJSUzI1NiJ9.test"

    def test_basic_auth(self):
        config = FhirIntegrationConfig(
            server_url="https://fhir.example.com/R4",
            auth_type="basic",
            username="admin",
            password="secret",
        )
        assert config.auth_type == "basic"
        assert config.username == "admin"

    def test_client_credentials_auth(self):
        config = FhirIntegrationConfig(
            server_url="https://fhir.example.com/R4",
            auth_type="client_credentials",
            client_id="myclientid",
            client_secret="myclientsecret",
        )
        assert config.client_id == "myclientid"

    def test_explicit_r5_version(self):
        config = FhirIntegrationConfig(
            server_url="https://fhir.example.com/R5",
            fhir_version="R5",
        )
        assert config.fhir_version == "R5"

    def test_auto_detect_version_is_none_by_default(self):
        config = FhirIntegrationConfig(server_url="https://fhir.example.com/R4")
        assert config.fhir_version is None

    def test_missing_server_url_raises(self):
        with pytest.raises(ValidationError):
            FhirIntegrationConfig()


class TestSnowflakeIntegrationConfig:
    def test_all_required_fields(self):
        config = SnowflakeIntegrationConfig(
            account="myaccount.us-east-1",
            username="analyst",
            password="securepassword",
            database="ATHENAHEALTH",
            schema_name="DATAVIEW",
            warehouse="COMPUTE_WH",
        )
        assert config.account == "myaccount.us-east-1"
        assert config.schema_name == "DATAVIEW"
        assert config.role is None

    def test_with_role(self):
        config = SnowflakeIntegrationConfig(
            account="myaccount",
            username="analyst",
            password="secret",
            database="DB",
            schema_name="SCHEMA",
            warehouse="WH",
            role="ANALYST_ROLE",
        )
        assert config.role == "ANALYST_ROLE"

    def test_missing_account_raises(self):
        with pytest.raises(ValidationError):
            SnowflakeIntegrationConfig(
                username="analyst",
                password="secret",
                database="DB",
                schema_name="SCHEMA",
                warehouse="WH",
            )

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            SnowflakeIntegrationConfig(
                account="myaccount",
                username="analyst",
                database="DB",
                schema_name="SCHEMA",
                warehouse="WH",
            )


class TestIntegrationCreate:
    def test_fhir_integration_create(self):
        create = IntegrationCreate(
            name="Main FHIR Server",
            type="fhir",
            config_json={"server_url": "https://fhir.example.com/R4"},
        )
        assert create.name == "Main FHIR Server"
        assert create.type == "fhir"
        assert create.config_json["server_url"] == "https://fhir.example.com/R4"

    def test_snowflake_integration_create(self):
        create = IntegrationCreate(
            name="athenahealth DataView",
            type="snowflake",
            config_json={
                "account": "myaccount",
                "username": "analyst",
                "password": "secret",
                "database": "ATHENA",
                "schema_name": "DATAVIEW",
                "warehouse": "WH",
            },
        )
        assert create.type == "snowflake"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            IntegrationCreate(type="fhir", config_json={})

    def test_missing_type_raises(self):
        with pytest.raises(ValidationError):
            IntegrationCreate(name="Test", config_json={})


class TestIntegrationUpdate:
    def test_all_optional(self):
        update = IntegrationUpdate()
        assert update.name is None
        assert update.config_json is None
        assert update.status is None

    def test_partial_update_name_only(self):
        update = IntegrationUpdate(name="New Name")
        assert update.name == "New Name"

    def test_partial_update_status_only(self):
        update = IntegrationUpdate(status="inactive")
        assert update.status == "inactive"


class TestIntegrationResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = IntegrationResponse(
            id=1,
            name="Test FHIR",
            type="fhir",
            status="active",
            created_by=42,
            created_at=now,
            updated_at=now,
        )
        assert resp.id == 1
        assert resp.type == "fhir"
        assert resp.status == "active"

    def test_missing_id_raises(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValidationError):
            IntegrationResponse(
                name="Test",
                type="fhir",
                status="active",
                created_by=1,
                created_at=now,
                updated_at=now,
            )


class TestIngestionRunResponse:
    def test_valid_running_state(self):
        now = datetime.now(timezone.utc)
        run = IngestionRunResponse(
            id=10,
            integration_id=1,
            status="running",
            records_processed=5000,
            records_failed=3,
            started_at=now,
        )
        assert run.status == "running"
        assert run.completed_at is None
        assert run.records_processed == 5000

    def test_completed_state_with_cursor(self):
        now = datetime.now(timezone.utc)
        run = IngestionRunResponse(
            id=11,
            integration_id=1,
            status="completed",
            records_processed=10000,
            records_failed=0,
            started_at=now,
            completed_at=now,
            last_cursor="2024-03-01T00:00:00+00:00",
        )
        assert run.status == "completed"
        assert run.last_cursor is not None

    def test_failed_state_with_error(self):
        now = datetime.now(timezone.utc)
        run = IngestionRunResponse(
            id=12,
            integration_id=1,
            status="failed",
            records_processed=50,
            records_failed=0,
            started_at=now,
            error_message="Connection refused",
        )
        assert run.status == "failed"
        assert run.error_message == "Connection refused"


class TestQuarantineResponse:
    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        qr = QuarantineResponse(
            id=1,
            ingestion_run_id=5,
            error_message="Missing required PATID",
            source_resource_type="Patient",
            source_resource_id="patient-123",
            created_at=now,
        )
        assert qr.source_resource_type == "Patient"
        assert qr.error_message == "Missing required PATID"

    def test_optional_fields_can_be_none(self):
        now = datetime.now(timezone.utc)
        qr = QuarantineResponse(
            id=2,
            ingestion_run_id=5,
            error_message="Unknown error",
            created_at=now,
        )
        assert qr.source_resource_type is None
        assert qr.source_resource_id is None


class TestQuarantineStatsResponse:
    def test_valid_stats(self):
        stats = QuarantineStatsResponse(
            total=150,
            by_resource_type={"Patient": 10, "Encounter": 140},
            recent_errors=["Missing PATID", "Invalid date format"],
        )
        assert stats.total == 150
        assert stats.by_resource_type["Patient"] == 10

    def test_empty_stats(self):
        stats = QuarantineStatsResponse(
            total=0,
            by_resource_type={},
            recent_errors=[],
        )
        assert stats.total == 0
        assert len(stats.recent_errors) == 0
