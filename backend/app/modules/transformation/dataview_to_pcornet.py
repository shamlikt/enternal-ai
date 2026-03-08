"""athenahealth DataView to PCORnet CDM v7.0 mapper.

Maps athenahealth DataView Snowflake table rows to PCORnet CDM tables.
The DataView schema follows athenahealth's standard column naming conventions.
"""
from typing import Any


def _extract_date(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value)
    if len(s) >= 10:
        return s[:10]
    return s


def _coerce_str(value: Any, max_len: int | None = None) -> str | None:
    if value is None:
        return None
    s = str(value)
    if max_len:
        return s[:max_len]
    return s


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# DataView table name prefix → handler function
_TABLE_HANDLERS: dict[str, str] = {
    "PATIENT": "map_patient",
    "APPOINTMENT": "map_appointment",
    "ENCOUNTER": "map_encounter",
    "PROBLEM": "map_problem",
    "ORDER": "map_order",
    "MEDICATION": "map_medication",
    "LAB": "map_lab",
    "VITAL": "map_vital",
    "IMMUNIZATION": "map_immunization",
}


def map_row(table_name: str, row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Route a DataView row to the appropriate PCORnet CDM mapper.

    Returns:
        (cdm_table_name, mapped_dict) — e.g. ("DEMOGRAPHIC", {...})

    Raises:
        ValueError: if table_name is not recognized.
    """
    table_upper = table_name.upper()

    for prefix, handler_name in _TABLE_HANDLERS.items():
        if table_upper.startswith(prefix):
            handler = globals().get(handler_name)
            if handler:
                return handler(row)

    raise ValueError(f"No DataView mapper for table: {table_name}")


def map_patient(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID") or row.get("ID"), 50)
    if not patid:
        raise ValueError("Patient row missing PATIENTID")

    sex_raw = _coerce_str(row.get("SEX") or row.get("GENDER"))
    sex_map = {"male": "M", "female": "F", "m": "M", "f": "F"}
    sex_code = sex_map.get((sex_raw or "").lower(), "UN")

    return "DEMOGRAPHIC", {
        "PATID": patid,
        "BIRTH_DATE": _extract_date(row.get("DATEOFBIRTH") or row.get("DOB") or row.get("BIRTH_DATE")),
        "SEX": sex_code,
        "RAW_SEX": sex_raw,
        "RACE": _coerce_str(row.get("RACE"), 2),
        "HISPANIC": _coerce_str(row.get("ETHNICITYCODE") or row.get("ETHNICITY"), 2),
        "PAT_PREF_LANGUAGE_SPOKEN": _coerce_str(row.get("PREFERREDLANGUAGE") or row.get("LANGUAGE"), 3),
        "RAW_RACE": _coerce_str(row.get("RACE"), 50),
        "RAW_HISPANIC": _coerce_str(row.get("ETHNICITYCODE") or row.get("ETHNICITY"), 50),
    }


def map_encounter(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    enc_id = _coerce_str(row.get("ENCOUNTERID") or row.get("ENCOUNTER_ID") or row.get("APPOINTMENTID"), 50)
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID"), 50)
    if not enc_id or not patid:
        raise ValueError("Encounter row missing ENCOUNTERID or PATIENTID")

    enc_type_raw = _coerce_str(row.get("ENCOUNTERTYPE") or row.get("APPOINTMENTTYPE"))
    enc_type_map = {
        "office visit": "AV",
        "telehealth": "TH",
        "emergency": "ED",
        "inpatient": "IP",
        "hospital": "IP",
    }
    enc_type = "OT"
    for key, val in enc_type_map.items():
        if key in (enc_type_raw or "").lower():
            enc_type = val
            break

    return "ENCOUNTER", {
        "ENCOUNTERID": enc_id,
        "PATID": patid,
        "ADMIT_DATE": _extract_date(row.get("ADMITDATE") or row.get("APPOINTMENTDATE") or row.get("SERVICEDATE")),
        "DISCHARGE_DATE": _extract_date(row.get("DISCHARGEDATE")),
        "ENC_TYPE": enc_type,
        "RAW_ENC_TYPE": enc_type_raw,
        "PROVIDERID": _coerce_str(row.get("PROVIDERID") or row.get("PROVIDER_ID") or row.get("PHYSICIANID"), 50),
        "FACILITYID": _coerce_str(row.get("DEPARTMENTID") or row.get("FACILITYID"), 50),
    }


def map_appointment(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    # Appointments map to ENCOUNTER
    return map_encounter(row)


def map_problem(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    problem_id = _coerce_str(row.get("PROBLEMID") or row.get("PROBLEM_ID"), 50)
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID"), 50)
    if not problem_id or not patid:
        raise ValueError("Problem row missing PROBLEMID or PATIENTID")

    dx_code = _coerce_str(row.get("ICDCODE") or row.get("ICD10CODE") or row.get("ICD9CODE"), 18)
    dx_type = "10" if row.get("ICD10CODE") else ("09" if row.get("ICD9CODE") else "OT")

    status_raw = _coerce_str(row.get("STATUS") or row.get("PROBLEMSTATUS"))
    status_map = {"active": "AC", "chronic": "AC", "resolved": "RS", "inactive": "IN"}
    condition_status = status_map.get((status_raw or "").lower(), "UN")

    return "CONDITION", {
        "CONDITIONID": problem_id,
        "PATID": patid,
        "ENCOUNTERID": _coerce_str(row.get("ENCOUNTERID"), 50),
        "CONDITION": dx_code,
        "CONDITION_TYPE": dx_type,
        "CONDITION_STATUS": condition_status,
        "CONDITION_SOURCE": "PR",
        "ONSET_DATE": _extract_date(row.get("ONSETDATE") or row.get("STARTDATE")),
        "RESOLVE_DATE": _extract_date(row.get("RESOLVEDDATE") or row.get("ENDDATE")),
        "RAW_CONDITION_STATUS": status_raw,
        "RAW_CONDITION": dx_code,
    }


def map_order(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    order_id = _coerce_str(row.get("ORDERID") or row.get("ORDER_ID"), 50)
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID"), 50)
    if not order_id or not patid:
        raise ValueError("Order row missing ORDERID or PATIENTID")

    px_code = _coerce_str(row.get("CPTCODE") or row.get("PROCEDURECODE"), 11)
    px_type = "CH" if row.get("CPTCODE") else "OT"

    return "PROCEDURES", {
        "PROCEDURESID": order_id,
        "PATID": patid,
        "ENCOUNTERID": _coerce_str(row.get("ENCOUNTERID"), 50),
        "PX": px_code,
        "PX_TYPE": px_type,
        "RAW_PX": px_code,
        "RAW_PX_TYPE": _coerce_str(row.get("CODETYPE"), 50),
        "PX_DATE": _extract_date(row.get("ORDERDATE") or row.get("SERVICEDATE")),
        "PX_SOURCE": "OD",
        "PROVIDERID": _coerce_str(row.get("PROVIDERID"), 50),
    }


def map_medication(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    med_id = _coerce_str(row.get("MEDICATIONID") or row.get("MEDICATION_ID"), 50)
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID"), 50)
    if not med_id or not patid:
        raise ValueError("Medication row missing MEDICATIONID or PATIENTID")

    ndc = _coerce_str(row.get("NDC") or row.get("NDCCODE"), 11)
    rxnorm = _coerce_str(row.get("RXNORM") or row.get("RXNORMCODE"), 8)

    if ndc:
        return "DISPENSING", {
            "DISPENSINGID": med_id,
            "PATID": patid,
            "NDC": ndc,
            "RAW_NDC": ndc,
            "DISPENSE_DATE": _extract_date(row.get("FILLEDDATE") or row.get("DISPENSEDATE")),
            "DISPENSE_AMT": _coerce_float(row.get("DISPENSEDQUANTITY") or row.get("QUANTITY")),
            "DISPENSE_SUP": _coerce_int(row.get("DAYSSUPPLY") or row.get("DAYS_SUPPLY")),
            "DISPENSE_SOURCE": "PH",
        }
    else:
        return "PRESCRIBING", {
            "PRESCRIBINGID": med_id,
            "PATID": patid,
            "ENCOUNTERID": _coerce_str(row.get("ENCOUNTERID"), 50),
            "RXNORM_CUI": rxnorm,
            "RAW_RX_MED_NAME": _coerce_str(row.get("MEDICATIONNAME") or row.get("DRUGNAME"), 100),
            "RAW_RXNORM_CUI": rxnorm,
            "RX_ORDER_DATE": _extract_date(row.get("ORDEREDDATE") or row.get("PRESCRIBEDDATE")),
            "RX_DAYS_SUPPLY": _coerce_int(row.get("DAYSSUPPLY")),
            "RX_REFILLS": _coerce_int(row.get("REFILLS")),
            "RX_QUANTITY": _coerce_float(row.get("QUANTITY")),
            "RX_SOURCE": "OD",
            "RX_PROVIDERID": _coerce_str(row.get("PROVIDERID"), 50),
        }


def map_lab(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    lab_id = _coerce_str(row.get("LABRESULTID") or row.get("LAB_ID") or row.get("ORDERID"), 50)
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID"), 50)
    if not lab_id or not patid:
        raise ValueError("Lab row missing LABRESULTID or PATIENTID")

    result_num_raw = row.get("RESULTVALUE") or row.get("RESULT_VALUE")
    result_num = None
    result_qual = None
    try:
        result_num = float(result_num_raw)
    except (TypeError, ValueError):
        result_qual = _coerce_str(result_num_raw, 2)

    return "LAB_RESULT_CM", {
        "LAB_RESULT_CM_ID": lab_id,
        "PATID": patid,
        "ENCOUNTERID": _coerce_str(row.get("ENCOUNTERID"), 50),
        "LAB_LOINC": _coerce_str(row.get("LOINCCODE") or row.get("LOINC"), 10),
        "LAB_RESULT_SOURCE": "LR",
        "SPECIMEN_DATE": _extract_date(row.get("SPECIMENDATE") or row.get("COLLECTIONDATE")),
        "RESULT_DATE": _extract_date(row.get("RESULTDATE") or row.get("REPORTEDDATE")),
        "RESULT_NUM": result_num,
        "RESULT_QUAL": result_qual,
        "RESULT_UNIT": _coerce_str(row.get("RESULTUNIT") or row.get("UNITS"), 11),
        "RAW_LAB_NAME": _coerce_str(row.get("TESTNAME") or row.get("LABNAME"), 100),
        "RAW_LAB_CODE": _coerce_str(row.get("LOINCCODE") or row.get("TESTCODE"), 50),
        "RAW_RESULT": _coerce_str(result_num_raw, 50),
    }


def map_vital(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    vital_id = _coerce_str(row.get("VITALID") or row.get("VITAL_ID"), 50)
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID"), 50)
    if not vital_id or not patid:
        raise ValueError("Vital row missing VITALID or PATIENTID")

    return "VITAL", {
        "VITALID": vital_id,
        "PATID": patid,
        "ENCOUNTERID": _coerce_str(row.get("ENCOUNTERID"), 50),
        "MEASURE_DATE": _extract_date(row.get("VITALDATE") or row.get("MEASUREDATE")),
        "HT": _coerce_float(row.get("HEIGHT") or row.get("HT")),
        "WT": _coerce_float(row.get("WEIGHT") or row.get("WT")),
        "SYSTOLIC": _coerce_float(row.get("SYSTOLICBP") or row.get("SYSTOLIC")),
        "DIASTOLIC": _coerce_float(row.get("DIASTOLICBP") or row.get("DIASTOLIC")),
        "ORIGINAL_BMI": _coerce_float(row.get("BMI")),
        "VITAL_SOURCE": "PR",
    }


def map_immunization(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    imm_id = _coerce_str(row.get("IMMUNIZATIONID") or row.get("IMMUNIZATION_ID"), 50)
    patid = _coerce_str(row.get("PATIENTID") or row.get("PATIENT_ID"), 50)
    if not imm_id or not patid:
        raise ValueError("Immunization row missing IMMUNIZATIONID or PATIENTID")

    return "IMMUNIZATION", {
        "IMMUNIZATIONID": imm_id,
        "PATID": patid,
        "ENCOUNTERID": _coerce_str(row.get("ENCOUNTERID"), 50),
        "VX_CODE": _coerce_str(row.get("CVXCODE") or row.get("VACCINECODE"), 30),
        "VX_CODE_TYPE": "CV" if row.get("CVXCODE") else "OT",
        "RAW_VX_CODE": _coerce_str(row.get("CVXCODE") or row.get("VACCINECODE"), 50),
        "VX_ADMIN_DATE": _extract_date(row.get("ADMINDATE") or row.get("VACCINATIONDATE")),
        "VX_STATUS": "CP",
        "VX_SOURCE": "RG",
        "VX_MANUFACTURER": _coerce_str(row.get("MANUFACTURER"), 10),
        "VX_LOT_NUM": _coerce_str(row.get("LOTNUMBER") or row.get("LOTNUM"), 50),
    }
