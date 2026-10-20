export type Role = "admin" | "viewer";

export interface AuthSession { access_token: string; token_type: string; role: Role; tenant: string }
export interface LogEvent { id: string; timestamp: string; source: string; event_type: string; severity: number | null; src_ip: string | null; user_name: string | null; raw: Record<string, unknown> }
export interface LogPage { items: LogEvent[]; total: number; page: number; page_size: number }
export interface Group { value: string; count: number }
export interface DashboardStatistics { total_logs: number; failed_login_events: number; total_security_alerts: number; by_severity: Group[]; by_source: Group[]; top_source_ips: Group[]; top_usernames: Group[]; top_event_types: Group[]; activity: { timestamp: string; count: number }[] }
export interface Alert { id: string; title: string; severity: number; status: string; details: Record<string, unknown>; created_at: string }
