import { DatabaseZap, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { api } from "../services/api";

export function AdministrationPage() {
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const runRetention = async () => {
    if (!window.confirm("Run the retention cleanup now? Expired logs will be permanently removed by the server policy.")) return;
    setRunning(true);
    setError("");
    setMessage("");
    try {
      const result = await api.runRetention();
      setMessage(`Retention cleanup completed. ${result.deleted_logs} expired log${result.deleted_logs === 1 ? " was" : "s were"} removed.`);
    } catch {
      setError("The retention cleanup could not be completed. Please try again later.");
    } finally {
      setRunning(false);
    }
  };

  return <div className="page"><div className="page-title"><div><p className="eyebrow">Administrator-only controls</p><h1>Administration</h1></div><span className="live-indicator">Admin access</span></div><section className="panel admin-panel"><div className="admin-icon"><DatabaseZap size={22}/></div><div><h2>Log retention cleanup</h2><p>Run the existing server-side retention policy to remove logs that have passed their configured retention period.</p><p className="admin-note"><ShieldCheck size={16}/> This action is protected by backend role-based access control.</p></div><button className="primary-button" onClick={runRetention} disabled={running}>{running ? "Running cleanup…" : "Run retention cleanup"}</button></section>{message && <p className="success-banner">{message}</p>}{error && <p className="error-banner">{error}</p>}</div>;
}
