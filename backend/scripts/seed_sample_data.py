"""seed_sample_data.py — Insert synthetic sample data across all platform and CDM tables.

Run after migrations and seed_admin.py:
    cd backend && python3 scripts/seed_sample_data.py

Populates:
  - Platform tables: users (analyst/viewer), integrations, ingestion_runs,
    quarantine, saved_queries, query_history, dashboards, dashboard_widgets,
    audit_log, chat_sessions, chat_messages
  - PCORnet CDM tables: DEMOGRAPHIC, ENCOUNTER, DIAGNOSIS, PROCEDURES, VITAL,
    LAB_RESULT_CM, PRESCRIBING, DISPENSING, CONDITION, DEATH, ENROLLMENT,
    PROVIDER, IMMUNIZATION, HARVEST

All data is 100% synthetic — no real PHI.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.core.database import async_session as async_session_factory
from app.core.security import get_password_hash


async def seed() -> None:
    async with async_session_factory() as db:
        # Check if sample data already seeded (look for analyst user)
        row = await db.execute(text("SELECT id FROM users WHERE username = 'analyst'"))
        if row.scalar_one_or_none() is not None:
            print("[seed_sample_data] Sample data already exists — skipping.")
            return

        # Get admin user id
        row = await db.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        admin_id = row.scalar_one_or_none()
        if admin_id is None:
            print("[seed_sample_data] ERROR: admin user not found. Run seed_admin.py first.")
            return

        print("[seed_sample_data] Inserting sample data...")

        # ──────────────────────────────────────────────────
        # 1. Additional users
        # ──────────────────────────────────────────────────
        print("  [1/14] Users...")
        await db.execute(
            text("""
                INSERT INTO users (username, email, password_hash, role, is_active, created_at)
                VALUES
                  ('analyst', 'analyst@enternal.health', :pw_analyst, 'analyst', true, NOW()),
                  ('viewer', 'viewer@enternal.health', :pw_viewer, 'viewer', true, NOW()),
                  ('dr_chen', 'chen@enternal.health', :pw_chen, 'analyst', true, NOW())
            """),
            {
                "pw_analyst": get_password_hash("analyst123"),
                "pw_viewer": get_password_hash("viewer123"),
                "pw_chen": get_password_hash("chen123"),
            },
        )

        # ──────────────────────────────────────────────────
        # 2. Integration (FHIR)
        # ──────────────────────────────────────────────────
        print("  [2/14] Integrations...")
        result = await db.execute(
            text("""
                INSERT INTO integrations (name, type, config_json, status, created_by, created_at, updated_at)
                VALUES
                  ('HAPI FHIR Server', 'fhir',
                   :fhir_config, 'active', :admin_id, NOW(), NOW()),
                  ('Athena DataView (Snowflake)', 'snowflake',
                   :sf_config, 'inactive', :admin_id, NOW(), NOW())
                RETURNING id
            """),
            {
                "admin_id": admin_id,
                "fhir_config": json.dumps(
                    {"server_url": "http://fhir:8080/fhir", "auth_type": "none"}
                ),
                "sf_config": json.dumps(
                    {
                        "account": "xy12345.us-east-1",
                        "username": "svc_enternal",
                        "password": "***",
                        "database": "ATHENA_DV",
                        "schema_name": "PUBLIC",
                        "warehouse": "COMPUTE_WH",
                        "role": "DATA_READER",
                    }
                ),
            },
        )
        integration_ids = [r[0] for r in result.fetchall()]
        fhir_int_id = integration_ids[0]

        # ──────────────────────────────────────────────────
        # 3. Ingestion runs
        # ──────────────────────────────────────────────────
        print("  [3/14] Ingestion runs...")
        result = await db.execute(
            text("""
                INSERT INTO ingestion_runs
                    (integration_id, status, records_processed, records_failed,
                     started_at, completed_at, error_message)
                VALUES
                  (:fid, 'completed', 247, 3, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 50 minutes', NULL),
                  (:fid, 'completed', 182, 0, NOW() - INTERVAL '1 day', NOW() - INTERVAL '23 hours', NULL),
                  (:fid, 'failed', 0, 0, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '2 minutes',
                   'Connection refused: FHIR server unreachable')
                RETURNING id
            """),
            {"fid": fhir_int_id},
        )
        run_ids = [r[0] for r in result.fetchall()]

        # ──────────────────────────────────────────────────
        # 4. Quarantine records
        # ──────────────────────────────────────────────────
        print("  [4/14] Quarantine records...")
        await db.execute(
            text("""
                INSERT INTO quarantine
                    (ingestion_run_id, source_data, error_message,
                     source_resource_type, source_resource_id, created_at)
                VALUES
                  (:run1, '{"resourceType":"Observation","id":"obs-bad-001"}'::jsonb,
                   'Missing required field: subject', 'Observation', 'obs-bad-001', NOW() - INTERVAL '2 hours'),
                  (:run1, '{"resourceType":"Condition","id":"cond-bad-001"}'::jsonb,
                   'Invalid ICD-10 code: ZZ99.9', 'Condition', 'cond-bad-001', NOW() - INTERVAL '2 hours'),
                  (:run1, '{"resourceType":"Patient","id":"pat-bad-001"}'::jsonb,
                   'Duplicate PATID detected', 'Patient', 'pat-bad-001', NOW() - INTERVAL '2 hours')
            """),
            {"run1": run_ids[0]},
        )

        # ──────────────────────────────────────────────────
        # 5. DEMOGRAPHIC (PCORnet CDM)
        # ──────────────────────────────────────────────────
        print("  [5/14] DEMOGRAPHIC...")
        await db.execute(
            text("""
                INSERT INTO "DEMOGRAPHIC" ("PATID", "BIRTH_DATE", "SEX", "HISPANIC", "RACE", "BIOBANK_FLAG",
                    "RAW_SEX", "RAW_RACE", "RAW_HISPANIC")
                VALUES
                  ('PAT001', '1985-07-23', 'F', 'N', '05', 'N', 'Female', 'White', 'Not Hispanic'),
                  ('PAT002', '1972-03-15', 'M', 'N', '03', 'N', 'Male', 'Black or African American', 'Not Hispanic'),
                  ('PAT003', '1990-11-02', 'F', 'Y', '02', 'Y', 'Female', 'Asian', 'Hispanic'),
                  ('PAT004', '1965-01-30', 'M', 'N', '05', 'N', 'Male', 'White', 'Not Hispanic'),
                  ('PAT005', '2001-08-14', 'F', 'N', '01', 'N', 'Female', 'American Indian', 'Not Hispanic'),
                  ('PAT006', '1958-12-05', 'M', 'Y', '02', 'N', 'Male', 'Asian', 'Hispanic'),
                  ('PAT007', '1995-04-18', 'F', 'N', '03', 'N', 'Female', 'Black or African American', 'Not Hispanic'),
                  ('PAT008', '1980-09-22', 'M', 'N', '05', 'N', 'Male', 'White', 'Not Hispanic'),
                  ('PAT009', '2010-06-11', 'F', 'N', '07', 'N', 'Female', 'Refuse to answer', 'Not Hispanic'),
                  ('PAT010', '1948-02-28', 'M', 'N', '05', 'Y', 'Male', 'White', 'Not Hispanic')
                ON CONFLICT ("PATID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 6. PROVIDER
        # ──────────────────────────────────────────────────
        print("  [6/14] PROVIDER...")
        await db.execute(
            text("""
                INSERT INTO "PROVIDER" ("PROVIDERID", "PROVIDER_SEX", "PROVIDER_SPECIALTY_PRIMARY", "PROVIDER_NPI")
                VALUES
                  ('PROV001', 'M', '207', '1234567890'),
                  ('PROV002', 'F', '208', '0987654321'),
                  ('PROV003', 'F', '207', '1122334455')
                ON CONFLICT ("PROVIDERID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 7. ENCOUNTER
        # ──────────────────────────────────────────────────
        print("  [7/14] ENCOUNTER...")
        await db.execute(
            text("""
                INSERT INTO "ENCOUNTER"
                    ("ENCOUNTERID", "PATID", "ADMIT_DATE", "ADMIT_TIME", "DISCHARGE_DATE",
                     "PROVIDERID", "ENC_TYPE", "DISCHARGE_DISPOSITION", "PAYER_TYPE_PRIMARY")
                VALUES
                  ('ENC001', 'PAT001', '2025-06-15', '09:00', '2025-06-15', 'PROV001', 'AV', 'A', '1'),
                  ('ENC002', 'PAT001', '2025-08-10', '14:30', '2025-08-10', 'PROV002', 'AV', 'A', '1'),
                  ('ENC003', 'PAT002', '2025-05-20', '10:00', '2025-05-22', 'PROV001', 'IP', 'A', '2'),
                  ('ENC004', 'PAT003', '2025-07-01', '08:00', '2025-07-01', 'PROV003', 'AV', 'A', '1'),
                  ('ENC005', 'PAT004', '2025-09-12', '16:00', '2025-09-12', 'PROV001', 'ED', 'A', '3'),
                  ('ENC006', 'PAT005', '2025-04-05', '11:00', '2025-04-05', 'PROV002', 'AV', 'A', '1'),
                  ('ENC007', 'PAT006', '2025-03-18', '09:30', '2025-03-20', 'PROV003', 'IP', 'A', '2'),
                  ('ENC008', 'PAT007', '2025-10-01', '13:00', '2025-10-01', 'PROV001', 'AV', 'A', '1'),
                  ('ENC009', 'PAT008', '2025-11-15', '07:45', '2025-11-15', 'PROV002', 'AV', 'A', '1'),
                  ('ENC010', 'PAT002', '2025-01-05', '10:00', '2025-01-10', 'PROV001', 'IP', 'E', '2')
                ON CONFLICT ("ENCOUNTERID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 8. DIAGNOSIS
        # ──────────────────────────────────────────────────
        print("  [8/14] DIAGNOSIS...")
        await db.execute(
            text("""
                INSERT INTO "DIAGNOSIS"
                    ("DIAGNOSISID", "PATID", "ENCOUNTERID", "DX", "DX_TYPE", "DX_SOURCE", "PDX", "ADMIT_DATE")
                VALUES
                  ('DX001', 'PAT001', 'ENC001', 'E11.9',  '10', 'AD', 'P', '2025-06-15'),
                  ('DX002', 'PAT001', 'ENC001', 'I10',    '10', 'AD', 'S', '2025-06-15'),
                  ('DX003', 'PAT002', 'ENC003', 'J44.1',  '10', 'AD', 'P', '2025-05-20'),
                  ('DX004', 'PAT002', 'ENC010', 'C34.90', '10', 'FI', 'P', '2025-01-05'),
                  ('DX005', 'PAT003', 'ENC004', 'O09.91', '10', 'AD', 'P', '2025-07-01'),
                  ('DX006', 'PAT004', 'ENC005', 'S72.001A','10', 'AD', 'P', '2025-09-12'),
                  ('DX007', 'PAT005', 'ENC006', 'J06.9',  '10', 'AD', 'P', '2025-04-05'),
                  ('DX008', 'PAT006', 'ENC007', 'I25.10', '10', 'AD', 'P', '2025-03-18'),
                  ('DX009', 'PAT006', 'ENC007', 'E78.5',  '10', 'AD', 'S', '2025-03-18'),
                  ('DX010', 'PAT007', 'ENC008', 'F32.1',  '10', 'AD', 'P', '2025-10-01'),
                  ('DX011', 'PAT008', 'ENC009', 'M54.5',  '10', 'AD', 'P', '2025-11-15'),
                  ('DX012', 'PAT001', 'ENC002', 'E11.65', '10', 'AD', 'P', '2025-08-10')
                ON CONFLICT ("DIAGNOSISID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 9. PROCEDURES
        # ──────────────────────────────────────────────────
        print("  [9/14] PROCEDURES...")
        await db.execute(
            text("""
                INSERT INTO "PROCEDURES"
                    ("PROCEDURESID", "PATID", "ENCOUNTERID", "PX_DATE", "PX", "PX_TYPE", "PX_SOURCE")
                VALUES
                  ('PX001', 'PAT001', 'ENC001', '2025-06-15', '99213', 'CH', 'BI'),
                  ('PX002', 'PAT002', 'ENC003', '2025-05-21', '31622', 'CH', 'BI'),
                  ('PX003', 'PAT003', 'ENC004', '2025-07-01', '76815', 'CH', 'BI'),
                  ('PX004', 'PAT004', 'ENC005', '2025-09-12', '27236', 'CH', 'BI'),
                  ('PX005', 'PAT006', 'ENC007', '2025-03-19', '93458', 'CH', 'BI'),
                  ('PX006', 'PAT008', 'ENC009', '2025-11-15', '99214', 'CH', 'BI')
                ON CONFLICT ("PROCEDURESID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 10. VITAL
        # ──────────────────────────────────────────────────
        print("  [10/14] VITAL...")
        await db.execute(
            text("""
                INSERT INTO "VITAL"
                    ("VITALID", "PATID", "ENCOUNTERID", "MEASURE_DATE", "MEASURE_TIME",
                     "HT", "WT", "SYSTOLIC", "DIASTOLIC", "ORIGINAL_BMI", "SMOKING", "TOBACCO")
                VALUES
                  ('VIT001', 'PAT001', 'ENC001', '2025-06-15', '09:10', 165.0, 72.0, 128.0, 82.0, 26.4, '04', '02'),
                  ('VIT002', 'PAT001', 'ENC002', '2025-08-10', '14:35', 165.0, 71.5, 124.0, 78.0, 26.3, '04', '02'),
                  ('VIT003', 'PAT002', 'ENC003', '2025-05-20', '10:15', 178.0, 95.0, 145.0, 92.0, 30.0, '01', '01'),
                  ('VIT004', 'PAT003', 'ENC004', '2025-07-01', '08:10', 160.0, 68.0, 110.0, 70.0, 26.6, '04', '02'),
                  ('VIT005', 'PAT004', 'ENC005', '2025-09-12', '16:10', 175.0, 82.0, 138.0, 88.0, 26.8, '02', '01'),
                  ('VIT006', 'PAT005', 'ENC006', '2025-04-05', '11:10', 155.0, 55.0, 105.0, 68.0, 22.9, '04', '02'),
                  ('VIT007', 'PAT006', 'ENC007', '2025-03-18', '09:40', 170.0, 88.0, 152.0, 96.0, 30.4, '03', '01'),
                  ('VIT008', 'PAT007', 'ENC008', '2025-10-01', '13:10', 168.0, 65.0, 118.0, 74.0, 23.0, '04', '02'),
                  ('VIT009', 'PAT008', 'ENC009', '2025-11-15', '07:50', 180.0, 90.0, 130.0, 84.0, 27.8, '04', '02'),
                  ('VIT010', 'PAT010', NULL,      '2025-02-01', '10:00', 172.0, 78.0, 142.0, 90.0, 26.4, '01', '01')
                ON CONFLICT ("VITALID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 11. LAB_RESULT_CM
        # ──────────────────────────────────────────────────
        print("  [11/14] LAB_RESULT_CM...")
        await db.execute(
            text("""
                INSERT INTO "LAB_RESULT_CM"
                    ("LAB_RESULT_CM_ID", "PATID", "ENCOUNTERID", "LAB_LOINC",
                     "RESULT_NUM", "RESULT_UNIT", "RESULT_QUAL", "RESULT_DATE",
                     "RAW_LAB_NAME", "RAW_RESULT", "ABN_IND")
                VALUES
                  ('LAB001', 'PAT001', 'ENC001', '4548-4',  7.2, '%', 'NI', '2025-06-15', 'Hemoglobin A1c', '7.2', 'AH'),
                  ('LAB002', 'PAT001', 'ENC001', '2345-7',  95.0, 'mg/dL', 'NI', '2025-06-15', 'Glucose', '95', 'NI'),
                  ('LAB003', 'PAT001', 'ENC002', '4548-4',  6.8, '%', 'NI', '2025-08-10', 'Hemoglobin A1c', '6.8', 'NI'),
                  ('LAB004', 'PAT002', 'ENC003', '2093-3',  245.0, 'mg/dL', 'NI', '2025-05-20', 'Total Cholesterol', '245', 'AH'),
                  ('LAB005', 'PAT002', 'ENC003', '718-7',   12.1, 'g/dL', 'NI', '2025-05-20', 'Hemoglobin', '12.1', 'AL'),
                  ('LAB006', 'PAT003', 'ENC004', '2160-0',  0.8, 'mg/dL', 'NI', '2025-07-01', 'Creatinine', '0.8', 'NI'),
                  ('LAB007', 'PAT004', 'ENC005', '6690-2',  11200.0, '/uL', 'NI', '2025-09-12', 'WBC', '11200', 'AH'),
                  ('LAB008', 'PAT006', 'ENC007', '2085-9',  38.0, 'mg/dL', 'NI', '2025-03-18', 'HDL Cholesterol', '38', 'AL'),
                  ('LAB009', 'PAT006', 'ENC007', '13457-7', 185.0, 'mg/dL', 'NI', '2025-03-18', 'LDL Cholesterol', '185', 'AH'),
                  ('LAB010', 'PAT008', 'ENC009', '2160-0',  1.1, 'mg/dL', 'NI', '2025-11-15', 'Creatinine', '1.1', 'NI')
                ON CONFLICT ("LAB_RESULT_CM_ID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 12. PRESCRIBING & DISPENSING & CONDITION
        # ──────────────────────────────────────────────────
        print("  [12/14] PRESCRIBING, DISPENSING, CONDITION...")
        await db.execute(
            text("""
                INSERT INTO "PRESCRIBING"
                    ("PRESCRIBINGID", "PATID", "ENCOUNTERID", "RX_ORDER_DATE",
                     "RXNORM_CUI", "RX_DAYS_SUPPLY", "RX_REFILLS", "RAW_RX_MED_NAME",
                     "RX_PROVIDERID", "RX_SOURCE")
                VALUES
                  ('RX001', 'PAT001', 'ENC001', '2025-06-15', '860975',  90, 3, 'Metformin 500mg', 'PROV001', 'OD'),
                  ('RX002', 'PAT001', 'ENC001', '2025-06-15', '197361',  30, 2, 'Lisinopril 10mg', 'PROV001', 'OD'),
                  ('RX003', 'PAT002', 'ENC003', '2025-05-20', '896188',  30, 0, 'Albuterol Inhaler', 'PROV001', 'OD'),
                  ('RX004', 'PAT004', 'ENC005', '2025-09-12', '1049502', 14, 0, 'Oxycodone 5mg', 'PROV001', 'OD'),
                  ('RX005', 'PAT006', 'ENC007', '2025-03-18', '259255',  90, 3, 'Atorvastatin 40mg', 'PROV003', 'OD'),
                  ('RX006', 'PAT007', 'ENC008', '2025-10-01', '312938',  30, 5, 'Sertraline 50mg', 'PROV001', 'OD')
                ON CONFLICT ("PRESCRIBINGID") DO NOTHING
            """)
        )

        await db.execute(
            text("""
                INSERT INTO "DISPENSING"
                    ("DISPENSINGID", "PATID", "PRESCRIBINGID", "DISPENSE_DATE",
                     "NDC", "DISPENSE_SUP", "DISPENSE_AMT", "DISPENSE_SOURCE")
                VALUES
                  ('DISP001', 'PAT001', 'RX001', '2025-06-16', '00093-7214', 90, 90.0, 'OD'),
                  ('DISP002', 'PAT001', 'RX002', '2025-06-16', '00093-7210', 30, 30.0, 'OD'),
                  ('DISP003', 'PAT006', 'RX005', '2025-03-19', '00071-0155', 90, 90.0, 'OD')
                ON CONFLICT ("DISPENSINGID") DO NOTHING
            """)
        )

        await db.execute(
            text("""
                INSERT INTO "CONDITION"
                    ("CONDITIONID", "PATID", "ENCOUNTERID", "ONSET_DATE",
                     "CONDITION", "CONDITION_TYPE", "CONDITION_STATUS", "CONDITION_SOURCE")
                VALUES
                  ('COND001', 'PAT001', 'ENC001', '2020-03-01', 'E11.9',  '10', 'AC', 'HC'),
                  ('COND002', 'PAT001', 'ENC001', '2018-06-15', 'I10',    '10', 'AC', 'HC'),
                  ('COND003', 'PAT002', 'ENC003', '2015-09-10', 'J44.1',  '10', 'AC', 'HC'),
                  ('COND004', 'PAT003', 'ENC004', '2025-07-01', 'O09.91', '10', 'AC', 'HC'),
                  ('COND005', 'PAT006', 'ENC007', '2010-11-20', 'I25.10', '10', 'AC', 'HC'),
                  ('COND006', 'PAT007', 'ENC008', '2024-02-15', 'F32.1',  '10', 'AC', 'HC')
                ON CONFLICT ("CONDITIONID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 13. DEATH, ENROLLMENT, IMMUNIZATION, HARVEST
        # ──────────────────────────────────────────────────
        print("  [13/14] DEATH, ENROLLMENT, IMMUNIZATION, HARVEST...")
        await db.execute(
            text("""
                INSERT INTO "DEATH" ("PATID", "DEATH_DATE", "DEATH_SOURCE", "DEATH_MATCH_CONFIDENCE")
                VALUES ('PAT002', '2025-01-10', 'L', 'E')
                ON CONFLICT ("PATID") DO NOTHING
            """)
        )

        await db.execute(
            text("""
                INSERT INTO "ENROLLMENT" ("PATID", "ENR_START_DATE", "ENR_BASIS", "ENR_END_DATE", "CHART")
                VALUES
                  ('PAT001', '2020-01-01', 'I', NULL, 'Y'),
                  ('PAT002', '2015-06-01', 'I', '2025-01-10', 'Y'),
                  ('PAT003', '2022-03-15', 'I', NULL, 'Y'),
                  ('PAT004', '2019-09-01', 'I', NULL, 'N'),
                  ('PAT005', '2023-01-01', 'I', NULL, 'Y'),
                  ('PAT006', '2010-01-01', 'I', NULL, 'Y'),
                  ('PAT007', '2024-01-01', 'I', NULL, 'Y'),
                  ('PAT008', '2021-07-01', 'I', NULL, 'N'),
                  ('PAT010', '2005-01-01', 'I', NULL, 'Y')
                ON CONFLICT DO NOTHING
            """)
        )

        await db.execute(
            text("""
                INSERT INTO "IMMUNIZATION"
                    ("IMMUNIZATIONID", "PATID", "VX_ADMIN_DATE", "VX_CODE_TYPE",
                     "VX_CODE", "VX_STATUS", "VX_SOURCE", "RAW_VX_NAME")
                VALUES
                  ('IMM001', 'PAT001', '2025-01-15', 'CX', '208', 'CP', 'OD', 'COVID-19 mRNA Vaccine'),
                  ('IMM002', 'PAT001', '2024-10-01', 'CX', '197', 'CP', 'OD', 'Influenza Vaccine'),
                  ('IMM003', 'PAT003', '2025-05-10', 'CX', '208', 'CP', 'OD', 'COVID-19 mRNA Vaccine'),
                  ('IMM004', 'PAT005', '2024-09-15', 'CX', '197', 'CP', 'OD', 'Influenza Vaccine'),
                  ('IMM005', 'PAT007', '2025-02-20', 'CX', '208', 'CP', 'OD', 'COVID-19 mRNA Vaccine')
                ON CONFLICT ("IMMUNIZATIONID") DO NOTHING
            """)
        )

        await db.execute(
            text("""
                INSERT INTO "HARVEST"
                    ("NETWORKID", "NETWORK_NAME", "DATAMARTID", "DATAMART_NAME",
                     "CDM_VERSION", "DATAMART_CLAIMS", "DATAMART_EHR",
                     "REFRESH_DEMOGRAPHIC_DATE", "REFRESH_ENCOUNTER_DATE", "REFRESH_DIAGNOSIS_DATE")
                VALUES
                  ('ENT01', 'Enternal Network', 'DM01', 'Enternal DM',
                   '7.0', 'N', 'Y', '2025-12-01', '2025-12-01', '2025-12-01')
                ON CONFLICT ("NETWORKID") DO NOTHING
            """)
        )

        # ──────────────────────────────────────────────────
        # 14. Platform tables: saved queries, dashboards, audit, chat
        # ──────────────────────────────────────────────────
        print("  [14/14] Platform data (queries, dashboards, audit, chat)...")

        # Saved queries — use bind params for sql to avoid : conflicts
        saved_queries = [
            ("Patient Demographics", "List all patients with demographics",
             'SELECT "PATID", "BIRTH_DATE", "SEX", "RACE", "HISPANIC" FROM "DEMOGRAPHIC" ORDER BY "PATID"'),
            ("Encounter Summary", "Count encounters by type",
             'SELECT "ENC_TYPE", COUNT(*) as cnt FROM "ENCOUNTER" GROUP BY "ENC_TYPE" ORDER BY cnt DESC'),
            ("Diagnosis Frequency", "Top 10 diagnoses",
             'SELECT "DX", COUNT(*) as cnt FROM "DIAGNOSIS" GROUP BY "DX" ORDER BY cnt DESC LIMIT 10'),
            ("Abnormal Labs", "Lab results with abnormal indicators",
             """SELECT l."PATID", l."RAW_LAB_NAME", l."RESULT_NUM", l."RESULT_UNIT", l."ABN_IND" FROM "LAB_RESULT_CM" l WHERE l."ABN_IND" IN ('AH', 'AL') ORDER BY l."RESULT_DATE" DESC"""),
        ]
        for name, desc, sql in saved_queries:
            await db.execute(
                text("""
                    INSERT INTO saved_queries (user_id, name, description, sql, created_at, updated_at)
                    VALUES (:uid, :name, :desc, :sql, NOW(), NOW())
                """),
                {"uid": admin_id, "name": name, "desc": desc, "sql": sql},
            )

        # Dashboards + widgets
        result = await db.execute(
            text("""
                INSERT INTO dashboards (user_id, name, description, is_public, created_at, updated_at)
                VALUES
                  (:admin_id, 'Population Overview', 'Key metrics for the patient population', true, NOW(), NOW()),
                  (:admin_id, 'Clinical Quality', 'Quality measures and outcomes tracking', false, NOW(), NOW())
                RETURNING id
            """),
            {"admin_id": admin_id},
        )
        dash_ids = [r[0] for r in result.fetchall()]

        widgets = [
            (dash_ids[0], "Total Patients", "kpi",
             'SELECT COUNT(*) as value FROM "DEMOGRAPHIC"',
             '{"label":"Patients"}', 0, 0, 3, 2),
            (dash_ids[0], "Total Encounters", "kpi",
             'SELECT COUNT(*) as value FROM "ENCOUNTER"',
             '{"label":"Encounters"}', 3, 0, 3, 2),
            (dash_ids[0], "Encounters by Type", "bar",
             'SELECT "ENC_TYPE" as category, COUNT(*) as value FROM "ENCOUNTER" GROUP BY "ENC_TYPE"',
             '{"xAxis":"category","yAxis":"value"}', 0, 2, 6, 4),
            (dash_ids[0], "Sex Distribution", "pie",
             'SELECT "SEX" as category, COUNT(*) as value FROM "DEMOGRAPHIC" GROUP BY "SEX"',
             '{"label":"category","value":"value"}', 6, 0, 6, 4),
            (dash_ids[1], "Abnormal Lab Rate", "kpi",
             """SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE "ABN_IND" IN ('AH','AL')) / NULLIF(COUNT(*),0), 1) as value FROM "LAB_RESULT_CM\"""",
             '{"label":"Abnormal %","suffix":"%"}', 0, 0, 4, 2),
            (dash_ids[1], "Diagnoses per Patient", "bar",
             'SELECT "PATID" as category, COUNT(*) as value FROM "DIAGNOSIS" GROUP BY "PATID" ORDER BY value DESC LIMIT 10',
             '{"xAxis":"category","yAxis":"value"}', 0, 2, 12, 4),
        ]
        for did, title, wtype, sql, cfg, gx, gy, gw, gh in widgets:
            await db.execute(
                text("""
                    INSERT INTO dashboard_widgets
                        (dashboard_id, title, widget_type, sql, config_json,
                         grid_x, grid_y, grid_w, grid_h, created_at)
                    VALUES (:did, :title, :wtype, :sql, :cfg, :gx, :gy, :gw, :gh, NOW())
                """),
                {"did": did, "title": title, "wtype": wtype, "sql": sql,
                 "cfg": cfg, "gx": gx, "gy": gy, "gw": gw, "gh": gh},
            )

        # Audit log entries — use bind params for details to avoid : conflicts
        audit_entries = [
            ("login", "auth", None, '{"method":"password"}', "2 hours"),
            ("query.execute", "query", None, '{"sql":"SELECT * FROM DEMOGRAPHIC LIMIT 10"}', "1 hour 55 minutes"),
            ("integration.create", "integration", "1", '{"type":"fhir","name":"HAPI FHIR"}', "1 hour 50 minutes"),
            ("ingestion.trigger", "ingestion_run", "1", '{"integration_id":1}', "1 hour 45 minutes"),
            ("dashboard.create", "dashboard", "1", '{"name":"Population Overview"}', "1 hour"),
            ("export.csv", "export", None, '{"query":"Patient Demographics","rows":10}', "30 minutes"),
            ("login", "auth", None, '{"method":"password"}', "10 minutes"),
            ("query.execute", "query", None, '{"sql":"SELECT COUNT(*) FROM ENCOUNTER"}', "5 minutes"),
        ]
        for action, res_type, res_id, details, interval in audit_entries:
            await db.execute(
                text(f"""
                    INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, ip_address, timestamp)
                    VALUES (:uid, :action, :res_type, :res_id, :details, '127.0.0.1', NOW() - INTERVAL '{interval}')
                """),
                {"uid": admin_id, "action": action, "res_type": res_type, "res_id": res_id, "details": details},
            )

        # Chat session + messages
        result = await db.execute(
            text("""
                INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
                VALUES (:admin_id, 'Patient analysis questions', NOW(), NOW())
                RETURNING id
            """),
            {"admin_id": admin_id},
        )
        session_id = result.scalar_one()

        chat_msgs = [
            ("user", "How many patients have diabetes?", None, "5 minutes"),
            ("assistant",
             "Based on the diagnosis data, there are 2 patients with Type 2 diabetes (ICD-10 codes E11.x).",
             "SELECT COUNT(DISTINCT \"PATID\") FROM \"DIAGNOSIS\" WHERE \"DX\" LIKE 'E11%'",
             "4 minutes"),
            ("user", "What are their most recent HbA1c levels?", None, "3 minutes"),
            ("assistant",
             "Patient PAT001 has an HbA1c of 6.8% (most recent on 2025-08-10), showing improvement from 7.2% in June.",
             "SELECT l.\"PATID\", l.\"RESULT_NUM\", l.\"RESULT_DATE\" FROM \"LAB_RESULT_CM\" l WHERE l.\"LAB_LOINC\" = '4548-4' ORDER BY l.\"RESULT_DATE\" DESC",
             "2 minutes"),
        ]
        for role, content, sql_gen, interval in chat_msgs:
            await db.execute(
                text(f"""
                    INSERT INTO chat_messages (session_id, role, content, sql_generated, created_at)
                    VALUES (:sid, :role, :content, :sql_gen, NOW() - INTERVAL '{interval}')
                """),
                {"sid": session_id, "role": role, "content": content, "sql_gen": sql_gen},
            )

        await db.commit()
        print("[seed_sample_data] Done! Sample data inserted successfully.")

        # Print summary
        tables = [
            "users", "integrations", "ingestion_runs", "quarantine",
            '"DEMOGRAPHIC"', '"ENCOUNTER"', '"DIAGNOSIS"', '"PROCEDURES"',
            '"VITAL"', '"LAB_RESULT_CM"', '"PRESCRIBING"', '"DISPENSING"',
            '"CONDITION"', '"DEATH"', '"ENROLLMENT"', '"IMMUNIZATION"',
            '"PROVIDER"', '"HARVEST"',
            "saved_queries", "dashboards", "dashboard_widgets",
            "audit_log", "chat_sessions", "chat_messages",
        ]
        print("\n  Table row counts:")
        for t in tables:
            r = await db.execute(text(f"SELECT COUNT(*) FROM {t}"))
            print(f"    {t:30s} {r.scalar():>5}")


if __name__ == "__main__":
    asyncio.run(seed())
