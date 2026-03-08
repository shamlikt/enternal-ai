"""Transformation engine orchestrator.

Routes FHIR resources to appropriate mapper, validates output via Pydantic CDM schemas,
inserts into PCORnet tables, or routes to quarantine on failure.
"""
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cdm import models as cdm_models
from app.modules.cdm.schemas import (
    ConditionSchema,
    DemographicSchema,
    DeathSchema,
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
from app.modules.transformation import fhir_to_pcornet as fhir_mapper

logger = structlog.get_logger(__name__)

# Observation category codes that indicate vital signs vs lab results
VITAL_SIGN_CATEGORIES = {"vital-signs", "vital signs", "VS"}
LAB_CATEGORIES = {"laboratory", "LAB"}


def _get_observation_category(resource: dict[str, Any]) -> str:
    categories = resource.get("category", [])
    for cat in categories:
        codings = cat.get("coding", [])
        for coding in codings:
            code = coding.get("code", "").lower()
            if "vital" in code:
                return "vital-signs"
            if "lab" in code:
                return "laboratory"
    return "unknown"


class TransformationEngine:
    async def transform_fhir_resource(
        self,
        db: AsyncSession,
        resource: dict[str, Any],
        ingestion_run_id: int,
    ) -> None:
        resource_type = resource.get("resourceType")
        if not resource_type:
            raise ValueError("Resource missing resourceType")

        if resource_type == "Patient":
            await self._transform_patient(db, resource)
        elif resource_type == "Encounter":
            await self._transform_encounter(db, resource)
        elif resource_type == "Condition":
            await self._transform_condition(db, resource)
        elif resource_type == "Procedure":
            await self._transform_procedure(db, resource)
        elif resource_type == "Observation":
            await self._transform_observation(db, resource)
        elif resource_type == "MedicationRequest":
            await self._transform_medication_request(db, resource)
        elif resource_type == "MedicationDispense":
            await self._transform_medication_dispense(db, resource)
        elif resource_type == "Immunization":
            await self._transform_immunization(db, resource)
        elif resource_type == "Practitioner":
            await self._transform_practitioner(db, resource)
        else:
            logger.debug("fhir_resource_type_skipped", resource_type=resource_type)

    async def _upsert(self, db: AsyncSession, model_class, data: dict, pk_field: str) -> None:
        stmt = insert(model_class).values(**data)
        pk_val = data[pk_field]
        existing = await db.get(model_class, pk_val)
        if existing:
            for k, v in data.items():
                if k != pk_field:
                    setattr(existing, k, v)
        else:
            db.add(model_class(**data))
        await db.flush()

    async def _transform_patient(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        demographic_data = fhir_mapper.map_patient_to_demographic(resource)
        validated = DemographicSchema(**demographic_data)
        await self._upsert(db, cdm_models.Demographic, validated.model_dump(), "PATID")

        death_data = fhir_mapper.map_patient_to_death(resource)
        if death_data:
            validated_death = DeathSchema(**death_data)
            await self._upsert(db, cdm_models.Death, validated_death.model_dump(), "PATID")

        await db.commit()

    async def _transform_encounter(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        encounter_data = fhir_mapper.map_encounter_to_encounter(resource)
        validated = EncounterSchema(**encounter_data)
        await self._upsert(db, cdm_models.Encounter, validated.model_dump(), "ENCOUNTERID")
        await db.commit()

    async def _transform_condition(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        diag_data = fhir_mapper.map_condition_to_diagnosis(resource)
        validated_diag = DiagnosisSchema(**diag_data)
        await self._upsert(db, cdm_models.Diagnosis, validated_diag.model_dump(), "DIAGNOSISID")

        cond_data = fhir_mapper.map_condition_to_condition(resource)
        validated_cond = ConditionSchema(**cond_data)
        await self._upsert(db, cdm_models.Condition, validated_cond.model_dump(), "CONDITIONID")

        await db.commit()

    async def _transform_procedure(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        proc_data = fhir_mapper.map_procedure_to_procedures(resource)
        validated = ProceduresSchema(**proc_data)
        await self._upsert(db, cdm_models.Procedures, validated.model_dump(), "PROCEDURESID")
        await db.commit()

    async def _transform_observation(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        category = _get_observation_category(resource)
        if category == "vital-signs":
            vital_data = fhir_mapper.map_observation_to_vital(resource)
            validated = VitalSchema(**vital_data)
            await self._upsert(db, cdm_models.Vital, validated.model_dump(), "VITALID")
        else:
            lab_data = fhir_mapper.map_observation_to_lab(resource)
            validated = LabResultCmSchema(**lab_data)
            await self._upsert(db, cdm_models.LabResultCm, validated.model_dump(), "LAB_RESULT_CM_ID")
        await db.commit()

    async def _transform_medication_request(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        rx_data = fhir_mapper.map_medication_request_to_prescribing(resource)
        validated = PrescribingSchema(**rx_data)
        await self._upsert(db, cdm_models.Prescribing, validated.model_dump(), "PRESCRIBINGID")
        await db.commit()

    async def _transform_medication_dispense(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        disp_data = fhir_mapper.map_medication_dispense_to_dispensing(resource)
        validated = DispensingSchema(**disp_data)
        await self._upsert(db, cdm_models.Dispensing, validated.model_dump(), "DISPENSINGID")
        await db.commit()

    async def _transform_immunization(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        imm_data = fhir_mapper.map_immunization_to_immunization(resource)
        validated = ImmunizationSchema(**imm_data)
        await self._upsert(db, cdm_models.Immunization, validated.model_dump(), "IMMUNIZATIONID")
        await db.commit()

    async def _transform_practitioner(self, db: AsyncSession, resource: dict[str, Any]) -> None:
        provider_data = fhir_mapper.map_practitioner_to_provider(resource)
        validated = ProviderSchema(**provider_data)
        await self._upsert(db, cdm_models.Provider, validated.model_dump(), "PROVIDERID")
        await db.commit()


    def transform_dataview_resource(
        self,
        resource_type: str,
        row: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Route DataView rows to appropriate CDM mapper. Returns (cdm_table_name, mapped_data)."""
        from app.modules.transformation import dataview_to_pcornet as dv_mapper

        return dv_mapper.map_row(resource_type, row)
