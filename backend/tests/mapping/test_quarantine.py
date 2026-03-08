"""Quarantine routing tests.

Tests that records with missing required fields or invalid data are properly
identified and would be routed to quarantine by the transformation engine.
"""
import pytest
from pydantic import ValidationError

from app.modules.transformation import fhir_to_pcornet as mapper
from app.modules.cdm.schemas import DemographicSchema, EncounterSchema, DiagnosisSchema


def test_demographic_schema_requires_patid():
    with pytest.raises(ValidationError):
        DemographicSchema()


def test_demographic_schema_valid_minimal():
    schema = DemographicSchema(PATID="pat-001")
    assert schema.PATID == "pat-001"
    assert schema.SEX is None


def test_encounter_schema_requires_patid_and_encounterid():
    with pytest.raises(ValidationError):
        EncounterSchema(ENCOUNTERID="enc-001")  # missing PATID


def test_diagnosis_schema_requires_diagnosisid_and_patid():
    with pytest.raises(ValidationError):
        DiagnosisSchema(PATID="pat-001")  # missing DIAGNOSISID


def test_patient_missing_id_maps_empty_patid():
    resource = {"resourceType": "Patient", "gender": "female"}
    result = mapper.map_patient_to_demographic(resource)
    assert result["PATID"] == ""


def test_condition_missing_subject_produces_empty_patid():
    resource = {
        "resourceType": "Condition",
        "id": "cond-001",
        "code": {
            "coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"}]
        },
    }
    result = mapper.map_condition_to_diagnosis(resource)
    assert result["PATID"] == ""


def test_observation_vitals_no_values_returns_base_record():
    resource = {
        "resourceType": "Observation",
        "id": "obs-empty",
        "status": "final",
        "category": [
            {"coding": [{"code": "vital-signs"}]}
        ],
        "code": {"coding": [{"system": "http://loinc.org", "code": "55284-4"}]},
        "subject": {"reference": "Patient/pat-001"},
    }
    result = mapper.map_observation_to_vital(resource)
    assert result["VITALID"] == "obs-empty"
    assert result["SYSTOLIC"] is None
    assert result["DIASTOLIC"] is None


def test_medication_dispense_no_ndc_maps_without_ndc():
    resource = {
        "resourceType": "MedicationDispense",
        "id": "disp-no-ndc",
        "status": "completed",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "860975",
                }
            ]
        },
        "subject": {"reference": "Patient/pat-001"},
        "quantity": {"value": 30},
        "whenHandedOver": "2024-03-01",
    }
    result = mapper.map_medication_dispense_to_dispensing(resource)
    assert result["DISPENSINGID"] == "disp-no-ndc"
    assert result["NDC"] == "860975"  # Falls back to first code when no NDC system


def test_immunization_not_done_status():
    resource = {
        "resourceType": "Immunization",
        "id": "imm-not-done",
        "status": "not-done",
        "vaccineCode": {
            "coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "88"}]
        },
        "patient": {"reference": "Patient/pat-001"},
        "occurrenceDateTime": "2024-01-15",
    }
    result = mapper.map_immunization_to_immunization(resource)
    assert result["VX_STATUS"] == "RF"


def test_condition_resolved_status():
    resource = {
        "resourceType": "Condition",
        "id": "cond-resolved",
        "clinicalStatus": {
            "coding": [{"code": "resolved"}]
        },
        "code": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "J06.9"}]},
        "subject": {"reference": "Patient/pat-001"},
        "abatementDateTime": "2024-02-01",
    }
    result = mapper.map_condition_to_condition(resource)
    assert result["CONDITION_STATUS"] == "RS"
    assert result["RESOLVE_DATE"] == "2024-02-01"
