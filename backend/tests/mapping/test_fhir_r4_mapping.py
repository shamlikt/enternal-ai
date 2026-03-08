"""FHIR R4 to PCORnet CDM v7.0 mapping tests.

Tests the mapper functions directly (unit tests — no DB required).
"""
import pytest

from app.modules.transformation import fhir_to_pcornet as mapper
from tests.mapping.conftest import load_expected


def test_patient_to_demographic(patient_r4):
    expected = load_expected("patient_r4.json")["DEMOGRAPHIC"]
    result = mapper.map_patient_to_demographic(patient_r4)

    assert result["PATID"] == expected["PATID"]
    assert result["BIRTH_DATE"] == expected["BIRTH_DATE"]
    assert result["SEX"] == expected["SEX"]
    assert result["RAW_SEX"] == expected["RAW_SEX"]
    assert result["RACE"] == expected["RACE"]
    assert result["HISPANIC"] == expected["HISPANIC"]
    assert result["PAT_PREF_LANGUAGE_SPOKEN"] == expected["PAT_PREF_LANGUAGE_SPOKEN"]


def test_patient_no_death_when_alive(patient_r4):
    result = mapper.map_patient_to_death(patient_r4)
    assert result is None


def test_patient_deceased_produces_death_record():
    resource = {
        "resourceType": "Patient",
        "id": "pat-deceased",
        "gender": "female",
        "birthDate": "1940-05-20",
        "deceasedDateTime": "2023-11-01",
    }
    result = mapper.map_patient_to_death(resource)
    assert result is not None
    assert result["PATID"] == "pat-deceased"
    assert result["DEATH_DATE"] == "2023-11-01"
    assert result["DEATH_SOURCE"] == "EH"


def test_patient_deceased_boolean():
    resource = {
        "resourceType": "Patient",
        "id": "pat-dead-bool",
        "deceasedBoolean": True,
    }
    result = mapper.map_patient_to_death(resource)
    assert result is not None
    assert result["PATID"] == "pat-dead-bool"
    assert result["DEATH_DATE"] is None


def test_encounter_to_encounter(encounter_r4):
    expected = load_expected("encounter_r4.json")["ENCOUNTER"]
    result = mapper.map_encounter_to_encounter(encounter_r4)

    assert result["ENCOUNTERID"] == expected["ENCOUNTERID"]
    assert result["PATID"] == expected["PATID"]
    assert result["ADMIT_DATE"] == expected["ADMIT_DATE"]
    assert result["DISCHARGE_DATE"] == expected["DISCHARGE_DATE"]
    assert result["ENC_TYPE"] == expected["ENC_TYPE"]
    assert result["PROVIDERID"] == expected["PROVIDERID"]


def test_encounter_type_mapping():
    resource = {
        "resourceType": "Encounter",
        "id": "enc-ed",
        "subject": {"reference": "Patient/pat-001"},
        "class": {"code": "EMER"},
        "period": {"start": "2024-01-01"},
    }
    result = mapper.map_encounter_to_encounter(resource)
    assert result["ENC_TYPE"] == "ED"


def test_condition_to_diagnosis(condition_r4):
    expected = load_expected("condition_r4.json")["DIAGNOSIS"]
    result = mapper.map_condition_to_diagnosis(condition_r4)

    assert result["DIAGNOSISID"] == expected["DIAGNOSISID"]
    assert result["PATID"] == expected["PATID"]
    assert result["ENCOUNTERID"] == expected["ENCOUNTERID"]
    assert result["DX"] == expected["DX"]
    assert result["DX_TYPE"] == expected["DX_TYPE"]
    assert result["DX_SOURCE"] == expected["DX_SOURCE"]


def test_condition_to_condition(condition_r4):
    expected = load_expected("condition_r4.json")["CONDITION"]
    result = mapper.map_condition_to_condition(condition_r4)

    assert result["CONDITIONID"] == expected["CONDITIONID"]
    assert result["PATID"] == expected["PATID"]
    assert result["CONDITION"] == expected["CONDITION"]
    assert result["CONDITION_STATUS"] == expected["CONDITION_STATUS"]
    assert result["CONDITION_SOURCE"] == expected["CONDITION_SOURCE"]
    assert result["ONSET_DATE"] == expected["ONSET_DATE"]


def test_procedure_to_procedures(procedure_r4):
    expected = load_expected("procedure_r4.json")["PROCEDURES"]
    result = mapper.map_procedure_to_procedures(procedure_r4)

    assert result["PROCEDURESID"] == expected["PROCEDURESID"]
    assert result["PATID"] == expected["PATID"]
    assert result["ENCOUNTERID"] == expected["ENCOUNTERID"]
    assert result["PX"] == expected["PX"]
    assert result["PX_TYPE"] == expected["PX_TYPE"]
    assert result["PX_DATE"] == expected["PX_DATE"]
    assert result["PROVIDERID"] == expected["PROVIDERID"]


def test_observation_vital_to_vital(observation_vitals_r4):
    expected = load_expected("observation_vitals_r4.json")["VITAL"]
    result = mapper.map_observation_to_vital(observation_vitals_r4)

    assert result["VITALID"] == expected["VITALID"]
    assert result["PATID"] == expected["PATID"]
    assert result["ENCOUNTERID"] == expected["ENCOUNTERID"]
    assert result["MEASURE_DATE"] == expected["MEASURE_DATE"]
    assert result["SYSTOLIC"] == expected["SYSTOLIC"]
    assert result["DIASTOLIC"] == expected["DIASTOLIC"]
    assert result["VITAL_SOURCE"] == expected["VITAL_SOURCE"]


def test_observation_lab_to_lab(observation_labs_r4):
    expected = load_expected("observation_labs_r4.json")["LAB_RESULT_CM"]
    result = mapper.map_observation_to_lab(observation_labs_r4)

    assert result["LAB_RESULT_CM_ID"] == expected["LAB_RESULT_CM_ID"]
    assert result["PATID"] == expected["PATID"]
    assert result["LAB_LOINC"] == expected["LAB_LOINC"]
    assert result["RESULT_NUM"] == expected["RESULT_NUM"]
    assert result["RESULT_UNIT"] == expected["RESULT_UNIT"]
    assert result["ABN_IND"] == expected["ABN_IND"]


def test_medication_request_to_prescribing(medication_request_r4):
    expected = load_expected("medication_request_r4.json")["PRESCRIBING"]
    result = mapper.map_medication_request_to_prescribing(medication_request_r4)

    assert result["PRESCRIBINGID"] == expected["PRESCRIBINGID"]
    assert result["PATID"] == expected["PATID"]
    assert result["ENCOUNTERID"] == expected["ENCOUNTERID"]
    assert result["RXNORM_CUI"] == expected["RXNORM_CUI"]
    assert result["RX_ORDER_DATE"] == expected["RX_ORDER_DATE"]
    assert result["RX_DAYS_SUPPLY"] == expected["RX_DAYS_SUPPLY"]
    assert result["RX_REFILLS"] == expected["RX_REFILLS"]
    assert result["RX_QUANTITY"] == expected["RX_QUANTITY"]


def test_medication_dispense_to_dispensing(medication_dispense_r4):
    expected = load_expected("medication_dispense_r4.json")["DISPENSING"]
    result = mapper.map_medication_dispense_to_dispensing(medication_dispense_r4)

    assert result["DISPENSINGID"] == expected["DISPENSINGID"]
    assert result["PATID"] == expected["PATID"]
    assert result["PRESCRIBINGID"] == expected["PRESCRIBINGID"]
    assert result["NDC"] == expected["NDC"]
    assert result["DISPENSE_DATE"] == expected["DISPENSE_DATE"]
    assert result["DISPENSE_AMT"] == expected["DISPENSE_AMT"]
    assert result["DISPENSE_SUP"] == expected["DISPENSE_SUP"]


def test_immunization_to_immunization(immunization_r4):
    expected = load_expected("immunization_r4.json")["IMMUNIZATION"]
    result = mapper.map_immunization_to_immunization(immunization_r4)

    assert result["IMMUNIZATIONID"] == expected["IMMUNIZATIONID"]
    assert result["PATID"] == expected["PATID"]
    assert result["ENCOUNTERID"] == expected["ENCOUNTERID"]
    assert result["VX_CODE"] == expected["VX_CODE"]
    assert result["VX_CODE_TYPE"] == expected["VX_CODE_TYPE"]
    assert result["VX_ADMIN_DATE"] == expected["VX_ADMIN_DATE"]
    assert result["VX_STATUS"] == expected["VX_STATUS"]
    assert result["VX_DOSE_NUM"] == expected["VX_DOSE_NUM"]


def test_practitioner_to_provider():
    resource = {
        "resourceType": "Practitioner",
        "id": "prov-001",
        "gender": "male",
        "identifier": [
            {
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": "1234567890",
            }
        ],
    }
    result = mapper.map_practitioner_to_provider(resource)
    assert result["PROVIDERID"] == "prov-001"
    assert result["PROVIDER_SEX"] == "M"
    assert result["PROVIDER_NPI"] == "1234567890"
