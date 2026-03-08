"""Validation helpers for PCORnet CDM schemas.

Used by the transformation engine to validate mapped data before insertion.
Raises pydantic.ValidationError on invalid data — caller routes to quarantine.
"""
from typing import Any

from pydantic import ValidationError

from app.modules.cdm.schemas import (
    ConditionSchema,
    DeathSchema,
    DemographicSchema,
    DiagnosisSchema,
    DispensingSchema,
    EncounterSchema,
    ImmunizationSchema,
    LabResultCmSchema,
    PrescribingSchema,
    ProceduresSchema,
    ProviderSchema,
    VitalSchema,
)

SCHEMA_MAP = {
    "DEMOGRAPHIC": DemographicSchema,
    "ENCOUNTER": EncounterSchema,
    "DIAGNOSIS": DiagnosisSchema,
    "PROCEDURES": ProceduresSchema,
    "VITAL": VitalSchema,
    "LAB_RESULT_CM": LabResultCmSchema,
    "PRESCRIBING": PrescribingSchema,
    "DISPENSING": DispensingSchema,
    "CONDITION": ConditionSchema,
    "DEATH": DeathSchema,
    "PROVIDER": ProviderSchema,
    "IMMUNIZATION": ImmunizationSchema,
}


def validate_cdm_record(table_name: str, data: dict[str, Any]) -> dict[str, Any]:
    schema_class = SCHEMA_MAP.get(table_name.upper())
    if schema_class is None:
        raise ValueError(f"No schema registered for table: {table_name}")
    validated = schema_class(**data)
    return validated.model_dump()
