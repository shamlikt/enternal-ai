from datetime import date
from typing import Optional

from pydantic import BaseModel


class DemographicSchema(BaseModel):
    PATID: str
    BIRTH_DATE: Optional[date] = None
    BIRTH_TIME: Optional[str] = None
    SEX: Optional[str] = None
    SEXUAL_ORIENTATION: Optional[str] = None
    GENDER_IDENTITY: Optional[str] = None
    HISPANIC: Optional[str] = None
    RACE: Optional[str] = None
    BIOBANK_FLAG: Optional[str] = None
    PAT_PREF_LANGUAGE_SPOKEN: Optional[str] = None
    RAW_SEX: Optional[str] = None
    RAW_SEXUAL_ORIENTATION: Optional[str] = None
    RAW_GENDER_IDENTITY: Optional[str] = None
    RAW_HISPANIC: Optional[str] = None
    RAW_RACE: Optional[str] = None
    RAW_PAT_PREF_LANGUAGE_SPOKEN: Optional[str] = None

    model_config = {"from_attributes": True}


class EncounterSchema(BaseModel):
    ENCOUNTERID: str
    PATID: str
    ADMIT_DATE: Optional[date] = None
    ADMIT_TIME: Optional[str] = None
    DISCHARGE_DATE: Optional[date] = None
    DISCHARGE_TIME: Optional[str] = None
    PROVIDERID: Optional[str] = None
    FACILITY_LOCATION: Optional[str] = None
    ENC_TYPE: Optional[str] = None
    FACILITYID: Optional[str] = None
    DISCHARGE_DISPOSITION: Optional[str] = None
    DISCHARGE_STATUS: Optional[str] = None
    DRG: Optional[str] = None
    DRG_TYPE: Optional[str] = None
    ADMITTING_SOURCE: Optional[str] = None
    PAYER_TYPE_PRIMARY: Optional[str] = None
    PAYER_TYPE_SECONDARY: Optional[str] = None
    FACILITY_TYPE: Optional[str] = None

    model_config = {"from_attributes": True}


class DiagnosisSchema(BaseModel):
    DIAGNOSISID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    ENC_TYPE: Optional[str] = None
    ADMIT_DATE: Optional[date] = None
    PROVIDERID: Optional[str] = None
    DX: Optional[str] = None
    DX_TYPE: Optional[str] = None
    DX_SOURCE: Optional[str] = None
    DX_ORIGIN: Optional[str] = None
    PDX: Optional[str] = None
    DX_POA: Optional[str] = None

    model_config = {"from_attributes": True}


class ProceduresSchema(BaseModel):
    PROCEDURESID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    ENC_TYPE: Optional[str] = None
    ADMIT_DATE: Optional[date] = None
    PROVIDERID: Optional[str] = None
    PX_DATE: Optional[date] = None
    PX: Optional[str] = None
    PX_TYPE: Optional[str] = None
    PX_SOURCE: Optional[str] = None
    PPX: Optional[str] = None

    model_config = {"from_attributes": True}


class VitalSchema(BaseModel):
    VITALID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    MEASURE_DATE: Optional[date] = None
    MEASURE_TIME: Optional[str] = None
    VITAL_SOURCE: Optional[str] = None
    HT: Optional[float] = None
    WT: Optional[float] = None
    DIASTOLIC: Optional[float] = None
    SYSTOLIC: Optional[float] = None
    ORIGINAL_BMI: Optional[float] = None
    BP_POSITION: Optional[str] = None
    SMOKING: Optional[str] = None
    TOBACCO: Optional[str] = None
    TOBACCO_TYPE: Optional[str] = None

    model_config = {"from_attributes": True}


class LabResultCmSchema(BaseModel):
    LAB_RESULT_CM_ID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    SPECIMEN_SOURCE: Optional[str] = None
    LAB_LOINC: Optional[str] = None
    LAB_RESULT_SOURCE: Optional[str] = None
    LAB_LOINC_SOURCE: Optional[str] = None
    PRIORITY: Optional[str] = None
    RESULT_LOC: Optional[str] = None
    LAB_PX: Optional[str] = None
    LAB_PX_TYPE: Optional[str] = None
    LAB_ORDER_DATE: Optional[date] = None
    SPECIMEN_DATE: Optional[date] = None
    SPECIMEN_TIME: Optional[str] = None
    RESULT_DATE: Optional[date] = None
    RESULT_TIME: Optional[str] = None
    RESULT_QUAL: Optional[str] = None
    RESULT_SNOMED: Optional[str] = None
    RESULT_NUM: Optional[float] = None
    RESULT_MODIFIER: Optional[str] = None
    RESULT_UNIT: Optional[str] = None
    NORM_RANGE_LOW: Optional[str] = None
    NORM_MODIFIER_LOW: Optional[str] = None
    NORM_RANGE_HIGH: Optional[str] = None
    NORM_MODIFIER_HIGH: Optional[str] = None
    ABN_IND: Optional[str] = None
    RAW_LAB_NAME: Optional[str] = None
    RAW_LAB_CODE: Optional[str] = None
    RAW_RESULT: Optional[str] = None
    RAW_UNIT: Optional[str] = None

    model_config = {"from_attributes": True}


class PrescribingSchema(BaseModel):
    PRESCRIBINGID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    RX_PROVIDERID: Optional[str] = None
    RX_ORDER_DATE: Optional[date] = None
    RX_ORDER_TIME: Optional[str] = None
    RX_START_DATE: Optional[date] = None
    RX_END_DATE: Optional[date] = None
    RX_QUANTITY: Optional[float] = None
    RX_QUANTITY_UNIT: Optional[str] = None
    RX_REFILLS: Optional[int] = None
    RX_DAYS_SUPPLY: Optional[float] = None
    RX_FREQUENCY: Optional[str] = None
    RX_PRN_FLAG: Optional[str] = None
    RX_ROUTE: Optional[str] = None
    RX_BASIS: Optional[str] = None
    RXNORM_CUI: Optional[str] = None
    RX_SOURCE: Optional[str] = None
    RX_DISPENSE_AS_WRITTEN: Optional[str] = None
    RAW_RX_MED_NAME: Optional[str] = None
    RAW_RXNORM_CUI: Optional[str] = None

    model_config = {"from_attributes": True}


class DispensingSchema(BaseModel):
    DISPENSINGID: str
    PATID: str
    PRESCRIBINGID: Optional[str] = None
    DISPENSE_DATE: Optional[date] = None
    NDC: Optional[str] = None
    DISPENSE_SOURCE: Optional[str] = None
    DISPENSE_SUP: Optional[float] = None
    DISPENSE_AMT: Optional[float] = None
    DISPENSE_DOSE_DISP: Optional[float] = None
    DISPENSE_DOSE_DISP_UNIT: Optional[str] = None
    DISPENSE_ROUTE: Optional[str] = None
    RAW_NDC: Optional[str] = None

    model_config = {"from_attributes": True}


class ConditionSchema(BaseModel):
    CONDITIONID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    REPORT_DATE: Optional[date] = None
    RESOLVE_DATE: Optional[date] = None
    ONSET_DATE: Optional[date] = None
    CONDITION_STATUS: Optional[str] = None
    CONDITION: Optional[str] = None
    CONDITION_TYPE: Optional[str] = None
    CONDITION_SOURCE: Optional[str] = None

    model_config = {"from_attributes": True}


class DeathSchema(BaseModel):
    PATID: str
    DEATH_DATE: Optional[date] = None
    DEATH_DATE_IMPUTE: Optional[str] = None
    DEATH_SOURCE: Optional[str] = None
    DEATH_MATCH_CONFIDENCE: Optional[str] = None

    model_config = {"from_attributes": True}


class DeathCauseSchema(BaseModel):
    PATID: str
    DEATH_CAUSE: str
    DEATH_CAUSE_CODE: str
    DEATH_CAUSE_TYPE: str
    DEATH_CAUSE_SOURCE: str
    DEATH_CAUSE_CONFIDENCE: Optional[str] = None

    model_config = {"from_attributes": True}


class EnrollmentSchema(BaseModel):
    PATID: str
    ENR_START_DATE: date
    ENR_END_DATE: Optional[date] = None
    CHART: Optional[str] = None
    ENR_BASIS: str

    model_config = {"from_attributes": True}


class MedAdminSchema(BaseModel):
    MEDADMINID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    PRESCRIBINGID: Optional[str] = None
    MEDADMIN_PROVIDERID: Optional[str] = None
    MEDADMIN_START_DATE: Optional[date] = None
    MEDADMIN_START_TIME: Optional[str] = None
    MEDADMIN_STOP_DATE: Optional[date] = None
    MEDADMIN_STOP_TIME: Optional[str] = None
    MEDADMIN_TYPE: Optional[str] = None
    MEDADMIN_CODE: Optional[str] = None
    MEDADMIN_DOSE_ADMIN: Optional[float] = None
    MEDADMIN_DOSE_ADMIN_UNIT: Optional[str] = None
    MEDADMIN_ROUTE: Optional[str] = None
    MEDADMIN_SOURCE: Optional[str] = None

    model_config = {"from_attributes": True}


class ObsClinSchema(BaseModel):
    OBSCLINID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    OBSCLIN_PROVIDERID: Optional[str] = None
    OBSCLIN_DATE: Optional[date] = None
    OBSCLIN_TIME: Optional[str] = None
    OBSCLIN_TYPE: Optional[str] = None
    OBSCLIN_CODE: Optional[str] = None
    OBSCLIN_RESULT_QUAL: Optional[str] = None
    OBSCLIN_RESULT_TEXT: Optional[str] = None
    OBSCLIN_RESULT_SNOMED: Optional[str] = None
    OBSCLIN_RESULT_NUM: Optional[float] = None
    OBSCLIN_RESULT_MODIFIER: Optional[str] = None
    OBSCLIN_RESULT_UNIT: Optional[str] = None
    OBSCLIN_SOURCE: Optional[str] = None
    OBSCLIN_ABN_IND: Optional[str] = None

    model_config = {"from_attributes": True}


class ObsGenSchema(BaseModel):
    OBSGENID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    OBSGEN_PROVIDERID: Optional[str] = None
    OBSGEN_DATE: Optional[date] = None
    OBSGEN_TIME: Optional[str] = None
    OBSGEN_TYPE: Optional[str] = None
    OBSGEN_CODE: Optional[str] = None
    OBSGEN_RESULT_QUAL: Optional[str] = None
    OBSGEN_RESULT_TEXT: Optional[str] = None
    OBSGEN_RESULT_NUM: Optional[float] = None
    OBSGEN_RESULT_MODIFIER: Optional[str] = None
    OBSGEN_RESULT_UNIT: Optional[str] = None
    OBSGEN_TABLE_MODIFIED: Optional[str] = None
    OBSGEN_ID_MODIFIED: Optional[str] = None

    model_config = {"from_attributes": True}


class PcornetTrialSchema(BaseModel):
    PATID: str
    TRIALID: str
    PARTICIPANTID: Optional[str] = None
    TRIAL_SITEID: Optional[str] = None
    TRIAL_ENROLL_DATE: Optional[date] = None
    TRIAL_END_DATE: Optional[date] = None
    TRIAL_WITHDRAW_DATE: Optional[date] = None
    TRIAL_INVITE_CODE: Optional[str] = None

    model_config = {"from_attributes": True}


class ProCmSchema(BaseModel):
    PRO_CM_ID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    PRO_DATE: Optional[date] = None
    PRO_TIME: Optional[str] = None
    PRO_TYPE: Optional[str] = None
    PRO_ITEM_LOINC: Optional[str] = None
    PRO_ITEM_NAME: Optional[str] = None
    PRO_MEASURE_LOINC: Optional[str] = None
    PRO_MEASURE_NAME: Optional[str] = None
    PRO_RESPONSE_TEXT: Optional[str] = None
    PRO_RESPONSE_NUM: Optional[float] = None
    PRO_METHOD: Optional[str] = None
    PRO_MODE: Optional[str] = None
    PRO_CAT: Optional[str] = None
    PRO_SOURCE: Optional[str] = None

    model_config = {"from_attributes": True}


class ProviderSchema(BaseModel):
    PROVIDERID: str
    PROVIDER_SEX: Optional[str] = None
    PROVIDER_SPECIALTY_PRIMARY: Optional[str] = None
    PROVIDER_NPI: Optional[str] = None
    PROVIDER_NPI_FLAG: Optional[str] = None

    model_config = {"from_attributes": True}


class ImmunizationSchema(BaseModel):
    IMMUNIZATIONID: str
    PATID: str
    ENCOUNTERID: Optional[str] = None
    PROCEDURESID: Optional[str] = None
    VX_PROVIDERID: Optional[str] = None
    VX_RECORD_DATE: Optional[date] = None
    VX_ADMIN_DATE: Optional[date] = None
    VX_CODE_TYPE: Optional[str] = None
    VX_CODE: Optional[str] = None
    VX_STATUS: Optional[str] = None
    VX_STATUS_REASON: Optional[str] = None
    VX_SOURCE: Optional[str] = None
    VX_DOSE_NUM: Optional[float] = None
    VX_SERIES_COMPLETE: Optional[str] = None
    VX_MANUFACTURER: Optional[str] = None
    VX_LOT_NUM: Optional[str] = None
    VX_ROUTE: Optional[str] = None
    VX_BODY_SITE: Optional[str] = None
    VX_DOSE: Optional[float] = None
    VX_DOSE_UNIT: Optional[str] = None
    PROCEDURE_DATE: Optional[date] = None

    model_config = {"from_attributes": True}


class HashTokenSchema(BaseModel):
    PATID: str
    TOKEN_ENCRYPTION_KEY: Optional[str] = None

    model_config = {"from_attributes": True}


class LdsAddressHistorySchema(BaseModel):
    ADDRESSID: str
    PATID: str
    ADDRESS_USE: Optional[str] = None
    ADDRESS_TYPE: Optional[str] = None
    ADDRESS_PREFERRED: Optional[str] = None
    ADDRESS_CITY: Optional[str] = None
    ADDRESS_STATE: Optional[str] = None
    ADDRESS_ZIP5: Optional[str] = None
    ADDRESS_ZIP9: Optional[str] = None
    ADDRESS_COUNTY: Optional[str] = None
    ADDRESS_PERIOD_START: Optional[date] = None
    ADDRESS_PERIOD_END: Optional[date] = None

    model_config = {"from_attributes": True}
