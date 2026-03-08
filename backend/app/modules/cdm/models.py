"""PCORnet CDM v7.0 SQLAlchemy models for all 22 tables."""
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Demographic(Base):
    __tablename__ = "DEMOGRAPHIC"

    PATID: Mapped[str] = mapped_column(String(50), primary_key=True)
    BIRTH_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    BIRTH_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    SEX: Mapped[str | None] = mapped_column(String(2), nullable=True)
    SEXUAL_ORIENTATION: Mapped[str | None] = mapped_column(String(2), nullable=True)
    GENDER_IDENTITY: Mapped[str | None] = mapped_column(String(2), nullable=True)
    HISPANIC: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RACE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    BIOBANK_FLAG: Mapped[str | None] = mapped_column(String(1), nullable=True)
    PAT_PREF_LANGUAGE_SPOKEN: Mapped[str | None] = mapped_column(String(3), nullable=True)
    RAW_SEX: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_SEXUAL_ORIENTATION: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_GENDER_IDENTITY: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_HISPANIC: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_RACE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_PAT_PREF_LANGUAGE_SPOKEN: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Encounter(Base):
    __tablename__ = "ENCOUNTER"

    ENCOUNTERID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ADMIT_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ADMIT_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    DISCHARGE_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    DISCHARGE_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    FACILITY_LOCATION: Mapped[str | None] = mapped_column(String(3), nullable=True)
    ENC_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    FACILITYID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    DISCHARGE_DISPOSITION: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DISCHARGE_STATUS: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DRG: Mapped[str | None] = mapped_column(String(3), nullable=True)
    DRG_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ADMITTING_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PAYER_TYPE_PRIMARY: Mapped[str | None] = mapped_column(String(3), nullable=True)
    PAYER_TYPE_SECONDARY: Mapped[str | None] = mapped_column(String(3), nullable=True)
    FACILITY_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_SITEID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_ENC_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DISCHARGE_DISPOSITION: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DISCHARGE_STATUS: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DRG_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_ADMITTING_SOURCE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_PAYER_TYPE_PRIMARY: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_PAYER_TYPE_SECONDARY: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_FACILITY_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Diagnosis(Base):
    __tablename__ = "DIAGNOSIS"

    DIAGNOSISID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    ENC_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ADMIT_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    DX: Mapped[str | None] = mapped_column(String(18), nullable=True)
    DX_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DX_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DX_ORIGIN: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PDX: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DX_POA: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_DX: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DX_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DX_SOURCE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DX_ORIGIN: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_PDX: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DX_POA: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Procedures(Base):
    __tablename__ = "PROCEDURES"

    PROCEDURESID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    ENC_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ADMIT_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    PX_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    PX: Mapped[str | None] = mapped_column(String(11), nullable=True)
    PX_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PX_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PPX: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_PX: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_PX_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_PPX: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Vital(Base):
    __tablename__ = "VITAL"

    VITALID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    MEASURE_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    MEASURE_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    VITAL_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    HT: Mapped[float | None] = mapped_column(Float, nullable=True)
    WT: Mapped[float | None] = mapped_column(Float, nullable=True)
    DIASTOLIC: Mapped[float | None] = mapped_column(Float, nullable=True)
    SYSTOLIC: Mapped[float | None] = mapped_column(Float, nullable=True)
    ORIGINAL_BMI: Mapped[float | None] = mapped_column(Float, nullable=True)
    BP_POSITION: Mapped[str | None] = mapped_column(String(2), nullable=True)
    SMOKING: Mapped[str | None] = mapped_column(String(2), nullable=True)
    TOBACCO: Mapped[str | None] = mapped_column(String(2), nullable=True)
    TOBACCO_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_DIASTOLIC: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_SYSTOLIC: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_BP_POSITION: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_SMOKING: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_TOBACCO: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_TOBACCO_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_VITAL_SOURCE: Mapped[str | None] = mapped_column(String(50), nullable=True)


class LabResultCm(Base):
    __tablename__ = "LAB_RESULT_CM"

    LAB_RESULT_CM_ID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    ACCESSION_ID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    LAB_LOINC: Mapped[str | None] = mapped_column(String(10), nullable=True)
    LAB_RESULT_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    LAB_LOINC_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PRIORITY: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RESULT_LOC: Mapped[str | None] = mapped_column(String(2), nullable=True)
    LAB_PX: Mapped[str | None] = mapped_column(String(11), nullable=True)
    LAB_PX_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    LAB_ORDER_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    SPECIMEN_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    SPECIMEN_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    RESULT_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    RESULT_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    RESULT_QUAL: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RESULT_SNOMED: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RESULT_NUM: Mapped[float | None] = mapped_column(Float, nullable=True)
    RESULT_MODIFIER: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RESULT_UNIT: Mapped[str | None] = mapped_column(String(11), nullable=True)
    NORM_RANGE_LOW: Mapped[str | None] = mapped_column(String(10), nullable=True)
    NORM_MODIFIER_LOW: Mapped[str | None] = mapped_column(String(2), nullable=True)
    NORM_RANGE_HIGH: Mapped[str | None] = mapped_column(String(10), nullable=True)
    NORM_MODIFIER_HIGH: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ABN_IND: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_LAB_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    RAW_LAB_CODE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_PANEL: Mapped[str | None] = mapped_column(String(100), nullable=True)
    RAW_RESULT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_ORDER_DEPT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_FACILITY_CODE: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Prescribing(Base):
    __tablename__ = "PRESCRIBING"

    PRESCRIBINGID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    RX_PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RX_ORDER_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    RX_ORDER_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    RX_START_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    RX_END_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    RX_QUANTITY: Mapped[float | None] = mapped_column(Float, nullable=True)
    RX_QUANTITY_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RX_REFILLS: Mapped[int | None] = mapped_column(Integer, nullable=True)
    RX_DAYS_SUPPLY: Mapped[int | None] = mapped_column(Integer, nullable=True)
    RX_FREQUENCY: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RX_PRN_FLAG: Mapped[str | None] = mapped_column(String(1), nullable=True)
    RX_ROUTE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RX_BASIS: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RXNORM_CUI: Mapped[str | None] = mapped_column(String(8), nullable=True)
    RX_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RX_DISPENSE_AS_WRITTEN: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_RX_MED_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    RAW_RX_FREQUENCY: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_RX_QUANTITY: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_RX_ROUTE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_RX_BASIS: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_RXNORM_CUI: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Dispensing(Base):
    __tablename__ = "DISPENSING"

    DISPENSINGID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    PRESCRIBINGID: Mapped[str | None] = mapped_column(String(50), ForeignKey("PRESCRIBING.PRESCRIBINGID"), nullable=True, index=True)
    DISPENSE_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    NDC: Mapped[str | None] = mapped_column(String(11), nullable=True)
    DISPENSE_SUP: Mapped[int | None] = mapped_column(Integer, nullable=True)
    DISPENSE_AMT: Mapped[float | None] = mapped_column(Float, nullable=True)
    DISPENSE_DOSE_DISP: Mapped[float | None] = mapped_column(Float, nullable=True)
    DISPENSE_DOSE_DISP_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    DISPENSE_ROUTE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DISPENSE_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_NDC: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DISPENSE_DOSE_DISP: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DISPENSE_DOSE_DISP_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_DISPENSE_ROUTE: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Condition(Base):
    __tablename__ = "CONDITION"

    CONDITIONID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    REPORT_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    RESOLVE_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ONSET_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    CONDITION_STATUS: Mapped[str | None] = mapped_column(String(2), nullable=True)
    CONDITION: Mapped[str | None] = mapped_column(String(18), nullable=True)
    CONDITION_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    CONDITION_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_CONDITION_STATUS: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_CONDITION: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_CONDITION_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_CONDITION_SOURCE: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Death(Base):
    __tablename__ = "DEATH"

    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True)
    DEATH_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    DEATH_DATE_IMPUTE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DEATH_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    DEATH_MATCH_CONFIDENCE: Mapped[str | None] = mapped_column(String(2), nullable=True)


class DeathCause(Base):
    __tablename__ = "DEATH_CAUSE"

    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True)
    DEATH_CAUSE: Mapped[str] = mapped_column(String(8), primary_key=True)
    DEATH_CAUSE_CODE: Mapped[str] = mapped_column(String(2), primary_key=True)
    DEATH_CAUSE_TYPE: Mapped[str] = mapped_column(String(2), primary_key=True)
    DEATH_CAUSE_SOURCE: Mapped[str] = mapped_column(String(2), primary_key=True)
    DEATH_CAUSE_CONFIDENCE: Mapped[str | None] = mapped_column(String(2), nullable=True)


class Enrollment(Base):
    __tablename__ = "ENROLLMENT"

    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True)
    ENR_START_DATE: Mapped[str] = mapped_column(String(10), primary_key=True)
    ENR_BASIS: Mapped[str] = mapped_column(String(1), primary_key=True)
    ENR_END_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    CHART: Mapped[str | None] = mapped_column(String(1), nullable=True)
    RAW_CHART: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Harvest(Base):
    __tablename__ = "HARVEST"

    NETWORKID: Mapped[str] = mapped_column(String(10), primary_key=True)
    NETWORK_NAME: Mapped[str | None] = mapped_column(String(20), nullable=True)
    DATAMARTID: Mapped[str | None] = mapped_column(String(10), nullable=True)
    DATAMART_NAME: Mapped[str | None] = mapped_column(String(20), nullable=True)
    DATAMART_PLATFORM: Mapped[str | None] = mapped_column(String(2), nullable=True)
    CDM_VERSION: Mapped[str | None] = mapped_column(String(6), nullable=True)
    DATAMART_CLAIMS: Mapped[str | None] = mapped_column(String(1), nullable=True)
    DATAMART_EHR: Mapped[str | None] = mapped_column(String(1), nullable=True)
    BIRTH_DATE_IMPOSED: Mapped[str | None] = mapped_column(String(1), nullable=True)
    BIRTH_DATE_SHIFT: Mapped[int | None] = mapped_column(Integer, nullable=True)
    REFRESH_DEMOGRAPHIC_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_ENROLLMENT_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_ENCOUNTER_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_DIAGNOSIS_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_PROCEDURES_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_VITAL_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_DISPENSING_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_LAB_RESULT_CM_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_CONDITION_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_PRO_CM_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_PRESCRIBING_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_PCORNET_TRIAL_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_DEATH_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_DEATH_CAUSE_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_MED_ADMIN_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_OBS_GEN_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_LDS_ADDRESS_HISTORY_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_IMMUNIZATION_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    REFRESH_OBS_CLIN_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)


class LdsAddressHistory(Base):
    __tablename__ = "LDS_ADDRESS_HISTORY"

    ADDRESSID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ADDRESS_USE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ADDRESS_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ADDRESS_PREFERRED: Mapped[str | None] = mapped_column(String(1), nullable=True)
    ADDRESS_CITY: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ADDRESS_STATE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ADDRESS_ZIP5: Mapped[str | None] = mapped_column(String(5), nullable=True)
    ADDRESS_ZIP9: Mapped[str | None] = mapped_column(String(9), nullable=True)
    ADDRESS_COUNTY: Mapped[str | None] = mapped_column(String(3), nullable=True)
    ADDRESS_PERIOD_START: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ADDRESS_PERIOD_END: Mapped[str | None] = mapped_column(String(10), nullable=True)


class MedAdmin(Base):
    __tablename__ = "MED_ADMIN"

    MEDADMINID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    PRESCRIBINGID: Mapped[str | None] = mapped_column(String(50), ForeignKey("PRESCRIBING.PRESCRIBINGID"), nullable=True)
    MEDADMIN_PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    MEDADMIN_START_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    MEDADMIN_START_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    MEDADMIN_STOP_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    MEDADMIN_STOP_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    MEDADMIN_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    MEDADMIN_CODE: Mapped[str | None] = mapped_column(String(11), nullable=True)
    MEDADMIN_DOSE_ADMIN: Mapped[float | None] = mapped_column(Float, nullable=True)
    MEDADMIN_DOSE_ADMIN_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    MEDADMIN_ROUTE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    MEDADMIN_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_MEDADMIN_MED_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    RAW_MEDADMIN_CODE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_MEDADMIN_DOSE_ADMIN: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_MEDADMIN_DOSE_ADMIN_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_MEDADMIN_ROUTE: Mapped[str | None] = mapped_column(String(50), nullable=True)


class ObsClin(Base):
    __tablename__ = "OBS_CLIN"

    OBSCLINID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    OBSCLIN_PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    OBSCLIN_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    OBSCLIN_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    OBSCLIN_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    OBSCLIN_CODE: Mapped[str | None] = mapped_column(String(18), nullable=True)
    OBSCLIN_RESULT_TEXT: Mapped[str | None] = mapped_column(Text, nullable=True)
    OBSCLIN_RESULT_SNOMED: Mapped[str | None] = mapped_column(String(50), nullable=True)
    OBSCLIN_RESULT_NUM: Mapped[float | None] = mapped_column(Float, nullable=True)
    OBSCLIN_RESULT_MODIFIER: Mapped[str | None] = mapped_column(String(2), nullable=True)
    OBSCLIN_RESULT_UNIT: Mapped[str | None] = mapped_column(String(11), nullable=True)
    OBSCLIN_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    OBSCLIN_ABN_IND: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_OBSCLIN_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    RAW_OBSCLIN_CODE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_OBSCLIN_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_OBSCLIN_RESULT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_OBSCLIN_MODIFIER: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_OBSCLIN_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)


class ObsGen(Base):
    __tablename__ = "OBS_GEN"

    OBSGENID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    OBSGEN_PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    OBSGEN_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    OBSGEN_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    OBSGEN_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    OBSGEN_CODE: Mapped[str | None] = mapped_column(String(18), nullable=True)
    OBSGEN_RESULT_TEXT: Mapped[str | None] = mapped_column(Text, nullable=True)
    OBSGEN_RESULT_NUM: Mapped[float | None] = mapped_column(Float, nullable=True)
    OBSGEN_RESULT_MODIFIER: Mapped[str | None] = mapped_column(String(2), nullable=True)
    OBSGEN_RESULT_UNIT: Mapped[str | None] = mapped_column(String(11), nullable=True)
    OBSGEN_TABLE_MODIFIED: Mapped[str | None] = mapped_column(String(2), nullable=True)
    OBSGEN_ID_MODIFIED: Mapped[str | None] = mapped_column(String(50), nullable=True)
    OBSGEN_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    RAW_OBSGEN_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    RAW_OBSGEN_CODE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_OBSGEN_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_OBSGEN_RESULT: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_OBSGEN_UNIT: Mapped[str | None] = mapped_column(String(50), nullable=True)


class PcornetTrial(Base):
    __tablename__ = "PCORNET_TRIAL"

    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True)
    TRIALID: Mapped[str] = mapped_column(String(20), primary_key=True)
    PARTICIPANTID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    TRIAL_SITEID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    TRIAL_ENROLL_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    TRIAL_END_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    TRIAL_WITHDRAW_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    TRIAL_INVITE_CODE: Mapped[str | None] = mapped_column(String(20), nullable=True)


class ProCm(Base):
    __tablename__ = "PRO_CM"

    PRO_CM_ID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    PRO_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    PRO_TIME: Mapped[str | None] = mapped_column(String(5), nullable=True)
    PRO_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PRO_ITEM_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    PRO_ITEM_LOINC: Mapped[str | None] = mapped_column(String(10), nullable=True)
    PRO_RESPONSE_TEXT: Mapped[str | None] = mapped_column(Text, nullable=True)
    PRO_RESPONSE_NUM: Mapped[float | None] = mapped_column(Float, nullable=True)
    PRO_METHOD: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PRO_MODE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PRO_CAT: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PRO_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PRO_MEASURE_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    PRO_MEASURE_SEQ: Mapped[str | None] = mapped_column(String(4), nullable=True)
    PRO_MEASURE_SCORE: Mapped[float | None] = mapped_column(Float, nullable=True)
    PRO_MEASURE_THETA: Mapped[float | None] = mapped_column(Float, nullable=True)
    PRO_MEASURE_SE: Mapped[float | None] = mapped_column(Float, nullable=True)
    PRO_MEASURE_COUNT_SCORED: Mapped[int | None] = mapped_column(Integer, nullable=True)
    PRO_MEASURE_LOINC: Mapped[str | None] = mapped_column(String(10), nullable=True)
    PRO_MEASURE_VERSION: Mapped[str | None] = mapped_column(String(20), nullable=True)
    PRO_MEASURE_AGREEMENT_STAT: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PRO_MEASURE_PAIRED_TEST_ID: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Provider(Base):
    __tablename__ = "PROVIDER"

    PROVIDERID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PROVIDER_SEX: Mapped[str | None] = mapped_column(String(2), nullable=True)
    PROVIDER_SPECIALTY_PRIMARY: Mapped[str | None] = mapped_column(String(3), nullable=True)
    PROVIDER_NPI: Mapped[str | None] = mapped_column(String(10), nullable=True)
    RAW_PROVIDER_SPECIALTY_PRIMARY: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Immunization(Base):
    __tablename__ = "IMMUNIZATION"

    IMMUNIZATIONID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), nullable=False, index=True)
    ENCOUNTERID: Mapped[str | None] = mapped_column(String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True, index=True)
    PROCEDURESID: Mapped[str | None] = mapped_column(String(50), ForeignKey("PROCEDURES.PROCEDURESID"), nullable=True)
    VX_PROVIDERID: Mapped[str | None] = mapped_column(String(50), nullable=True)
    VX_RECORD_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    VX_ADMIN_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    VX_CODE_TYPE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    VX_CODE: Mapped[str | None] = mapped_column(String(30), nullable=True)
    VX_STATUS: Mapped[str | None] = mapped_column(String(2), nullable=True)
    VX_STATUS_REASON: Mapped[str | None] = mapped_column(String(2), nullable=True)
    VX_SOURCE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    VX_DOSE_NUM: Mapped[float | None] = mapped_column(Float, nullable=True)
    VX_SERIES_COMPLETE: Mapped[str | None] = mapped_column(String(2), nullable=True)
    VX_MANUFACTURER: Mapped[str | None] = mapped_column(String(10), nullable=True)
    VX_LOT_NUM: Mapped[str | None] = mapped_column(String(50), nullable=True)
    VX_EXP_DATE: Mapped[str | None] = mapped_column(String(10), nullable=True)
    RAW_VX_NAME: Mapped[str | None] = mapped_column(String(100), nullable=True)
    RAW_VX_CODE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_VX_CODE_TYPE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_VX_DOSE_NUM: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_VX_SERIES_COMPLETE: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_VX_STATUS: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_VX_STATUS_REASON: Mapped[str | None] = mapped_column(String(50), nullable=True)
    RAW_VX_SOURCE: Mapped[str | None] = mapped_column(String(50), nullable=True)


class HashToken(Base):
    __tablename__ = "HASH_TOKEN"

    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True)
    TOKEN_ENCRYPTION_KEY: Mapped[str | None] = mapped_column(String(50), nullable=True)
    HASHED_ID: Mapped[str | None] = mapped_column(String(256), nullable=True)
    TOKEN_APPEND: Mapped[str | None] = mapped_column(String(50), nullable=True)
