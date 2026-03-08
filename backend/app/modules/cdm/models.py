from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Demographic(Base):
    __tablename__ = "DEMOGRAPHIC"

    PATID: Mapped[str] = mapped_column(String(50), primary_key=True)
    BIRTH_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    BIRTH_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    SEX: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    SEXUAL_ORIENTATION: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    GENDER_IDENTITY: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    HISPANIC: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RACE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    BIOBANK_FLAG: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    PAT_PREF_LANGUAGE_SPOKEN: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    RAW_SEX: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_SEXUAL_ORIENTATION: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_GENDER_IDENTITY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_HISPANIC: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RACE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PAT_PREF_LANGUAGE_SPOKEN: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Encounter(Base):
    __tablename__ = "ENCOUNTER"

    ENCOUNTERID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ADMIT_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ADMIT_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    DISCHARGE_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    DISCHARGE_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    FACILITY_LOCATION: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    ENC_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    FACILITYID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    DISCHARGE_DISPOSITION: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DISCHARGE_STATUS: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DRG: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    DRG_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ADMITTING_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PAYER_TYPE_PRIMARY: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PAYER_TYPE_SECONDARY: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    FACILITY_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_ADMITTING_SOURCE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DISCHARGE_DISPOSITION: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DISCHARGE_STATUS: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DRG_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_ENC_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PAYER_TYPE_PRIMARY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PAYER_TYPE_SECONDARY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_FACILITY_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Diagnosis(Base):
    __tablename__ = "DIAGNOSIS"

    DIAGNOSISID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    ENC_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ADMIT_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    DX: Mapped[Optional[str]] = mapped_column(String(18), nullable=True)
    DX_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DX_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DX_ORIGIN: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PDX: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DX_POA: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_DX: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DX_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DX_SOURCE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DX_ORIGIN: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PDX: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DX_POA: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Procedures(Base):
    __tablename__ = "PROCEDURES"

    PROCEDURESID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    ENC_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ADMIT_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    PX_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    PX: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    PX_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PX_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PPX: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_PX: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PX_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PPX: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Vital(Base):
    __tablename__ = "VITAL"

    VITALID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    MEASURE_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    MEASURE_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    VITAL_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    HT: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    WT: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    DIASTOLIC: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    SYSTOLIC: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ORIGINAL_BMI: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    BP_POSITION: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    SMOKING: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    TOBACCO: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    TOBACCO_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_DIASTOLIC: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_SYSTOLIC: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_BP_POSITION: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_SMOKING: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_TOBACCO: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_TOBACCO_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VITAL_SOURCE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class LabResultCm(Base):
    __tablename__ = "LAB_RESULT_CM"

    LAB_RESULT_CM_ID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    SPECIMEN_SOURCE: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    LAB_LOINC: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    LAB_RESULT_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    LAB_LOINC_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PRIORITY: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RESULT_LOC: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    LAB_PX: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    LAB_PX_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    LAB_ORDER_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    SPECIMEN_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    SPECIMEN_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    RESULT_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    RESULT_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    RESULT_QUAL: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    RESULT_SNOMED: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    RESULT_NUM: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    RESULT_MODIFIER: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RESULT_UNIT: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    NORM_RANGE_LOW: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    NORM_MODIFIER_LOW: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    NORM_RANGE_HIGH: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    NORM_MODIFIER_HIGH: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ABN_IND: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_LAB_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_LAB_CODE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PANEL: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RESULT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_UNIT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_ORDER_DEPT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_FACILITY_CODE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Prescribing(Base):
    __tablename__ = "PRESCRIBING"

    PRESCRIBINGID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    RX_PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    RX_ORDER_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    RX_ORDER_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    RX_START_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    RX_END_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    RX_QUANTITY: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    RX_QUANTITY_UNIT: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    RX_REFILLS: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    RX_DAYS_SUPPLY: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    RX_FREQUENCY: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RX_PRN_FLAG: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    RX_ROUTE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RX_BASIS: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RXNORM_CUI: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    RX_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RX_DISPENSE_AS_WRITTEN: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_RX_MED_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RX_FREQUENCY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RXNORM_CUI: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RX_QUANTITY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RX_NDC: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RX_DOSE_ORDERED: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RX_DOSE_ORDERED_UNIT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RX_ROUTE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_RX_BASIS: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Dispensing(Base):
    __tablename__ = "DISPENSING"

    DISPENSINGID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    PRESCRIBINGID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("PRESCRIBING.PRESCRIBINGID"), nullable=True
    )
    DISPENSE_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    NDC: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    DISPENSE_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DISPENSE_SUP: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    DISPENSE_AMT: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    DISPENSE_DOSE_DISP: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    DISPENSE_DOSE_DISP_UNIT: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    DISPENSE_ROUTE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_NDC: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DISPENSE_DOSE_DISP: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DISPENSE_DOSE_DISP_UNIT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_DISPENSE_ROUTE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Condition(Base):
    __tablename__ = "CONDITION"

    CONDITIONID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    REPORT_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    RESOLVE_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ONSET_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    CONDITION_STATUS: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    CONDITION: Mapped[Optional[str]] = mapped_column(String(18), nullable=True)
    CONDITION_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    CONDITION_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_CONDITION_STATUS: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_CONDITION: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_CONDITION_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_CONDITION_SOURCE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Death(Base):
    __tablename__ = "DEATH"

    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True)
    DEATH_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    DEATH_DATE_IMPUTE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DEATH_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DEATH_MATCH_CONFIDENCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)


class DeathCause(Base):
    __tablename__ = "DEATH_CAUSE"

    PATID: Mapped[str] = mapped_column(
        String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True
    )
    DEATH_CAUSE: Mapped[str] = mapped_column(String(8), primary_key=True)
    DEATH_CAUSE_CODE: Mapped[str] = mapped_column(String(2), primary_key=True)
    DEATH_CAUSE_TYPE: Mapped[str] = mapped_column(String(2), primary_key=True)
    DEATH_CAUSE_SOURCE: Mapped[str] = mapped_column(String(2), primary_key=True)
    DEATH_CAUSE_CONFIDENCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)


class Enrollment(Base):
    __tablename__ = "ENROLLMENT"

    PATID: Mapped[str] = mapped_column(
        String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True
    )
    ENR_START_DATE: Mapped[date] = mapped_column(Date, primary_key=True)
    ENR_END_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    CHART: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    ENR_BASIS: Mapped[str] = mapped_column(String(1), primary_key=True)
    RAW_CHART: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_BASIS: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Harvest(Base):
    __tablename__ = "HARVEST"

    NETWORKID: Mapped[str] = mapped_column(String(10), primary_key=True)
    NETWORK_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    DATAMARTID: Mapped[str] = mapped_column(String(10))
    DATAMART_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    DATAMART_PLATFORM: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    CDM_VERSION: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    DATAMART_CLAIMS: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    DATAMART_EHR: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    BIRTH_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ENR_START_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ENR_END_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ADMIT_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DISCHARGE_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PX_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RX_ORDER_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RX_START_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RX_END_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    DISPENSE_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    LAB_ORDER_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    SPECIMEN_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RESULT_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    MEASURE_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ONSET_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    REPORT_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RESOLVE_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PRO_DATE_MGMT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    REFRESH_DEMOGRAPHIC_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_ENROLLMENT_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_ENCOUNTER_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_DIAGNOSIS_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_PROCEDURES_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_VITAL_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_DISPENSING_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_LAB_RESULT_CM_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_CONDITION_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_PRO_CM_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_PRESCRIBING_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_PCORNET_TRIAL_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_DEATH_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_DEATH_CAUSE_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_MED_ADMIN_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_OBS_CLIN_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_OBS_GEN_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_IMMUNIZATION_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_LDS_ADDRESS_HISTORY_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    REFRESH_PROVIDER_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class LdsAddressHistory(Base):
    __tablename__ = "LDS_ADDRESS_HISTORY"

    ADDRESSID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ADDRESS_USE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ADDRESS_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ADDRESS_PREFERRED: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    ADDRESS_CITY: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ADDRESS_STATE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    ADDRESS_ZIP5: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    ADDRESS_ZIP9: Mapped[Optional[str]] = mapped_column(String(9), nullable=True)
    ADDRESS_COUNTY: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    ADDRESS_PERIOD_START: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ADDRESS_PERIOD_END: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class MedAdmin(Base):
    __tablename__ = "MED_ADMIN"

    MEDADMINID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    PRESCRIBINGID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    MEDADMIN_PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    MEDADMIN_START_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    MEDADMIN_START_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    MEDADMIN_STOP_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    MEDADMIN_STOP_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    MEDADMIN_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    MEDADMIN_CODE: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    MEDADMIN_DOSE_ADMIN: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    MEDADMIN_DOSE_ADMIN_UNIT: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    MEDADMIN_ROUTE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    MEDADMIN_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_MEDADMIN_MED_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_MEDADMIN_CODE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_MEDADMIN_DOSE_ADMIN: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_MEDADMIN_DOSE_ADMIN_UNIT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_MEDADMIN_ROUTE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class ObsClin(Base):
    __tablename__ = "OBS_CLIN"

    OBSCLINID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    OBSCLIN_PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    OBSCLIN_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    OBSCLIN_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    OBSCLIN_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    OBSCLIN_CODE: Mapped[Optional[str]] = mapped_column(String(18), nullable=True)
    OBSCLIN_RESULT_QUAL: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    OBSCLIN_RESULT_TEXT: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    OBSCLIN_RESULT_SNOMED: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    OBSCLIN_RESULT_NUM: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    OBSCLIN_RESULT_MODIFIER: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    OBSCLIN_RESULT_UNIT: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    OBSCLIN_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    OBSCLIN_ABN_IND: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_OBSCLIN_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSCLIN_CODE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSCLIN_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSCLIN_RESULT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSCLIN_MODIFIER: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSCLIN_UNIT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class ObsGen(Base):
    __tablename__ = "OBS_GEN"

    OBSGENID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    OBSGEN_PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    OBSGEN_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    OBSGEN_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    OBSGEN_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    OBSGEN_CODE: Mapped[Optional[str]] = mapped_column(String(18), nullable=True)
    OBSGEN_RESULT_QUAL: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    OBSGEN_RESULT_TEXT: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    OBSGEN_RESULT_NUM: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    OBSGEN_RESULT_MODIFIER: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    OBSGEN_RESULT_UNIT: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    OBSGEN_TABLE_MODIFIED: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    OBSGEN_ID_MODIFIED: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    RAW_OBSGEN_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSGEN_CODE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSGEN_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSGEN_RESULT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_OBSGEN_UNIT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class PcornetTrial(Base):
    __tablename__ = "PCORNET_TRIAL"

    PATID: Mapped[str] = mapped_column(
        String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True
    )
    TRIALID: Mapped[str] = mapped_column(String(20), primary_key=True)
    PARTICIPANTID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    TRIAL_SITEID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    TRIAL_ENROLL_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    TRIAL_END_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    TRIAL_WITHDRAW_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    TRIAL_INVITE_CODE: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class ProCm(Base):
    __tablename__ = "PRO_CM"

    PRO_CM_ID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    PRO_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    PRO_TIME: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    PRO_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PRO_ITEM_LOINC: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    PRO_ITEM_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    PRO_MEASURE_LOINC: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    PRO_MEASURE_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    PRO_RESPONSE_TEXT: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    PRO_RESPONSE_NUM: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    PRO_METHOD: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PRO_MODE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PRO_CAT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PRO_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_PRO_CODE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_PRO_RESPONSE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Provider(Base):
    __tablename__ = "PROVIDER"

    PROVIDERID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PROVIDER_SEX: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    PROVIDER_SPECIALTY_PRIMARY: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    PROVIDER_NPI: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    PROVIDER_NPI_FLAG: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    RAW_PROVIDER_SPECIALTY_PRIMARY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class Immunization(Base):
    __tablename__ = "IMMUNIZATION"

    IMMUNIZATIONID: Mapped[str] = mapped_column(String(50), primary_key=True)
    PATID: Mapped[str] = mapped_column(String(50), ForeignKey("DEMOGRAPHIC.PATID"))
    ENCOUNTERID: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("ENCOUNTER.ENCOUNTERID"), nullable=True
    )
    PROCEDURESID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    VX_PROVIDERID: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    VX_RECORD_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    VX_ADMIN_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    VX_CODE_TYPE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    VX_CODE: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    VX_STATUS: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    VX_STATUS_REASON: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    VX_SOURCE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    VX_DOSE_NUM: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    VX_SERIES_COMPLETE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    VX_MANUFACTURER: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    VX_LOT_NUM: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    VX_ROUTE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    VX_BODY_SITE: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    VX_DOSE: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    VX_DOSE_UNIT: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    RAW_VX_NAME: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VX_CODE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VX_CODE_TYPE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VX_STATUS: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VX_STATUS_REASON: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VX_ROUTE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VX_BODY_SITE: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_VX_DOSE_UNIT: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    PROCEDURE_DATE: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class HashToken(Base):
    __tablename__ = "HASH_TOKEN"

    PATID: Mapped[str] = mapped_column(
        String(50), ForeignKey("DEMOGRAPHIC.PATID"), primary_key=True
    )
    TOKEN_ENCRYPTION_KEY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    RAW_TOKEN_ENCRYPTION_KEY: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
