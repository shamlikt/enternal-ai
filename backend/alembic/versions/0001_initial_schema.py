"""initial schema - PCORnet CDM v7.0 + platform tables

Revision ID: 0001
Revises:
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Platform Tables ---
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'analyst', 'viewer', name='role'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table('saved_queries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sql', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_saved_queries_user_id', 'saved_queries', ['user_id'])

    op.create_table('query_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sql', sa.Text(), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('execution_ms', sa.Integer(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_query_history_user_id', 'query_history', ['user_id'])

    op.create_table('query_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('history_id', sa.Integer(), nullable=False),
        sa.Column('result_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['history_id'], ['query_history.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_query_results_history_id', 'query_results', ['history_id'])

    op.create_table('chat_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])

    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sql_generated', sa.Text(), nullable=True),
        sa.Column('result_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])

    op.create_table('dashboards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_dashboards_user_id', 'dashboards', ['user_id'])

    op.create_table('dashboard_widgets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dashboard_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('widget_type', sa.String(50), nullable=False),
        sa.Column('sql', sa.Text(), nullable=False),
        sa.Column('config_json', sa.Text(), nullable=True),
        sa.Column('grid_x', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('grid_y', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('grid_w', sa.Integer(), nullable=False, server_default=sa.text('6')),
        sa.Column('grid_h', sa.Integer(), nullable=False, server_default=sa.text('4')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_dashboard_widgets_dashboard_id', 'dashboard_widgets', ['dashboard_id'])

    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_timestamp', 'audit_log', ['timestamp'])

    # --- PCORnet CDM v7.0 Tables ---
    op.create_table('DEMOGRAPHIC',
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('BIRTH_DATE', sa.String(10), nullable=True),
        sa.Column('BIRTH_TIME', sa.String(5), nullable=True),
        sa.Column('SEX', sa.String(2), nullable=True),
        sa.Column('SEXUAL_ORIENTATION', sa.String(2), nullable=True),
        sa.Column('GENDER_IDENTITY', sa.String(2), nullable=True),
        sa.Column('HISPANIC', sa.String(2), nullable=True),
        sa.Column('RACE', sa.String(2), nullable=True),
        sa.Column('BIOBANK_FLAG', sa.String(1), nullable=True),
        sa.Column('PAT_PREF_LANGUAGE_SPOKEN', sa.String(3), nullable=True),
        sa.Column('RAW_SEX', sa.String(50), nullable=True),
        sa.Column('RAW_SEXUAL_ORIENTATION', sa.String(50), nullable=True),
        sa.Column('RAW_GENDER_IDENTITY', sa.String(50), nullable=True),
        sa.Column('RAW_HISPANIC', sa.String(50), nullable=True),
        sa.Column('RAW_RACE', sa.String(50), nullable=True),
        sa.Column('RAW_PAT_PREF_LANGUAGE_SPOKEN', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('PATID'),
    )

    op.create_table('ENCOUNTER',
        sa.Column('ENCOUNTERID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ADMIT_DATE', sa.String(10), nullable=True),
        sa.Column('ADMIT_TIME', sa.String(5), nullable=True),
        sa.Column('DISCHARGE_DATE', sa.String(10), nullable=True),
        sa.Column('DISCHARGE_TIME', sa.String(5), nullable=True),
        sa.Column('PROVIDERID', sa.String(50), nullable=True),
        sa.Column('FACILITY_LOCATION', sa.String(3), nullable=True),
        sa.Column('ENC_TYPE', sa.String(2), nullable=True),
        sa.Column('FACILITYID', sa.String(50), nullable=True),
        sa.Column('DISCHARGE_DISPOSITION', sa.String(2), nullable=True),
        sa.Column('DISCHARGE_STATUS', sa.String(2), nullable=True),
        sa.Column('DRG', sa.String(3), nullable=True),
        sa.Column('DRG_TYPE', sa.String(2), nullable=True),
        sa.Column('ADMITTING_SOURCE', sa.String(2), nullable=True),
        sa.Column('PAYER_TYPE_PRIMARY', sa.String(3), nullable=True),
        sa.Column('PAYER_TYPE_SECONDARY', sa.String(3), nullable=True),
        sa.Column('FACILITY_TYPE', sa.String(2), nullable=True),
        sa.Column('RAW_SITEID', sa.String(50), nullable=True),
        sa.Column('RAW_ENC_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_DISCHARGE_DISPOSITION', sa.String(50), nullable=True),
        sa.Column('RAW_DISCHARGE_STATUS', sa.String(50), nullable=True),
        sa.Column('RAW_DRG_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_ADMITTING_SOURCE', sa.String(50), nullable=True),
        sa.Column('RAW_PAYER_TYPE_PRIMARY', sa.String(50), nullable=True),
        sa.Column('RAW_PAYER_TYPE_SECONDARY', sa.String(50), nullable=True),
        sa.Column('RAW_FACILITY_TYPE', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('ENCOUNTERID'),
    )
    op.create_index('ix_ENCOUNTER_PATID', 'ENCOUNTER', ['PATID'])

    op.create_table('DIAGNOSIS',
        sa.Column('DIAGNOSISID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('ENC_TYPE', sa.String(2), nullable=True),
        sa.Column('ADMIT_DATE', sa.String(10), nullable=True),
        sa.Column('PROVIDERID', sa.String(50), nullable=True),
        sa.Column('DX', sa.String(18), nullable=True),
        sa.Column('DX_TYPE', sa.String(2), nullable=True),
        sa.Column('DX_SOURCE', sa.String(2), nullable=True),
        sa.Column('DX_ORIGIN', sa.String(2), nullable=True),
        sa.Column('PDX', sa.String(2), nullable=True),
        sa.Column('DX_POA', sa.String(2), nullable=True),
        sa.Column('RAW_DX', sa.String(50), nullable=True),
        sa.Column('RAW_DX_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_DX_SOURCE', sa.String(50), nullable=True),
        sa.Column('RAW_DX_ORIGIN', sa.String(50), nullable=True),
        sa.Column('RAW_PDX', sa.String(50), nullable=True),
        sa.Column('RAW_DX_POA', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('DIAGNOSISID'),
    )
    op.create_index('ix_DIAGNOSIS_PATID', 'DIAGNOSIS', ['PATID'])
    op.create_index('ix_DIAGNOSIS_ENCOUNTERID', 'DIAGNOSIS', ['ENCOUNTERID'])

    op.create_table('PROCEDURES',
        sa.Column('PROCEDURESID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('ENC_TYPE', sa.String(2), nullable=True),
        sa.Column('ADMIT_DATE', sa.String(10), nullable=True),
        sa.Column('PROVIDERID', sa.String(50), nullable=True),
        sa.Column('PX_DATE', sa.String(10), nullable=True),
        sa.Column('PX', sa.String(11), nullable=True),
        sa.Column('PX_TYPE', sa.String(2), nullable=True),
        sa.Column('PX_SOURCE', sa.String(2), nullable=True),
        sa.Column('PPX', sa.String(2), nullable=True),
        sa.Column('RAW_PX', sa.String(50), nullable=True),
        sa.Column('RAW_PX_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_PPX', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PROCEDURESID'),
    )
    op.create_index('ix_PROCEDURES_PATID', 'PROCEDURES', ['PATID'])
    op.create_index('ix_PROCEDURES_ENCOUNTERID', 'PROCEDURES', ['ENCOUNTERID'])

    op.create_table('VITAL',
        sa.Column('VITALID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('MEASURE_DATE', sa.String(10), nullable=True),
        sa.Column('MEASURE_TIME', sa.String(5), nullable=True),
        sa.Column('VITAL_SOURCE', sa.String(2), nullable=True),
        sa.Column('HT', sa.Float(), nullable=True),
        sa.Column('WT', sa.Float(), nullable=True),
        sa.Column('DIASTOLIC', sa.Float(), nullable=True),
        sa.Column('SYSTOLIC', sa.Float(), nullable=True),
        sa.Column('ORIGINAL_BMI', sa.Float(), nullable=True),
        sa.Column('BP_POSITION', sa.String(2), nullable=True),
        sa.Column('SMOKING', sa.String(2), nullable=True),
        sa.Column('TOBACCO', sa.String(2), nullable=True),
        sa.Column('TOBACCO_TYPE', sa.String(2), nullable=True),
        sa.Column('RAW_DIASTOLIC', sa.String(50), nullable=True),
        sa.Column('RAW_SYSTOLIC', sa.String(50), nullable=True),
        sa.Column('RAW_BP_POSITION', sa.String(50), nullable=True),
        sa.Column('RAW_SMOKING', sa.String(50), nullable=True),
        sa.Column('RAW_TOBACCO', sa.String(50), nullable=True),
        sa.Column('RAW_TOBACCO_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_VITAL_SOURCE', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('VITALID'),
    )
    op.create_index('ix_VITAL_PATID', 'VITAL', ['PATID'])

    op.create_table('LAB_RESULT_CM',
        sa.Column('LAB_RESULT_CM_ID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('ACCESSION_ID', sa.String(50), nullable=True),
        sa.Column('LAB_LOINC', sa.String(10), nullable=True),
        sa.Column('LAB_RESULT_SOURCE', sa.String(2), nullable=True),
        sa.Column('LAB_LOINC_SOURCE', sa.String(2), nullable=True),
        sa.Column('PRIORITY', sa.String(2), nullable=True),
        sa.Column('RESULT_LOC', sa.String(2), nullable=True),
        sa.Column('LAB_PX', sa.String(11), nullable=True),
        sa.Column('LAB_PX_TYPE', sa.String(2), nullable=True),
        sa.Column('LAB_ORDER_DATE', sa.String(10), nullable=True),
        sa.Column('SPECIMEN_DATE', sa.String(10), nullable=True),
        sa.Column('SPECIMEN_TIME', sa.String(5), nullable=True),
        sa.Column('RESULT_DATE', sa.String(10), nullable=True),
        sa.Column('RESULT_TIME', sa.String(5), nullable=True),
        sa.Column('RESULT_QUAL', sa.String(2), nullable=True),
        sa.Column('RESULT_SNOMED', sa.String(50), nullable=True),
        sa.Column('RESULT_NUM', sa.Float(), nullable=True),
        sa.Column('RESULT_MODIFIER', sa.String(2), nullable=True),
        sa.Column('RESULT_UNIT', sa.String(11), nullable=True),
        sa.Column('NORM_RANGE_LOW', sa.String(10), nullable=True),
        sa.Column('NORM_MODIFIER_LOW', sa.String(2), nullable=True),
        sa.Column('NORM_RANGE_HIGH', sa.String(10), nullable=True),
        sa.Column('NORM_MODIFIER_HIGH', sa.String(2), nullable=True),
        sa.Column('ABN_IND', sa.String(2), nullable=True),
        sa.Column('RAW_LAB_NAME', sa.String(100), nullable=True),
        sa.Column('RAW_LAB_CODE', sa.String(50), nullable=True),
        sa.Column('RAW_PANEL', sa.String(100), nullable=True),
        sa.Column('RAW_RESULT', sa.String(50), nullable=True),
        sa.Column('RAW_UNIT', sa.String(50), nullable=True),
        sa.Column('RAW_ORDER_DEPT', sa.String(50), nullable=True),
        sa.Column('RAW_FACILITY_CODE', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('LAB_RESULT_CM_ID'),
    )
    op.create_index('ix_LAB_RESULT_CM_PATID', 'LAB_RESULT_CM', ['PATID'])

    op.create_table('PRESCRIBING',
        sa.Column('PRESCRIBINGID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('RX_PROVIDERID', sa.String(50), nullable=True),
        sa.Column('RX_ORDER_DATE', sa.String(10), nullable=True),
        sa.Column('RX_ORDER_TIME', sa.String(5), nullable=True),
        sa.Column('RX_START_DATE', sa.String(10), nullable=True),
        sa.Column('RX_END_DATE', sa.String(10), nullable=True),
        sa.Column('RX_QUANTITY', sa.Float(), nullable=True),
        sa.Column('RX_QUANTITY_UNIT', sa.String(50), nullable=True),
        sa.Column('RX_REFILLS', sa.Integer(), nullable=True),
        sa.Column('RX_DAYS_SUPPLY', sa.Integer(), nullable=True),
        sa.Column('RX_FREQUENCY', sa.String(2), nullable=True),
        sa.Column('RX_PRN_FLAG', sa.String(1), nullable=True),
        sa.Column('RX_ROUTE', sa.String(2), nullable=True),
        sa.Column('RX_BASIS', sa.String(2), nullable=True),
        sa.Column('RXNORM_CUI', sa.String(8), nullable=True),
        sa.Column('RX_SOURCE', sa.String(2), nullable=True),
        sa.Column('RX_DISPENSE_AS_WRITTEN', sa.String(2), nullable=True),
        sa.Column('RAW_RX_MED_NAME', sa.String(100), nullable=True),
        sa.Column('RAW_RX_FREQUENCY', sa.String(50), nullable=True),
        sa.Column('RAW_RX_QUANTITY', sa.String(50), nullable=True),
        sa.Column('RAW_RX_ROUTE', sa.String(50), nullable=True),
        sa.Column('RAW_RX_BASIS', sa.String(50), nullable=True),
        sa.Column('RAW_RXNORM_CUI', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PRESCRIBINGID'),
    )
    op.create_index('ix_PRESCRIBING_PATID', 'PRESCRIBING', ['PATID'])

    op.create_table('DISPENSING',
        sa.Column('DISPENSINGID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('PRESCRIBINGID', sa.String(50), nullable=True),
        sa.Column('DISPENSE_DATE', sa.String(10), nullable=True),
        sa.Column('NDC', sa.String(11), nullable=True),
        sa.Column('DISPENSE_SUP', sa.Integer(), nullable=True),
        sa.Column('DISPENSE_AMT', sa.Float(), nullable=True),
        sa.Column('DISPENSE_DOSE_DISP', sa.Float(), nullable=True),
        sa.Column('DISPENSE_DOSE_DISP_UNIT', sa.String(50), nullable=True),
        sa.Column('DISPENSE_ROUTE', sa.String(2), nullable=True),
        sa.Column('DISPENSE_SOURCE', sa.String(2), nullable=True),
        sa.Column('RAW_NDC', sa.String(50), nullable=True),
        sa.Column('RAW_DISPENSE_DOSE_DISP', sa.String(50), nullable=True),
        sa.Column('RAW_DISPENSE_DOSE_DISP_UNIT', sa.String(50), nullable=True),
        sa.Column('RAW_DISPENSE_ROUTE', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.ForeignKeyConstraint(['PRESCRIBINGID'], ['PRESCRIBING.PRESCRIBINGID']),
        sa.PrimaryKeyConstraint('DISPENSINGID'),
    )
    op.create_index('ix_DISPENSING_PATID', 'DISPENSING', ['PATID'])

    op.create_table('CONDITION',
        sa.Column('CONDITIONID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('REPORT_DATE', sa.String(10), nullable=True),
        sa.Column('RESOLVE_DATE', sa.String(10), nullable=True),
        sa.Column('ONSET_DATE', sa.String(10), nullable=True),
        sa.Column('CONDITION_STATUS', sa.String(2), nullable=True),
        sa.Column('CONDITION', sa.String(18), nullable=True),
        sa.Column('CONDITION_TYPE', sa.String(2), nullable=True),
        sa.Column('CONDITION_SOURCE', sa.String(2), nullable=True),
        sa.Column('RAW_CONDITION_STATUS', sa.String(50), nullable=True),
        sa.Column('RAW_CONDITION', sa.String(50), nullable=True),
        sa.Column('RAW_CONDITION_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_CONDITION_SOURCE', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('CONDITIONID'),
    )
    op.create_index('ix_CONDITION_PATID', 'CONDITION', ['PATID'])

    op.create_table('DEATH',
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('DEATH_DATE', sa.String(10), nullable=True),
        sa.Column('DEATH_DATE_IMPUTE', sa.String(2), nullable=True),
        sa.Column('DEATH_SOURCE', sa.String(2), nullable=True),
        sa.Column('DEATH_MATCH_CONFIDENCE', sa.String(2), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PATID'),
    )

    op.create_table('DEATH_CAUSE',
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('DEATH_CAUSE', sa.String(8), nullable=False),
        sa.Column('DEATH_CAUSE_CODE', sa.String(2), nullable=False),
        sa.Column('DEATH_CAUSE_TYPE', sa.String(2), nullable=False),
        sa.Column('DEATH_CAUSE_SOURCE', sa.String(2), nullable=False),
        sa.Column('DEATH_CAUSE_CONFIDENCE', sa.String(2), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PATID', 'DEATH_CAUSE', 'DEATH_CAUSE_CODE', 'DEATH_CAUSE_TYPE', 'DEATH_CAUSE_SOURCE'),
    )

    op.create_table('ENROLLMENT',
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENR_START_DATE', sa.String(10), nullable=False),
        sa.Column('ENR_BASIS', sa.String(1), nullable=False),
        sa.Column('ENR_END_DATE', sa.String(10), nullable=True),
        sa.Column('CHART', sa.String(1), nullable=True),
        sa.Column('RAW_CHART', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PATID', 'ENR_START_DATE', 'ENR_BASIS'),
    )

    op.create_table('HARVEST',
        sa.Column('NETWORKID', sa.String(10), nullable=False),
        sa.Column('NETWORK_NAME', sa.String(20), nullable=True),
        sa.Column('DATAMARTID', sa.String(10), nullable=True),
        sa.Column('DATAMART_NAME', sa.String(20), nullable=True),
        sa.Column('DATAMART_PLATFORM', sa.String(2), nullable=True),
        sa.Column('CDM_VERSION', sa.String(6), nullable=True),
        sa.Column('DATAMART_CLAIMS', sa.String(1), nullable=True),
        sa.Column('DATAMART_EHR', sa.String(1), nullable=True),
        sa.Column('BIRTH_DATE_IMPOSED', sa.String(1), nullable=True),
        sa.Column('BIRTH_DATE_SHIFT', sa.Integer(), nullable=True),
        sa.Column('REFRESH_DEMOGRAPHIC_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_ENROLLMENT_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_ENCOUNTER_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_DIAGNOSIS_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_PROCEDURES_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_VITAL_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_DISPENSING_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_LAB_RESULT_CM_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_CONDITION_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_PRO_CM_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_PRESCRIBING_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_PCORNET_TRIAL_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_DEATH_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_DEATH_CAUSE_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_MED_ADMIN_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_OBS_GEN_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_LDS_ADDRESS_HISTORY_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_IMMUNIZATION_DATE', sa.String(10), nullable=True),
        sa.Column('REFRESH_OBS_CLIN_DATE', sa.String(10), nullable=True),
        sa.PrimaryKeyConstraint('NETWORKID'),
    )

    op.create_table('LDS_ADDRESS_HISTORY',
        sa.Column('ADDRESSID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ADDRESS_USE', sa.String(2), nullable=True),
        sa.Column('ADDRESS_TYPE', sa.String(2), nullable=True),
        sa.Column('ADDRESS_PREFERRED', sa.String(1), nullable=True),
        sa.Column('ADDRESS_CITY', sa.String(50), nullable=True),
        sa.Column('ADDRESS_STATE', sa.String(2), nullable=True),
        sa.Column('ADDRESS_ZIP5', sa.String(5), nullable=True),
        sa.Column('ADDRESS_ZIP9', sa.String(9), nullable=True),
        sa.Column('ADDRESS_COUNTY', sa.String(3), nullable=True),
        sa.Column('ADDRESS_PERIOD_START', sa.String(10), nullable=True),
        sa.Column('ADDRESS_PERIOD_END', sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('ADDRESSID'),
    )
    op.create_index('ix_LDS_ADDRESS_HISTORY_PATID', 'LDS_ADDRESS_HISTORY', ['PATID'])

    op.create_table('MED_ADMIN',
        sa.Column('MEDADMINID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('PRESCRIBINGID', sa.String(50), nullable=True),
        sa.Column('MEDADMIN_PROVIDERID', sa.String(50), nullable=True),
        sa.Column('MEDADMIN_START_DATE', sa.String(10), nullable=True),
        sa.Column('MEDADMIN_START_TIME', sa.String(5), nullable=True),
        sa.Column('MEDADMIN_STOP_DATE', sa.String(10), nullable=True),
        sa.Column('MEDADMIN_STOP_TIME', sa.String(5), nullable=True),
        sa.Column('MEDADMIN_TYPE', sa.String(2), nullable=True),
        sa.Column('MEDADMIN_CODE', sa.String(11), nullable=True),
        sa.Column('MEDADMIN_DOSE_ADMIN', sa.Float(), nullable=True),
        sa.Column('MEDADMIN_DOSE_ADMIN_UNIT', sa.String(50), nullable=True),
        sa.Column('MEDADMIN_ROUTE', sa.String(2), nullable=True),
        sa.Column('MEDADMIN_SOURCE', sa.String(2), nullable=True),
        sa.Column('RAW_MEDADMIN_MED_NAME', sa.String(100), nullable=True),
        sa.Column('RAW_MEDADMIN_CODE', sa.String(50), nullable=True),
        sa.Column('RAW_MEDADMIN_DOSE_ADMIN', sa.String(50), nullable=True),
        sa.Column('RAW_MEDADMIN_DOSE_ADMIN_UNIT', sa.String(50), nullable=True),
        sa.Column('RAW_MEDADMIN_ROUTE', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.ForeignKeyConstraint(['PRESCRIBINGID'], ['PRESCRIBING.PRESCRIBINGID']),
        sa.PrimaryKeyConstraint('MEDADMINID'),
    )
    op.create_index('ix_MED_ADMIN_PATID', 'MED_ADMIN', ['PATID'])

    op.create_table('OBS_CLIN',
        sa.Column('OBSCLINID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('OBSCLIN_PROVIDERID', sa.String(50), nullable=True),
        sa.Column('OBSCLIN_DATE', sa.String(10), nullable=True),
        sa.Column('OBSCLIN_TIME', sa.String(5), nullable=True),
        sa.Column('OBSCLIN_TYPE', sa.String(2), nullable=True),
        sa.Column('OBSCLIN_CODE', sa.String(18), nullable=True),
        sa.Column('OBSCLIN_RESULT_TEXT', sa.Text(), nullable=True),
        sa.Column('OBSCLIN_RESULT_SNOMED', sa.String(50), nullable=True),
        sa.Column('OBSCLIN_RESULT_NUM', sa.Float(), nullable=True),
        sa.Column('OBSCLIN_RESULT_MODIFIER', sa.String(2), nullable=True),
        sa.Column('OBSCLIN_RESULT_UNIT', sa.String(11), nullable=True),
        sa.Column('OBSCLIN_SOURCE', sa.String(2), nullable=True),
        sa.Column('OBSCLIN_ABN_IND', sa.String(2), nullable=True),
        sa.Column('RAW_OBSCLIN_NAME', sa.String(100), nullable=True),
        sa.Column('RAW_OBSCLIN_CODE', sa.String(50), nullable=True),
        sa.Column('RAW_OBSCLIN_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_OBSCLIN_RESULT', sa.String(50), nullable=True),
        sa.Column('RAW_OBSCLIN_MODIFIER', sa.String(50), nullable=True),
        sa.Column('RAW_OBSCLIN_UNIT', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('OBSCLINID'),
    )
    op.create_index('ix_OBS_CLIN_PATID', 'OBS_CLIN', ['PATID'])

    op.create_table('OBS_GEN',
        sa.Column('OBSGENID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('OBSGEN_PROVIDERID', sa.String(50), nullable=True),
        sa.Column('OBSGEN_DATE', sa.String(10), nullable=True),
        sa.Column('OBSGEN_TIME', sa.String(5), nullable=True),
        sa.Column('OBSGEN_TYPE', sa.String(2), nullable=True),
        sa.Column('OBSGEN_CODE', sa.String(18), nullable=True),
        sa.Column('OBSGEN_RESULT_TEXT', sa.Text(), nullable=True),
        sa.Column('OBSGEN_RESULT_NUM', sa.Float(), nullable=True),
        sa.Column('OBSGEN_RESULT_MODIFIER', sa.String(2), nullable=True),
        sa.Column('OBSGEN_RESULT_UNIT', sa.String(11), nullable=True),
        sa.Column('OBSGEN_TABLE_MODIFIED', sa.String(2), nullable=True),
        sa.Column('OBSGEN_ID_MODIFIED', sa.String(50), nullable=True),
        sa.Column('OBSGEN_SOURCE', sa.String(2), nullable=True),
        sa.Column('RAW_OBSGEN_NAME', sa.String(100), nullable=True),
        sa.Column('RAW_OBSGEN_CODE', sa.String(50), nullable=True),
        sa.Column('RAW_OBSGEN_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_OBSGEN_RESULT', sa.String(50), nullable=True),
        sa.Column('RAW_OBSGEN_UNIT', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('OBSGENID'),
    )
    op.create_index('ix_OBS_GEN_PATID', 'OBS_GEN', ['PATID'])

    op.create_table('PCORNET_TRIAL',
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('TRIALID', sa.String(20), nullable=False),
        sa.Column('PARTICIPANTID', sa.String(50), nullable=True),
        sa.Column('TRIAL_SITEID', sa.String(50), nullable=True),
        sa.Column('TRIAL_ENROLL_DATE', sa.String(10), nullable=True),
        sa.Column('TRIAL_END_DATE', sa.String(10), nullable=True),
        sa.Column('TRIAL_WITHDRAW_DATE', sa.String(10), nullable=True),
        sa.Column('TRIAL_INVITE_CODE', sa.String(20), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PATID', 'TRIALID'),
    )

    op.create_table('PRO_CM',
        sa.Column('PRO_CM_ID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('PRO_DATE', sa.String(10), nullable=True),
        sa.Column('PRO_TIME', sa.String(5), nullable=True),
        sa.Column('PRO_TYPE', sa.String(2), nullable=True),
        sa.Column('PRO_ITEM_NAME', sa.String(100), nullable=True),
        sa.Column('PRO_ITEM_LOINC', sa.String(10), nullable=True),
        sa.Column('PRO_RESPONSE_TEXT', sa.Text(), nullable=True),
        sa.Column('PRO_RESPONSE_NUM', sa.Float(), nullable=True),
        sa.Column('PRO_METHOD', sa.String(2), nullable=True),
        sa.Column('PRO_MODE', sa.String(2), nullable=True),
        sa.Column('PRO_CAT', sa.String(2), nullable=True),
        sa.Column('PRO_SOURCE', sa.String(2), nullable=True),
        sa.Column('PRO_MEASURE_NAME', sa.String(100), nullable=True),
        sa.Column('PRO_MEASURE_SEQ', sa.String(4), nullable=True),
        sa.Column('PRO_MEASURE_SCORE', sa.Float(), nullable=True),
        sa.Column('PRO_MEASURE_THETA', sa.Float(), nullable=True),
        sa.Column('PRO_MEASURE_SE', sa.Float(), nullable=True),
        sa.Column('PRO_MEASURE_COUNT_SCORED', sa.Integer(), nullable=True),
        sa.Column('PRO_MEASURE_LOINC', sa.String(10), nullable=True),
        sa.Column('PRO_MEASURE_VERSION', sa.String(20), nullable=True),
        sa.Column('PRO_MEASURE_AGREEMENT_STAT', sa.String(2), nullable=True),
        sa.Column('PRO_MEASURE_PAIRED_TEST_ID', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PRO_CM_ID'),
    )
    op.create_index('ix_PRO_CM_PATID', 'PRO_CM', ['PATID'])

    op.create_table('PROVIDER',
        sa.Column('PROVIDERID', sa.String(50), nullable=False),
        sa.Column('PROVIDER_SEX', sa.String(2), nullable=True),
        sa.Column('PROVIDER_SPECIALTY_PRIMARY', sa.String(3), nullable=True),
        sa.Column('PROVIDER_NPI', sa.String(10), nullable=True),
        sa.Column('RAW_PROVIDER_SPECIALTY_PRIMARY', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('PROVIDERID'),
    )

    op.create_table('IMMUNIZATION',
        sa.Column('IMMUNIZATIONID', sa.String(50), nullable=False),
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('ENCOUNTERID', sa.String(50), nullable=True),
        sa.Column('PROCEDURESID', sa.String(50), nullable=True),
        sa.Column('VX_PROVIDERID', sa.String(50), nullable=True),
        sa.Column('VX_RECORD_DATE', sa.String(10), nullable=True),
        sa.Column('VX_ADMIN_DATE', sa.String(10), nullable=True),
        sa.Column('VX_CODE_TYPE', sa.String(2), nullable=True),
        sa.Column('VX_CODE', sa.String(30), nullable=True),
        sa.Column('VX_STATUS', sa.String(2), nullable=True),
        sa.Column('VX_STATUS_REASON', sa.String(2), nullable=True),
        sa.Column('VX_SOURCE', sa.String(2), nullable=True),
        sa.Column('VX_DOSE_NUM', sa.Float(), nullable=True),
        sa.Column('VX_SERIES_COMPLETE', sa.String(2), nullable=True),
        sa.Column('VX_MANUFACTURER', sa.String(10), nullable=True),
        sa.Column('VX_LOT_NUM', sa.String(50), nullable=True),
        sa.Column('VX_EXP_DATE', sa.String(10), nullable=True),
        sa.Column('RAW_VX_NAME', sa.String(100), nullable=True),
        sa.Column('RAW_VX_CODE', sa.String(50), nullable=True),
        sa.Column('RAW_VX_CODE_TYPE', sa.String(50), nullable=True),
        sa.Column('RAW_VX_DOSE_NUM', sa.String(50), nullable=True),
        sa.Column('RAW_VX_SERIES_COMPLETE', sa.String(50), nullable=True),
        sa.Column('RAW_VX_STATUS', sa.String(50), nullable=True),
        sa.Column('RAW_VX_STATUS_REASON', sa.String(50), nullable=True),
        sa.Column('RAW_VX_SOURCE', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['ENCOUNTERID'], ['ENCOUNTER.ENCOUNTERID']),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.ForeignKeyConstraint(['PROCEDURESID'], ['PROCEDURES.PROCEDURESID']),
        sa.PrimaryKeyConstraint('IMMUNIZATIONID'),
    )
    op.create_index('ix_IMMUNIZATION_PATID', 'IMMUNIZATION', ['PATID'])

    op.create_table('HASH_TOKEN',
        sa.Column('PATID', sa.String(50), nullable=False),
        sa.Column('TOKEN_ENCRYPTION_KEY', sa.String(50), nullable=True),
        sa.Column('HASHED_ID', sa.String(256), nullable=True),
        sa.Column('TOKEN_APPEND', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['PATID'], ['DEMOGRAPHIC.PATID']),
        sa.PrimaryKeyConstraint('PATID'),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table('HASH_TOKEN')
    op.drop_index('ix_IMMUNIZATION_PATID', 'IMMUNIZATION')
    op.drop_table('IMMUNIZATION')
    op.drop_table('PROVIDER')
    op.drop_index('ix_PRO_CM_PATID', 'PRO_CM')
    op.drop_table('PRO_CM')
    op.drop_table('PCORNET_TRIAL')
    op.drop_index('ix_OBS_GEN_PATID', 'OBS_GEN')
    op.drop_table('OBS_GEN')
    op.drop_index('ix_OBS_CLIN_PATID', 'OBS_CLIN')
    op.drop_table('OBS_CLIN')
    op.drop_index('ix_MED_ADMIN_PATID', 'MED_ADMIN')
    op.drop_table('MED_ADMIN')
    op.drop_index('ix_LDS_ADDRESS_HISTORY_PATID', 'LDS_ADDRESS_HISTORY')
    op.drop_table('LDS_ADDRESS_HISTORY')
    op.drop_table('HARVEST')
    op.drop_table('ENROLLMENT')
    op.drop_table('DEATH_CAUSE')
    op.drop_table('DEATH')
    op.drop_index('ix_CONDITION_PATID', 'CONDITION')
    op.drop_table('CONDITION')
    op.drop_index('ix_DISPENSING_PATID', 'DISPENSING')
    op.drop_table('DISPENSING')
    op.drop_index('ix_PRESCRIBING_PATID', 'PRESCRIBING')
    op.drop_table('PRESCRIBING')
    op.drop_index('ix_LAB_RESULT_CM_PATID', 'LAB_RESULT_CM')
    op.drop_table('LAB_RESULT_CM')
    op.drop_index('ix_VITAL_PATID', 'VITAL')
    op.drop_table('VITAL')
    op.drop_index('ix_PROCEDURES_PATID', 'PROCEDURES')
    op.drop_index('ix_PROCEDURES_ENCOUNTERID', 'PROCEDURES')
    op.drop_table('PROCEDURES')
    op.drop_index('ix_DIAGNOSIS_PATID', 'DIAGNOSIS')
    op.drop_index('ix_DIAGNOSIS_ENCOUNTERID', 'DIAGNOSIS')
    op.drop_table('DIAGNOSIS')
    op.drop_index('ix_ENCOUNTER_PATID', 'ENCOUNTER')
    op.drop_table('ENCOUNTER')
    op.drop_table('DEMOGRAPHIC')
    op.drop_index('ix_audit_log_timestamp', 'audit_log')
    op.drop_index('ix_audit_log_action', 'audit_log')
    op.drop_index('ix_audit_log_user_id', 'audit_log')
    op.drop_table('audit_log')
    op.drop_index('ix_dashboard_widgets_dashboard_id', 'dashboard_widgets')
    op.drop_table('dashboard_widgets')
    op.drop_index('ix_dashboards_user_id', 'dashboards')
    op.drop_table('dashboards')
    op.drop_index('ix_chat_messages_session_id', 'chat_messages')
    op.drop_table('chat_messages')
    op.drop_index('ix_chat_sessions_user_id', 'chat_sessions')
    op.drop_table('chat_sessions')
    op.drop_index('ix_query_results_history_id', 'query_results')
    op.drop_table('query_results')
    op.drop_index('ix_query_history_user_id', 'query_history')
    op.drop_table('query_history')
    op.drop_index('ix_saved_queries_user_id', 'saved_queries')
    op.drop_table('saved_queries')
    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_username', 'users')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS role")
