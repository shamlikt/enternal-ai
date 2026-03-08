"""Pydantic v2 schemas for PCORnet CDM v7.0 validation."""
from typing import Optional

from pydantic import BaseModel, Field


class DemographicSchema(BaseModel):
    PATID: str = Field(..., max_length=50)
    BIRTH_DATE: Optional[str] = Field(None, max_length=10)
    BIRTH_TIME: Optional[str] = Field(None, max_length=5)
    SEX: Optional[str] = Field(None, max_length=2)
    SEXUAL_ORIENTATION: Optional[str] = Field(None, max_length=2)
    GENDER_IDENTITY: Optional[str] = Field(None, max_length=2)
    HISPANIC: Optional[str] = Field(None, max_length=2)
    RACE: Optional[str] = Field(None, max_length=2)
    BIOBANK_FLAG: Optional[str] = Field(None, max_length=1)
    PAT_PREF_LANGUAGE_SPOKEN: Optional[str] = Field(None, max_length=3)
    RAW_SEX: Optional[str] = Field(None, max_length=50)
    RAW_SEXUAL_ORIENTATION: Optional[str] = Field(None, max_length=50)
    RAW_GENDER_IDENTITY: Optional[str] = Field(None, max_length=50)
    RAW_HISPANIC: Optional[str] = Field(None, max_length=50)
    RAW_RACE: Optional[str] = Field(None, max_length=50)
    RAW_PAT_PREF_LANGUAGE_SPOKEN: Optional[str] = Field(None, max_length=50)

    model_config = {"from_attributes": True}


class EncounterSchema(BaseModel):
    ENCOUNTERID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ADMIT_DATE: Optional[str] = Field(None, max_length=10)
    ADMIT_TIME: Optional[str] = Field(None, max_length=5)
    DISCHARGE_DATE: Optional[str] = Field(None, max_length=10)
    DISCHARGE_TIME: Optional[str] = Field(None, max_length=5)
    PROVIDERID: Optional[str] = Field(None, max_length=50)
    FACILITY_LOCATION: Optional[str] = Field(None, max_length=3)
    ENC_TYPE: Optional[str] = Field(None, max_length=2)
    FACILITYID: Optional[str] = Field(None, max_length=50)
    DISCHARGE_DISPOSITION: Optional[str] = Field(None, max_length=2)
    DISCHARGE_STATUS: Optional[str] = Field(None, max_length=2)
    DRG: Optional[str] = Field(None, max_length=3)
    DRG_TYPE: Optional[str] = Field(None, max_length=2)
    ADMITTING_SOURCE: Optional[str] = Field(None, max_length=2)
    PAYER_TYPE_PRIMARY: Optional[str] = Field(None, max_length=3)
    PAYER_TYPE_SECONDARY: Optional[str] = Field(None, max_length=3)
    FACILITY_TYPE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class DiagnosisSchema(BaseModel):
    DIAGNOSISID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    ENC_TYPE: Optional[str] = Field(None, max_length=2)
    ADMIT_DATE: Optional[str] = Field(None, max_length=10)
    PROVIDERID: Optional[str] = Field(None, max_length=50)
    DX: Optional[str] = Field(None, max_length=18)
    DX_TYPE: Optional[str] = Field(None, max_length=2)
    DX_SOURCE: Optional[str] = Field(None, max_length=2)
    DX_ORIGIN: Optional[str] = Field(None, max_length=2)
    PDX: Optional[str] = Field(None, max_length=2)
    DX_POA: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class ProceduresSchema(BaseModel):
    PROCEDURESID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    ENC_TYPE: Optional[str] = Field(None, max_length=2)
    ADMIT_DATE: Optional[str] = Field(None, max_length=10)
    PROVIDERID: Optional[str] = Field(None, max_length=50)
    PX_DATE: Optional[str] = Field(None, max_length=10)
    PX: Optional[str] = Field(None, max_length=11)
    PX_TYPE: Optional[str] = Field(None, max_length=2)
    PX_SOURCE: Optional[str] = Field(None, max_length=2)
    PPX: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class VitalSchema(BaseModel):
    VITALID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    MEASURE_DATE: Optional[str] = Field(None, max_length=10)
    MEASURE_TIME: Optional[str] = Field(None, max_length=5)
    VITAL_SOURCE: Optional[str] = Field(None, max_length=2)
    HT: Optional[float] = None
    WT: Optional[float] = None
    DIASTOLIC: Optional[float] = None
    SYSTOLIC: Optional[float] = None
    ORIGINAL_BMI: Optional[float] = None
    BP_POSITION: Optional[str] = Field(None, max_length=2)
    SMOKING: Optional[str] = Field(None, max_length=2)
    TOBACCO: Optional[str] = Field(None, max_length=2)
    TOBACCO_TYPE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class LabResultCmSchema(BaseModel):
    LAB_RESULT_CM_ID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    LAB_LOINC: Optional[str] = Field(None, max_length=10)
    LAB_RESULT_SOURCE: Optional[str] = Field(None, max_length=2)
    SPECIMEN_DATE: Optional[str] = Field(None, max_length=10)
    RESULT_DATE: Optional[str] = Field(None, max_length=10)
    RESULT_QUAL: Optional[str] = Field(None, max_length=2)
    RESULT_NUM: Optional[float] = None
    RESULT_MODIFIER: Optional[str] = Field(None, max_length=2)
    RESULT_UNIT: Optional[str] = Field(None, max_length=11)
    NORM_RANGE_LOW: Optional[str] = Field(None, max_length=10)
    NORM_RANGE_HIGH: Optional[str] = Field(None, max_length=10)
    ABN_IND: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class PrescribingSchema(BaseModel):
    PRESCRIBINGID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    RX_ORDER_DATE: Optional[str] = Field(None, max_length=10)
    RXNORM_CUI: Optional[str] = Field(None, max_length=8)
    RX_QUANTITY: Optional[float] = None
    RX_DAYS_SUPPLY: Optional[int] = None
    RX_REFILLS: Optional[int] = None
    RX_ROUTE: Optional[str] = Field(None, max_length=2)
    RX_FREQUENCY: Optional[str] = Field(None, max_length=2)
    RX_SOURCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class DispensingSchema(BaseModel):
    DISPENSINGID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    PRESCRIBINGID: Optional[str] = Field(None, max_length=50)
    DISPENSE_DATE: Optional[str] = Field(None, max_length=10)
    NDC: Optional[str] = Field(None, max_length=11)
    DISPENSE_SUP: Optional[int] = None
    DISPENSE_AMT: Optional[float] = None

    model_config = {"from_attributes": True}


class ConditionSchema(BaseModel):
    CONDITIONID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    REPORT_DATE: Optional[str] = Field(None, max_length=10)
    RESOLVE_DATE: Optional[str] = Field(None, max_length=10)
    ONSET_DATE: Optional[str] = Field(None, max_length=10)
    CONDITION_STATUS: Optional[str] = Field(None, max_length=2)
    CONDITION: Optional[str] = Field(None, max_length=18)
    CONDITION_TYPE: Optional[str] = Field(None, max_length=2)
    CONDITION_SOURCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class DeathSchema(BaseModel):
    PATID: str = Field(..., max_length=50)
    DEATH_DATE: Optional[str] = Field(None, max_length=10)
    DEATH_DATE_IMPUTE: Optional[str] = Field(None, max_length=2)
    DEATH_SOURCE: Optional[str] = Field(None, max_length=2)
    DEATH_MATCH_CONFIDENCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class DeathCauseSchema(BaseModel):
    PATID: str = Field(..., max_length=50)
    DEATH_CAUSE: str = Field(..., max_length=8)
    DEATH_CAUSE_CODE: str = Field(..., max_length=2)
    DEATH_CAUSE_TYPE: str = Field(..., max_length=2)
    DEATH_CAUSE_SOURCE: str = Field(..., max_length=2)
    DEATH_CAUSE_CONFIDENCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class EnrollmentSchema(BaseModel):
    PATID: str = Field(..., max_length=50)
    ENR_START_DATE: str = Field(..., max_length=10)
    ENR_BASIS: str = Field(..., max_length=1)
    ENR_END_DATE: Optional[str] = Field(None, max_length=10)
    CHART: Optional[str] = Field(None, max_length=1)

    model_config = {"from_attributes": True}


class HarvestSchema(BaseModel):
    NETWORKID: str = Field(..., max_length=10)
    NETWORK_NAME: Optional[str] = Field(None, max_length=20)
    DATAMARTID: Optional[str] = Field(None, max_length=10)
    DATAMART_NAME: Optional[str] = Field(None, max_length=20)
    CDM_VERSION: Optional[str] = Field(None, max_length=6)

    model_config = {"from_attributes": True}


class LdsAddressHistorySchema(BaseModel):
    ADDRESSID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ADDRESS_CITY: Optional[str] = Field(None, max_length=50)
    ADDRESS_STATE: Optional[str] = Field(None, max_length=2)
    ADDRESS_ZIP5: Optional[str] = Field(None, max_length=5)
    ADDRESS_ZIP9: Optional[str] = Field(None, max_length=9)
    ADDRESS_COUNTY: Optional[str] = Field(None, max_length=3)
    ADDRESS_PERIOD_START: Optional[str] = Field(None, max_length=10)
    ADDRESS_PERIOD_END: Optional[str] = Field(None, max_length=10)

    model_config = {"from_attributes": True}


class MedAdminSchema(BaseModel):
    MEDADMINID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    MEDADMIN_START_DATE: Optional[str] = Field(None, max_length=10)
    MEDADMIN_TYPE: Optional[str] = Field(None, max_length=2)
    MEDADMIN_CODE: Optional[str] = Field(None, max_length=11)
    MEDADMIN_DOSE_ADMIN: Optional[float] = None
    MEDADMIN_DOSE_ADMIN_UNIT: Optional[str] = Field(None, max_length=50)
    MEDADMIN_ROUTE: Optional[str] = Field(None, max_length=2)
    MEDADMIN_SOURCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class ObsClinSchema(BaseModel):
    OBSCLINID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    OBSCLIN_DATE: Optional[str] = Field(None, max_length=10)
    OBSCLIN_TYPE: Optional[str] = Field(None, max_length=2)
    OBSCLIN_CODE: Optional[str] = Field(None, max_length=18)
    OBSCLIN_RESULT_TEXT: Optional[str] = None
    OBSCLIN_RESULT_NUM: Optional[float] = None
    OBSCLIN_RESULT_UNIT: Optional[str] = Field(None, max_length=11)
    OBSCLIN_SOURCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class ObsGenSchema(BaseModel):
    OBSGENID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    OBSGEN_DATE: Optional[str] = Field(None, max_length=10)
    OBSGEN_TYPE: Optional[str] = Field(None, max_length=2)
    OBSGEN_CODE: Optional[str] = Field(None, max_length=18)
    OBSGEN_RESULT_TEXT: Optional[str] = None
    OBSGEN_RESULT_NUM: Optional[float] = None
    OBSGEN_RESULT_UNIT: Optional[str] = Field(None, max_length=11)
    OBSGEN_SOURCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class PcornetTrialSchema(BaseModel):
    PATID: str = Field(..., max_length=50)
    TRIALID: str = Field(..., max_length=20)
    PARTICIPANTID: Optional[str] = Field(None, max_length=50)
    TRIAL_SITEID: Optional[str] = Field(None, max_length=50)
    TRIAL_ENROLL_DATE: Optional[str] = Field(None, max_length=10)
    TRIAL_END_DATE: Optional[str] = Field(None, max_length=10)

    model_config = {"from_attributes": True}


class ProCmSchema(BaseModel):
    PRO_CM_ID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    PRO_DATE: Optional[str] = Field(None, max_length=10)
    PRO_ITEM_LOINC: Optional[str] = Field(None, max_length=10)
    PRO_RESPONSE_TEXT: Optional[str] = None
    PRO_RESPONSE_NUM: Optional[float] = None
    PRO_SOURCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class ProviderSchema(BaseModel):
    PROVIDERID: str = Field(..., max_length=50)
    PROVIDER_SEX: Optional[str] = Field(None, max_length=2)
    PROVIDER_SPECIALTY_PRIMARY: Optional[str] = Field(None, max_length=3)
    PROVIDER_NPI: Optional[str] = Field(None, max_length=10)

    model_config = {"from_attributes": True}


class ImmunizationSchema(BaseModel):
    IMMUNIZATIONID: str = Field(..., max_length=50)
    PATID: str = Field(..., max_length=50)
    ENCOUNTERID: Optional[str] = Field(None, max_length=50)
    VX_ADMIN_DATE: Optional[str] = Field(None, max_length=10)
    VX_CODE_TYPE: Optional[str] = Field(None, max_length=2)
    VX_CODE: Optional[str] = Field(None, max_length=30)
    VX_STATUS: Optional[str] = Field(None, max_length=2)
    VX_SOURCE: Optional[str] = Field(None, max_length=2)

    model_config = {"from_attributes": True}


class HashTokenSchema(BaseModel):
    PATID: str = Field(..., max_length=50)
    TOKEN_ENCRYPTION_KEY: Optional[str] = Field(None, max_length=50)
    HASHED_ID: Optional[str] = Field(None, max_length=256)

    model_config = {"from_attributes": True}
