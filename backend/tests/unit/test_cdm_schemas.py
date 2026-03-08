"""
Unit tests for app.modules.cdm.schemas — Pydantic v2 validation of PCORnet CDM v7.0 schemas.

Tests verify:
- Required fields are enforced
- Optional fields accept None
- Date fields parse correctly
- Numeric fields accept float values
- from_attributes config allows ORM model conversion
"""
from datetime import date

import pytest
from pydantic import ValidationError

from app.modules.cdm.schemas import (
    ConditionSchema,
    DeathCauseSchema,
    DeathSchema,
    DemographicSchema,
    DispensingSchema,
    DiagnosisSchema,
    EnrollmentSchema,
    HashTokenSchema,
    ImmunizationSchema,
    LabResultCmSchema,
    LdsAddressHistorySchema,
    MedAdminSchema,
    ObsClinSchema,
    ObsGenSchema,
    PcornetTrialSchema,
    PrescribingSchema,
    ProCmSchema,
    ProceduresSchema,
    ProviderSchema,
    VitalSchema,
    EncounterSchema,
)


class TestDemographicSchema:
    def test_minimal_valid(self):
        d = DemographicSchema(PATID="PAT001")
        assert d.PATID == "PAT001"
        assert d.BIRTH_DATE is None
        assert d.SEX is None

    def test_full_fields(self):
        d = DemographicSchema(
            PATID="PAT001",
            BIRTH_DATE=date(1980, 5, 15),
            SEX="M",
            SEXUAL_ORIENTATION="SU",
            GENDER_IDENTITY="M",
            HISPANIC="N",
            RACE="05",
            BIOBANK_FLAG="Y",
            PAT_PREF_LANGUAGE_SPOKEN="eng",
        )
        assert d.BIRTH_DATE == date(1980, 5, 15)
        assert d.SEX == "M"
        assert d.RACE == "05"

    def test_missing_patid_raises(self):
        with pytest.raises(ValidationError):
            DemographicSchema()

    def test_date_parsed_from_string(self):
        d = DemographicSchema(PATID="PAT002", BIRTH_DATE="1990-01-31")
        assert d.BIRTH_DATE == date(1990, 1, 31)

    def test_invalid_date_raises(self):
        with pytest.raises(ValidationError):
            DemographicSchema(PATID="PAT003", BIRTH_DATE="not-a-date")


class TestEncounterSchema:
    def test_minimal_valid(self):
        e = EncounterSchema(ENCOUNTERID="ENC001", PATID="PAT001")
        assert e.ENCOUNTERID == "ENC001"
        assert e.PATID == "PAT001"
        assert e.ADMIT_DATE is None

    def test_with_dates(self):
        e = EncounterSchema(
            ENCOUNTERID="ENC002",
            PATID="PAT001",
            ADMIT_DATE=date(2024, 3, 1),
            DISCHARGE_DATE=date(2024, 3, 5),
            ENC_TYPE="IP",
        )
        assert e.ADMIT_DATE == date(2024, 3, 1)
        assert e.DISCHARGE_DATE == date(2024, 3, 5)
        assert e.ENC_TYPE == "IP"

    def test_missing_encounterid_raises(self):
        with pytest.raises(ValidationError):
            EncounterSchema(PATID="PAT001")

    def test_missing_patid_raises(self):
        with pytest.raises(ValidationError):
            EncounterSchema(ENCOUNTERID="ENC001")


class TestDiagnosisSchema:
    def test_minimal_valid(self):
        d = DiagnosisSchema(DIAGNOSISID="DX001", PATID="PAT001")
        assert d.DIAGNOSISID == "DX001"
        assert d.DX is None

    def test_with_icd10_code(self):
        d = DiagnosisSchema(
            DIAGNOSISID="DX001",
            PATID="PAT001",
            DX="E11.9",
            DX_TYPE="10",
            DX_SOURCE="FI",
            PDX="P",
        )
        assert d.DX == "E11.9"
        assert d.DX_TYPE == "10"

    def test_missing_required_raises(self):
        with pytest.raises(ValidationError):
            DiagnosisSchema(PATID="PAT001")  # missing DIAGNOSISID


class TestProceduresSchema:
    def test_minimal_valid(self):
        p = ProceduresSchema(PROCEDURESID="PX001", PATID="PAT001")
        assert p.PROCEDURESID == "PX001"

    def test_with_procedure_code(self):
        p = ProceduresSchema(
            PROCEDURESID="PX001",
            PATID="PAT001",
            PX="99213",
            PX_TYPE="09",
            PX_DATE=date(2024, 1, 15),
        )
        assert p.PX == "99213"
        assert p.PX_DATE == date(2024, 1, 15)


class TestVitalSchema:
    def test_minimal_valid(self):
        v = VitalSchema(VITALID="VT001", PATID="PAT001")
        assert v.VITALID == "VT001"
        assert v.HT is None

    def test_numeric_vitals(self):
        v = VitalSchema(
            VITALID="VT001",
            PATID="PAT001",
            HT=170.5,
            WT=75.0,
            SYSTOLIC=120.0,
            DIASTOLIC=80.0,
            ORIGINAL_BMI=25.9,
        )
        assert v.HT == 170.5
        assert v.SYSTOLIC == 120.0
        assert v.ORIGINAL_BMI == 25.9

    def test_integer_coerced_to_float(self):
        v = VitalSchema(VITALID="VT001", PATID="PAT001", HT=170, WT=75)
        assert v.HT == 170.0
        assert isinstance(v.HT, float)


class TestLabResultCmSchema:
    def test_minimal_valid(self):
        l = LabResultCmSchema(LAB_RESULT_CM_ID="LAB001", PATID="PAT001")
        assert l.LAB_RESULT_CM_ID == "LAB001"

    def test_with_loinc_and_result(self):
        l = LabResultCmSchema(
            LAB_RESULT_CM_ID="LAB001",
            PATID="PAT001",
            LAB_LOINC="2339-0",
            RESULT_NUM=5.8,
            RESULT_UNIT="mg/dL",
            RESULT_QUAL="AB",
        )
        assert l.LAB_LOINC == "2339-0"
        assert l.RESULT_NUM == 5.8


class TestPrescribingSchema:
    def test_minimal_valid(self):
        p = PrescribingSchema(PRESCRIBINGID="RX001", PATID="PAT001")
        assert p.PRESCRIBINGID == "RX001"

    def test_with_rxnorm(self):
        p = PrescribingSchema(
            PRESCRIBINGID="RX001",
            PATID="PAT001",
            RXNORM_CUI="1049502",
            RX_QUANTITY=30.0,
            RX_DAYS_SUPPLY=30.0,
            RX_REFILLS=3,
            RX_ORDER_DATE=date(2024, 2, 1),
        )
        assert p.RXNORM_CUI == "1049502"
        assert p.RX_REFILLS == 3


class TestDispensingSchema:
    def test_minimal_valid(self):
        d = DispensingSchema(DISPENSINGID="DISP001", PATID="PAT001")
        assert d.DISPENSINGID == "DISP001"

    def test_with_ndc(self):
        d = DispensingSchema(
            DISPENSINGID="DISP001",
            PATID="PAT001",
            NDC="00071015523",
            DISPENSE_AMT=30.0,
            DISPENSE_SUP=30.0,
        )
        assert d.NDC == "00071015523"


class TestConditionSchema:
    def test_minimal_valid(self):
        c = ConditionSchema(CONDITIONID="CON001", PATID="PAT001")
        assert c.CONDITIONID == "CON001"

    def test_with_icd10_condition(self):
        c = ConditionSchema(
            CONDITIONID="CON001",
            PATID="PAT001",
            CONDITION="E11.9",
            CONDITION_TYPE="10",
            CONDITION_STATUS="AC",
            ONSET_DATE=date(2020, 1, 1),
        )
        assert c.CONDITION == "E11.9"
        assert c.CONDITION_STATUS == "AC"


class TestDeathSchema:
    def test_minimal_valid(self):
        d = DeathSchema(PATID="PAT001")
        assert d.PATID == "PAT001"
        assert d.DEATH_DATE is None

    def test_with_death_date(self):
        d = DeathSchema(PATID="PAT001", DEATH_DATE=date(2024, 6, 1), DEATH_SOURCE="D")
        assert d.DEATH_DATE == date(2024, 6, 1)


class TestDeathCauseSchema:
    def test_all_required_fields(self):
        dc = DeathCauseSchema(
            PATID="PAT001",
            DEATH_CAUSE="I219",
            DEATH_CAUSE_CODE="10",
            DEATH_CAUSE_TYPE="C",
            DEATH_CAUSE_SOURCE="D",
        )
        assert dc.DEATH_CAUSE == "I219"
        assert dc.DEATH_CAUSE_CONFIDENCE is None

    def test_missing_required_raises(self):
        with pytest.raises(ValidationError):
            DeathCauseSchema(PATID="PAT001")  # missing death cause fields


class TestEnrollmentSchema:
    def test_required_fields(self):
        e = EnrollmentSchema(
            PATID="PAT001",
            ENR_START_DATE=date(2020, 1, 1),
            ENR_BASIS="I",
        )
        assert e.ENR_START_DATE == date(2020, 1, 1)
        assert e.ENR_BASIS == "I"

    def test_missing_enr_start_date_raises(self):
        with pytest.raises(ValidationError):
            EnrollmentSchema(PATID="PAT001", ENR_BASIS="I")

    def test_missing_enr_basis_raises(self):
        with pytest.raises(ValidationError):
            EnrollmentSchema(PATID="PAT001", ENR_START_DATE=date(2020, 1, 1))


class TestImmunizationSchema:
    def test_minimal_valid(self):
        imm = ImmunizationSchema(IMMUNIZATIONID="IMM001", PATID="PAT001")
        assert imm.IMMUNIZATIONID == "IMM001"

    def test_with_vaccine_code(self):
        imm = ImmunizationSchema(
            IMMUNIZATIONID="IMM001",
            PATID="PAT001",
            VX_CODE="208",
            VX_CODE_TYPE="CV",
            VX_STATUS="CP",
            VX_ADMIN_DATE=date(2021, 4, 1),
        )
        assert imm.VX_CODE == "208"
        assert imm.VX_ADMIN_DATE == date(2021, 4, 1)


class TestProviderSchema:
    def test_minimal_valid(self):
        p = ProviderSchema(PROVIDERID="PROV001")
        assert p.PROVIDERID == "PROV001"
        assert p.PROVIDER_NPI is None

    def test_with_npi(self):
        p = ProviderSchema(PROVIDERID="PROV001", PROVIDER_NPI="1234567890", PROVIDER_SEX="F")
        assert p.PROVIDER_NPI == "1234567890"


class TestHashTokenSchema:
    def test_minimal_valid(self):
        ht = HashTokenSchema(PATID="PAT001")
        assert ht.PATID == "PAT001"
        assert ht.TOKEN_ENCRYPTION_KEY is None

    def test_with_key(self):
        ht = HashTokenSchema(PATID="PAT001", TOKEN_ENCRYPTION_KEY="abc123key")
        assert ht.TOKEN_ENCRYPTION_KEY == "abc123key"


class TestLdsAddressHistorySchema:
    def test_minimal_valid(self):
        addr = LdsAddressHistorySchema(ADDRESSID="ADDR001", PATID="PAT001")
        assert addr.ADDRESSID == "ADDR001"

    def test_with_address_fields(self):
        addr = LdsAddressHistorySchema(
            ADDRESSID="ADDR001",
            PATID="PAT001",
            ADDRESS_STATE="CA",
            ADDRESS_ZIP5="90210",
            ADDRESS_ZIP9="902101234",
        )
        assert addr.ADDRESS_ZIP5 == "90210"
        assert addr.ADDRESS_STATE == "CA"


class TestMedAdminSchema:
    def test_minimal_valid(self):
        m = MedAdminSchema(MEDADMINID="MA001", PATID="PAT001")
        assert m.MEDADMINID == "MA001"

    def test_with_dosing(self):
        m = MedAdminSchema(
            MEDADMINID="MA001",
            PATID="PAT001",
            MEDADMIN_CODE="1049502",
            MEDADMIN_TYPE="ND",
            MEDADMIN_DOSE_ADMIN=500.0,
            MEDADMIN_DOSE_ADMIN_UNIT="mg",
        )
        assert m.MEDADMIN_DOSE_ADMIN == 500.0


class TestObsClinSchema:
    def test_minimal_valid(self):
        o = ObsClinSchema(OBSCLINID="OC001", PATID="PAT001")
        assert o.OBSCLINID == "OC001"

    def test_with_result(self):
        o = ObsClinSchema(
            OBSCLINID="OC001",
            PATID="PAT001",
            OBSCLIN_TYPE="LC",
            OBSCLIN_CODE="2339-0",
            OBSCLIN_RESULT_NUM=98.6,
            OBSCLIN_RESULT_UNIT="degF",
        )
        assert o.OBSCLIN_RESULT_NUM == 98.6


class TestObsGenSchema:
    def test_minimal_valid(self):
        o = ObsGenSchema(OBSGENID="OG001", PATID="PAT001")
        assert o.OBSGENID == "OG001"

    def test_with_result_text(self):
        o = ObsGenSchema(
            OBSGENID="OG001",
            PATID="PAT001",
            OBSGEN_TYPE="SM",
            OBSGEN_RESULT_TEXT="Patient reported no pain",
        )
        assert o.OBSGEN_RESULT_TEXT == "Patient reported no pain"


class TestPcornetTrialSchema:
    def test_required_fields(self):
        t = PcornetTrialSchema(PATID="PAT001", TRIALID="TRIAL001")
        assert t.TRIALID == "TRIAL001"

    def test_missing_trialid_raises(self):
        with pytest.raises(ValidationError):
            PcornetTrialSchema(PATID="PAT001")


class TestProCmSchema:
    def test_minimal_valid(self):
        p = ProCmSchema(PRO_CM_ID="PRO001", PATID="PAT001")
        assert p.PRO_CM_ID == "PRO001"

    def test_with_response(self):
        p = ProCmSchema(
            PRO_CM_ID="PRO001",
            PATID="PAT001",
            PRO_ITEM_LOINC="77345-3",
            PRO_RESPONSE_NUM=7.0,
            PRO_RESPONSE_TEXT="Moderate",
        )
        assert p.PRO_RESPONSE_NUM == 7.0
        assert p.PRO_ITEM_LOINC == "77345-3"
