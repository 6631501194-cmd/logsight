import { auth } from "./auth";
import type { Alert, AuthSession, DashboardStatistics, LogPage } from "../types/api";

const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const session = auth.get();
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (session) headers.set("Authorization", `Bearer ${session.access_token}`);
  if (init.body) headers.set("Content-Type", "application/json");
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers });
  if (response.status === 401) { auth.clear(); window.dispatchEvent(new Event("logsight:unauthorized")); }
  if (!response.ok) throw new Error(response.status === 401 ? "Your session has expired. Please sign in again." : response.status === 403 ? "You do not have permission to access this resource." : "The request could not be completed.");
  return response.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) => request<AuthSession>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  statistics: () => request<DashboardStatistics>("/api/dashboard/statistics"),
  logs: (params: URLSearchParams) => request<LogPage>(`/api/logs?${params.toString()}`),
  alerts: (severity?: string) => request<Alert[]>(`/api/alerts${severity ? `?severity=${encodeURIComponent(severity)}` : ""}`),
};
