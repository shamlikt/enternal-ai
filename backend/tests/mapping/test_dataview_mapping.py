"""DataView to PCORnet CDM mapping tests."""
import pytest

from app.modules.transformation import dataview_to_pcornet as mapper


def test_patient_row_maps_to_demographic():
    row = {
        "PATIENTID": "dv-pat-001",
        "DATEOFBIRTH": "1975-06-22",
        "SEX": "Female",
        "RACE": "05",
        "ETHNICITYCODE": "N",
        "PREFERREDLANGUAGE": "en",
    }
    table, result = mapper.map_row("PATIENT", row)
    assert table == "DEMOGRAPHIC"
    assert result["PATID"] == "dv-pat-001"
    assert result["BIRTH_DATE"] == "1975-06-22"
    assert result["SEX"] == "F"


def test_encounter_row_maps_to_encounter():
    row = {
        "ENCOUNTERID": "dv-enc-001",
        "PATIENTID": "dv-pat-001",
        "ADMITDATE": "2024-03-10",
        "DISCHARGEDATE": "2024-03-12",
        "ENCOUNTERTYPE": "Hospital Inpatient",
        "PROVIDERID": "dv-prov-001",
    }
    table, result = mapper.map_row("ENCOUNTER", row)
    assert table == "ENCOUNTER"
    assert result["ENCOUNTERID"] == "dv-enc-001"
    assert result["PATID"] == "dv-pat-001"
    assert result["ENC_TYPE"] == "IP"


def test_appointment_row_maps_to_encounter():
    row = {
        "APPOINTMENTID": "dv-appt-001",
        "PATIENTID": "dv-pat-001",
        "APPOINTMENTDATE": "2024-04-01",
        "APPOINTMENTTYPE": "Office Visit",
    }
    table, result = mapper.map_row("APPOINTMENT", row)
    assert table == "ENCOUNTER"
    assert result["ENCOUNTERID"] == "dv-appt-001"


def test_problem_row_maps_to_condition():
    row = {
        "PROBLEMID": "dv-prob-001",
        "PATIENTID": "dv-pat-001",
        "ICD10CODE": "E11.9",
        "STATUS": "Active",
        "ONSETDATE": "2019-01-01",
    }
    table, result = mapper.map_row("PROBLEM", row)
    assert table == "CONDITION"
    assert result["CONDITIONID"] == "dv-prob-001"
    assert result["CONDITION"] == "E11.9"
    assert result["CONDITION_STATUS"] == "AC"


def test_medication_with_ndc_maps_to_dispensing():
    row = {
        "MEDICATIONID": "dv-med-001",
        "PATIENTID": "dv-pat-001",
        "NDC": "00093104801",  # 11-digit NDC without dashes
        "FILLEDDATE": "2024-06-01",
        "DISPENSEDQUANTITY": 60,
        "DAYSSUPPLY": 30,
    }
    table, result = mapper.map_row("MEDICATION", row)
    assert table == "DISPENSING"
    assert result["NDC"] == "00093104801"
    assert result["DISPENSE_SUP"] == 30


def test_medication_without_ndc_maps_to_prescribing():
    row = {
        "MEDICATIONID": "dv-rx-001",
        "PATIENTID": "dv-pat-001",
        "RXNORM": "860975",
        "MEDICATIONNAME": "Metformin",
        "ORDEREDDATE": "2024-06-15",
        "DAYSSUPPLY": 30,
    }
    table, result = mapper.map_row("MEDICATION", row)
    assert table == "PRESCRIBING"
    assert result["RXNORM_CUI"] == "860975"


def test_lab_row_maps_to_lab_result():
    row = {
        "LABRESULTID": "dv-lab-001",
        "PATIENTID": "dv-pat-001",
        "LOINCCODE": "4548-4",
        "RESULTVALUE": "7.2",
        "RESULTUNIT": "%",
        "SPECIMENDATE": "2024-05-01",
        "TESTNAME": "HbA1c",
    }
    table, result = mapper.map_row("LAB", row)
    assert table == "LAB_RESULT_CM"
    assert result["LAB_LOINC"] == "4548-4"
    assert result["RESULT_NUM"] == 7.2
    assert result["RESULT_UNIT"] == "%"


def test_lab_non_numeric_result_goes_to_qual():
    row = {
        "LABRESULTID": "dv-lab-002",
        "PATIENTID": "dv-pat-001",
        "LOINCCODE": "14988-8",
        "RESULTVALUE": "POSITIVE",
        "SPECIMENDATE": "2024-05-01",
    }
    table, result = mapper.map_row("LAB", row)
    assert table == "LAB_RESULT_CM"
    assert result["RESULT_NUM"] is None
    assert result["RESULT_QUAL"] == "PO"


def test_vital_row_maps_to_vital():
    row = {
        "VITALID": "dv-vital-001",
        "PATIENTID": "dv-pat-001",
        "HEIGHT": 170.5,
        "WEIGHT": 72.3,
        "SYSTOLICBP": 120,
        "DIASTOLICBP": 80,
        "BMI": 24.9,
        "VITALDATE": "2024-06-15",
    }
    table, result = mapper.map_row("VITAL", row)
    assert table == "VITAL"
    assert result["HT"] == 170.5
    assert result["WT"] == 72.3
    assert result["SYSTOLIC"] == 120.0
    assert result["DIASTOLIC"] == 80.0


def test_immunization_row_maps_to_immunization():
    row = {
        "IMMUNIZATIONID": "dv-imm-001",
        "PATIENTID": "dv-pat-001",
        "CVXCODE": "140",
        "ADMINDATE": "2024-01-15",
        "MANUFACTURER": "Sanofi",
    }
    table, result = mapper.map_row("IMMUNIZATION", row)
    assert table == "IMMUNIZATION"
    assert result["VX_CODE"] == "140"
    assert result["VX_CODE_TYPE"] == "CV"
    assert result["VX_ADMIN_DATE"] == "2024-01-15"


def test_unknown_table_raises_value_error():
    with pytest.raises(ValueError, match="No DataView mapper"):
        mapper.map_row("UNKNOWN_TABLE", {"id": "1"})


def test_patient_missing_id_raises_value_error():
    with pytest.raises(ValueError, match="missing PATIENTID"):
        mapper.map_row("PATIENT", {"SEX": "Male"})


def test_lab_missing_id_raises_value_error():
    with pytest.raises(ValueError, match="missing LABRESULTID"):
        mapper.map_row("LAB", {"PATIENTID": "pat-001"})
