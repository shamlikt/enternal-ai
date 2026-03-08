"""FHIR R4/R5 resource to PCORnet CDM v7.0 mapper functions.

Based on HL7 CDMH Implementation Guide for FHIR to PCORnet mapping.
All dates stored as YYYY-MM-DD strings per CDM spec.
"""
import uuid
from typing import Any


def _get_code(coding_list: list[dict], system: str | None = None) -> str | None:
    if not coding_list:
        return None
    for coding in coding_list:
        if system is None or coding.get("system") == system:
            return coding.get("code")
    return coding_list[0].get("code") if coding_list else None


def _extract_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    return date_str[:10] if len(date_str) >= 10 else date_str


def _map_sex(gender: str | None) -> str | None:
    mapping = {"male": "M", "female": "F", "other": "OT", "unknown": "UN"}
    return mapping.get((gender or "").lower())


def _map_race(extensions: list[dict]) -> str | None:
    for ext in extensions:
        if "ombCategory" in ext.get("url", "") or "race" in ext.get("url", "").lower():
            value_coding = ext.get("valueCoding", {})
            code = value_coding.get("code")
            race_map = {
                "1002-5": "01",  # American Indian/Alaska Native
                "2028-9": "02",  # Asian
                "2054-5": "03",  # Black/African American
                "2076-8": "04",  # Native Hawaiian/Pacific Islander
                "2106-3": "05",  # White
                "2131-1": "OT",  # Other Race
            }
            return race_map.get(code, "OT")
    return None


def _map_hispanic(extensions: list[dict]) -> str | None:
    for ext in extensions:
        if "ethnicity" in ext.get("url", "").lower():
            value_coding = ext.get("valueCoding", {})
            code = value_coding.get("code")
            if code == "2135-2":
                return "Y"
            if code == "2186-5":
                return "N"
    return None


def _map_encounter_type(class_code: str | None) -> str | None:
    mapping = {
        "AMB": "AV",  # Ambulatory Visit
        "EMER": "ED",  # Emergency Department
        "IMP": "IP",  # Inpatient Hospital Stay
        "ACUTE": "IP",
        "NONAC": "IS",  # Non-Acute Institutional Stay
        "SS": "OS",    # Other Ambulatory Visit
        "VR": "TH",    # Telehealth
    }
    return mapping.get((class_code or "").upper(), "OT")


def _map_dx_type(system: str | None) -> str | None:
    if not system:
        return None
    if "icd-10" in system.lower():
        return "10"
    if "icd-9" in system.lower():
        return "09"
    if "snomed" in system.lower():
        return "SM"
    return "OT"


def _map_px_type(system: str | None) -> str | None:
    if not system:
        return None
    if "cpt" in system.lower() or "hcpcs" in system.lower():
        return "CH"
    if "icd-10" in system.lower() and "procedure" in system.lower():
        return "10"
    if "icd-9" in system.lower() and "procedure" in system.lower():
        return "09"
    if "snomed" in system.lower():
        return "OT"
    return "OT"


def map_patient_to_demographic(resource: dict[str, Any]) -> dict[str, Any]:
    patient_id = resource.get("id", "")
    extensions = resource.get("extension", [])
    name_list = resource.get("name", [])
    language_list = resource.get("communication", [])

    preferred_language = None
    for comm in language_list:
        if comm.get("preferred"):
            lang = comm.get("language", {})
            codings = lang.get("coding", [])
            preferred_language = _get_code(codings)
            break

    return {
        "PATID": patient_id,
        "BIRTH_DATE": _extract_date(resource.get("birthDate")),
        "SEX": _map_sex(resource.get("gender")),
        "RAW_SEX": resource.get("gender"),
        "RACE": _map_race(extensions),
        "HISPANIC": _map_hispanic(extensions),
        "PAT_PREF_LANGUAGE_SPOKEN": preferred_language,
    }


def map_encounter_to_encounter(resource: dict[str, Any]) -> dict[str, Any]:
    encounter_id = resource.get("id", "")

    # Extract patient reference
    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    period = resource.get("period", {})
    admit_date = _extract_date(period.get("start"))
    discharge_date = _extract_date(period.get("end"))

    # class is FHIR R4; class is CodeableConcept in R5
    enc_class = resource.get("class", {})
    if isinstance(enc_class, dict):
        class_code = enc_class.get("code")
    elif isinstance(enc_class, list) and enc_class:
        class_code = enc_class[0].get("code")
    else:
        class_code = None

    provider_id = None
    for participant in resource.get("participant", []):
        individual = participant.get("individual", {})
        ref = individual.get("reference", "")
        if ref:
            provider_id = ref.split("/")[-1]
            break

    return {
        "ENCOUNTERID": encounter_id,
        "PATID": patid,
        "ADMIT_DATE": admit_date,
        "DISCHARGE_DATE": discharge_date,
        "ENC_TYPE": _map_encounter_type(class_code),
        "RAW_ENC_TYPE": class_code,
        "PROVIDERID": provider_id,
    }


def map_condition_to_diagnosis(resource: dict[str, Any]) -> dict[str, Any]:
    condition_id = resource.get("id", "")

    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    encounter = resource.get("encounter", {})
    enc_ref = encounter.get("reference", "")
    encounterid = enc_ref.split("/")[-1] if "/" in enc_ref else enc_ref or None

    code_obj = resource.get("code", {})
    codings = code_obj.get("coding", [])
    dx_code = _get_code(codings)
    dx_system = codings[0].get("system") if codings else None

    onset = resource.get("onsetDateTime") or resource.get("onsetPeriod", {}).get("start")

    return {
        "DIAGNOSISID": condition_id,
        "PATID": patid,
        "ENCOUNTERID": encounterid,
        "DX": dx_code,
        "DX_TYPE": _map_dx_type(dx_system),
        "RAW_DX": dx_code,
        "RAW_DX_TYPE": dx_system,
        "ADMIT_DATE": _extract_date(onset),
        "DX_SOURCE": "FH",
    }


def map_condition_to_condition(resource: dict[str, Any]) -> dict[str, Any]:
    condition_id = resource.get("id", "")

    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    encounter = resource.get("encounter", {})
    enc_ref = encounter.get("reference", "")
    encounterid = enc_ref.split("/")[-1] if "/" in enc_ref else enc_ref or None

    code_obj = resource.get("code", {})
    codings = code_obj.get("coding", [])
    condition_code = _get_code(codings)

    clinical_status = resource.get("clinicalStatus", {})
    cs_codings = clinical_status.get("coding", [])
    cs_code = _get_code(cs_codings)

    status_map = {"active": "AC", "relapse": "AC", "remission": "RS", "resolved": "RS", "inactive": "IN"}
    condition_status = status_map.get(cs_code or "", "UN")

    onset = resource.get("onsetDateTime") or resource.get("onsetPeriod", {}).get("start")
    abatement = resource.get("abatementDateTime") or resource.get("abatementPeriod", {}).get("end")

    return {
        "CONDITIONID": condition_id,
        "PATID": patid,
        "ENCOUNTERID": encounterid,
        "CONDITION": condition_code,
        "CONDITION_TYPE": "09" if condition_code and "." not in condition_code else "10",
        "CONDITION_STATUS": condition_status,
        "CONDITION_SOURCE": "FH",
        "ONSET_DATE": _extract_date(onset),
        "RESOLVE_DATE": _extract_date(abatement),
        "RAW_CONDITION_STATUS": cs_code,
        "RAW_CONDITION": condition_code,
    }


def map_procedure_to_procedures(resource: dict[str, Any]) -> dict[str, Any]:
    procedure_id = resource.get("id", "")

    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    encounter = resource.get("encounter", {})
    enc_ref = encounter.get("reference", "")
    encounterid = enc_ref.split("/")[-1] if "/" in enc_ref else enc_ref or None

    code_obj = resource.get("code", {})
    codings = code_obj.get("coding", [])
    px_code = _get_code(codings)
    px_system = codings[0].get("system") if codings else None

    px_date = _extract_date(
        resource.get("performedDateTime")
        or (resource.get("performedPeriod") or {}).get("start")
    )

    provider_id = None
    for performer in resource.get("performer", []):
        actor = performer.get("actor", {})
        ref = actor.get("reference", "")
        if ref:
            provider_id = ref.split("/")[-1]
            break

    return {
        "PROCEDURESID": procedure_id,
        "PATID": patid,
        "ENCOUNTERID": encounterid,
        "PX": px_code,
        "PX_TYPE": _map_px_type(px_system),
        "RAW_PX": px_code,
        "RAW_PX_TYPE": px_system,
        "PX_DATE": px_date,
        "PX_SOURCE": "FH",
        "PROVIDERID": provider_id,
    }


def map_observation_to_vital(resource: dict[str, Any]) -> dict[str, Any]:
    obs_id = resource.get("id", "")

    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    encounter = resource.get("encounter", {})
    enc_ref = encounter.get("reference", "")
    encounterid = enc_ref.split("/")[-1] if "/" in enc_ref else enc_ref or None

    measure_date = _extract_date(
        resource.get("effectiveDateTime")
        or (resource.get("effectivePeriod") or {}).get("start")
    )

    code_obj = resource.get("code", {})
    codings = code_obj.get("coding", [])
    loinc_code = _get_code(codings, "http://loinc.org")

    # Mapping LOINC codes to PCORnet vital fields
    loinc_to_field = {
        "8302-2": "HT",       # Body height
        "29463-7": "WT",      # Body weight
        "8480-6": "SYSTOLIC",
        "8462-4": "DIASTOLIC",
        "39156-5": "ORIGINAL_BMI",
    }
    vital_field = loinc_to_field.get(loinc_code or "")

    value_quantity = resource.get("valueQuantity", {})
    value = value_quantity.get("value")

    vital = {
        "VITALID": obs_id,
        "PATID": patid,
        "ENCOUNTERID": encounterid,
        "MEASURE_DATE": measure_date,
        "VITAL_SOURCE": "PR",
    }

    if vital_field and value is not None:
        vital[vital_field] = float(value)

    # Handle blood pressure components
    for component in resource.get("component", []):
        comp_code = component.get("code", {})
        comp_codings = comp_code.get("coding", [])
        comp_loinc = _get_code(comp_codings, "http://loinc.org")
        comp_value = component.get("valueQuantity", {}).get("value")
        if comp_loinc == "8480-6" and comp_value is not None:
            vital["SYSTOLIC"] = float(comp_value)
        elif comp_loinc == "8462-4" and comp_value is not None:
            vital["DIASTOLIC"] = float(comp_value)

    return vital


def map_observation_to_lab(resource: dict[str, Any]) -> dict[str, Any]:
    obs_id = resource.get("id", "")

    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    encounter = resource.get("encounter", {})
    enc_ref = encounter.get("reference", "")
    encounterid = enc_ref.split("/")[-1] if "/" in enc_ref else enc_ref or None

    code_obj = resource.get("code", {})
    codings = code_obj.get("coding", [])
    loinc_code = _get_code(codings, "http://loinc.org")

    effective = resource.get("effectiveDateTime") or (resource.get("effectivePeriod") or {}).get("start")
    issued = resource.get("issued")
    specimen = resource.get("specimen", {})

    value_quantity = resource.get("valueQuantity", {})
    result_num = value_quantity.get("value")
    result_unit = value_quantity.get("unit") or value_quantity.get("code")

    value_string = resource.get("valueString")
    value_codeable = resource.get("valueCodeableConcept", {})
    result_qual = _get_code(value_codeable.get("coding", [])) if value_codeable else None

    interp_list = resource.get("interpretation", [])
    abn_ind = None
    if interp_list:
        abn_code = _get_code(interp_list[0].get("coding", []))
        if abn_code in ("H", "HH", "HU"):
            abn_ind = "AH"
        elif abn_code in ("L", "LL", "LU"):
            abn_ind = "AL"
        elif abn_code == "N":
            abn_ind = "WL"

    return {
        "LAB_RESULT_CM_ID": obs_id,
        "PATID": patid,
        "ENCOUNTERID": encounterid,
        "LAB_LOINC": loinc_code,
        "LAB_RESULT_SOURCE": "LR",
        "SPECIMEN_DATE": _extract_date(effective),
        "RESULT_DATE": _extract_date(issued or effective),
        "RESULT_NUM": float(result_num) if result_num is not None else None,
        "RESULT_UNIT": result_unit,
        "RESULT_QUAL": result_qual,
        "RAW_LAB_NAME": code_obj.get("text"),
        "RAW_LAB_CODE": loinc_code,
        "RAW_RESULT": str(result_num) if result_num is not None else value_string,
        "ABN_IND": abn_ind,
    }


def map_medication_request_to_prescribing(resource: dict[str, Any]) -> dict[str, Any]:
    med_id = resource.get("id", "")

    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    encounter = resource.get("encounter", {})
    enc_ref = encounter.get("reference", "")
    encounterid = enc_ref.split("/")[-1] if "/" in enc_ref else enc_ref or None

    # Get medication code - RxNorm from medicationCodeableConcept
    med_code_obj = resource.get("medicationCodeableConcept", {})
    codings = med_code_obj.get("coding", [])
    rxnorm = _get_code(codings, "http://www.nlm.nih.gov/research/umls/rxnorm")
    if rxnorm is None:
        rxnorm = _get_code(codings)
    raw_med_name = med_code_obj.get("text")

    authored_on = resource.get("authoredOn")
    validity_period = resource.get("dispenseRequest", {}).get("validityPeriod", {})

    dosage_list = resource.get("dosageInstruction", [])
    rx_days = resource.get("dispenseRequest", {}).get("expectedSupplyDuration", {}).get("value")
    rx_refills = resource.get("dispenseRequest", {}).get("numberOfRepeatsAllowed")
    rx_quantity = resource.get("dispenseRequest", {}).get("quantity", {}).get("value")

    requester = resource.get("requester", {})
    provider_id = requester.get("reference", "").split("/")[-1] or None

    return {
        "PRESCRIBINGID": med_id,
        "PATID": patid,
        "ENCOUNTERID": encounterid,
        "RXNORM_CUI": rxnorm,
        "RAW_RX_MED_NAME": raw_med_name,
        "RAW_RXNORM_CUI": rxnorm,
        "RX_ORDER_DATE": _extract_date(authored_on),
        "RX_START_DATE": _extract_date(validity_period.get("start")),
        "RX_END_DATE": _extract_date(validity_period.get("end")),
        "RX_DAYS_SUPPLY": int(rx_days) if rx_days is not None else None,
        "RX_REFILLS": int(rx_refills) if rx_refills is not None else None,
        "RX_QUANTITY": float(rx_quantity) if rx_quantity is not None else None,
        "RX_SOURCE": "OD",
        "RX_PROVIDERID": provider_id,
    }


def map_medication_dispense_to_dispensing(resource: dict[str, Any]) -> dict[str, Any]:
    disp_id = resource.get("id", "")

    subject = resource.get("subject", {})
    pat_ref = subject.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    med_code_obj = resource.get("medicationCodeableConcept", {})
    codings = med_code_obj.get("coding", [])
    ndc = _get_code(codings, "http://hl7.org/fhir/sid/ndc")
    if ndc is None:
        ndc = _get_code(codings)

    when_handed_over = resource.get("whenHandedOver")
    quantity = resource.get("quantity", {}).get("value")
    days_supply = resource.get("daysSupply", {}).get("value")

    auth_prescription = resource.get("authorizingPrescription", [])
    prescribing_id = None
    if auth_prescription:
        ref = auth_prescription[0].get("reference", "")
        prescribing_id = ref.split("/")[-1] if "/" in ref else ref or None

    return {
        "DISPENSINGID": disp_id,
        "PATID": patid,
        "PRESCRIBINGID": prescribing_id,
        "NDC": ndc,
        "RAW_NDC": ndc,
        "DISPENSE_DATE": _extract_date(when_handed_over),
        "DISPENSE_AMT": float(quantity) if quantity is not None else None,
        "DISPENSE_SUP": int(days_supply) if days_supply is not None else None,
        "DISPENSE_SOURCE": "DP",
    }


def map_immunization_to_immunization(resource: dict[str, Any]) -> dict[str, Any]:
    imm_id = resource.get("id", "")

    patient = resource.get("patient", {})
    pat_ref = patient.get("reference", "")
    patid = pat_ref.split("/")[-1] if "/" in pat_ref else pat_ref

    encounter = resource.get("encounter", {})
    enc_ref = encounter.get("reference", "")
    encounterid = enc_ref.split("/")[-1] if "/" in enc_ref else enc_ref or None

    vaccine_code = resource.get("vaccineCode", {})
    codings = vaccine_code.get("coding", [])
    vx_code = _get_code(codings, "http://hl7.org/fhir/sid/cvx")
    vx_code_type = "CV" if vx_code else None
    if not vx_code:
        vx_code = _get_code(codings)
        vx_code_type = "OT"

    occurrence = resource.get("occurrenceDateTime")
    status = resource.get("status")
    status_map = {"completed": "CP", "not-done": "RF", "entered-in-error": "DE"}

    series = resource.get("protocolApplied", [])
    dose_num = None
    if series:
        dose_num = series[0].get("doseNumberPositiveInt") or series[0].get("doseNumberString")

    provider_id = None
    for performer in resource.get("performer", []):
        actor = performer.get("actor", {})
        ref = actor.get("reference", "")
        if ref and "Practitioner" in ref:
            provider_id = ref.split("/")[-1]
            break

    return {
        "IMMUNIZATIONID": imm_id,
        "PATID": patid,
        "ENCOUNTERID": encounterid,
        "VX_CODE": vx_code,
        "VX_CODE_TYPE": vx_code_type,
        "RAW_VX_CODE": vx_code,
        "RAW_VX_CODE_TYPE": vaccine_code.get("coding", [{}])[0].get("system") if vaccine_code.get("coding") else None,
        "VX_ADMIN_DATE": _extract_date(occurrence),
        "VX_STATUS": status_map.get(status or "", "UN"),
        "RAW_VX_STATUS": status,
        "VX_SOURCE": "RG",
        "VX_DOSE_NUM": float(dose_num) if dose_num is not None else None,
        "VX_PROVIDERID": provider_id,
    }


def map_practitioner_to_provider(resource: dict[str, Any]) -> dict[str, Any]:
    practitioner_id = resource.get("id", "")

    gender = resource.get("gender")
    sex_map = {"male": "M", "female": "F", "other": "OT", "unknown": "UN"}

    identifier_list = resource.get("identifier", [])
    npi = None
    for ident in identifier_list:
        if "npi" in (ident.get("system") or "").lower():
            npi = ident.get("value")
            break

    qualifications = resource.get("qualification", [])
    specialty = None
    for qual in qualifications:
        code = qual.get("code", {})
        codings = code.get("coding", [])
        if codings:
            specialty = codings[0].get("code")
            break

    return {
        "PROVIDERID": practitioner_id,
        "PROVIDER_SEX": sex_map.get((gender or "").lower()),
        "PROVIDER_NPI": npi,
        "PROVIDER_SPECIALTY_PRIMARY": specialty,
        "RAW_PROVIDER_SPECIALTY_PRIMARY": specialty,
    }


def map_patient_to_death(resource: dict[str, Any]) -> dict[str, Any] | None:
    if not resource.get("deceasedBoolean") and not resource.get("deceasedDateTime"):
        return None

    patient_id = resource.get("id", "")
    death_date = _extract_date(resource.get("deceasedDateTime"))

    return {
        "PATID": patient_id,
        "DEATH_DATE": death_date,
        "DEATH_DATE_IMPUTE": "M" if death_date and len(death_date) < 10 else None,
        "DEATH_SOURCE": "EH",
        "DEATH_MATCH_CONFIDENCE": "E",
    }
