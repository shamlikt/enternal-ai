// User and Auth
export type Role = "admin" | "analyst" | "viewer";

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Query
export interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  execution_time_ms: number;
  query_id?: string;
}

export interface SavedQuery {
  id: number;
  name: string;
  sql: string;
  description?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface QueryHistory {
  id: number;
  sql: string;
  status: "success" | "error";
  row_count?: number;
  execution_time_ms?: number;
  error_message?: string;
  created_at: string;
}

// Dashboard
export type WidgetType =
  | "bar_chart"
  | "line_chart"
  | "pie_chart"
  | "area_chart"
  | "donut_chart"
  | "kpi_card"
  | "data_table"
  | "funnel_chart";

export interface WidgetLayout {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface DashboardWidget {
  id: number;
  dashboard_id: number;
  widget_type: WidgetType;
  title: string;
  query_id?: number;
  sql?: string;
  config: Record<string, unknown>;
  layout: WidgetLayout;
}

export interface Dashboard {
  id: number;
  name: string;
  description?: string;
  is_public: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
  widgets: DashboardWidget[];
}

// Chat / Agent
export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: number;
  session_id: number;
  role: MessageRole;
  content: string;
  sql?: string;
  result?: QueryResult;
  created_at: string;
}

export interface ChatSession {
  id: number;
  title: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  messages?: ChatMessage[];
}

// Integrations / Ingestion
export type IntegrationType = "fhir" | "snowflake";
export type IntegrationStatus = "active" | "inactive" | "error";

export interface FhirConfig {
  server_url: string;
  auth_type: "none" | "basic" | "bearer" | "client_credentials";
  client_id?: string;
  client_secret?: string;
  username?: string;
  password?: string;
}

export interface SnowflakeConfig {
  account: string;
  username: string;
  password: string;
  database: string;
  schema: string;
  warehouse: string;
  role: string;
}

export interface Integration {
  id: number;
  name: string;
  type: IntegrationType;
  config: FhirConfig | SnowflakeConfig;
  status: IntegrationStatus;
  created_by: number;
  created_at: string;
}

export type IngestionRunStatus = "pending" | "running" | "completed" | "failed";

export interface IngestionRun {
  id: number;
  integration_id: number;
  status: IngestionRunStatus;
  records_processed: number;
  records_failed: number;
  started_at: string;
  completed_at?: string;
  last_cursor?: string;
}

// Quarantine
export interface QuarantineRecord {
  id: number;
  ingestion_run_id: number;
  error_message: string;
  source_resource_type?: string;
  source_resource_id?: string;
  created_at: string;
}

export interface QuarantineStats {
  total: number;
  by_resource_type: Record<string, number>;
  recent_errors: string[];
}

// Audit
export interface AuditLog {
  id: number;
  user_id: number;
  username: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, unknown>;
  ip_address?: string;
  created_at: string;
}

// Health
export interface SystemHealth {
  status: "healthy" | "degraded" | "unhealthy";
  database: {
    status: "connected" | "error";
    latency_ms?: number;
  };
  ingestion: {
    last_run?: string;
    status?: IngestionRunStatus;
    error_count_24h: number;
  };
  api: {
    uptime_seconds: number;
    version: string;
  };
}

// PCORnet CDM Tables (schema for data explorer)
export interface PCORnetTable {
  name: string;
  description: string;
  columns: PCORnetColumn[];
}

export interface PCORnetColumn {
  name: string;
  type: string;
  nullable: boolean;
  description?: string;
}

// API Response wrapper
export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
