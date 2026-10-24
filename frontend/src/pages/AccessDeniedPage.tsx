import { Link } from "react-router-dom";

export function AccessDeniedPage() {
  return <div className="page access-denied"><p className="eyebrow">Permission required</p><h1>Administration access denied</h1><p>Your Viewer account can access dashboards, logs, and alerts, but it cannot use tenant administration controls.</p><Link className="primary-button" to="/dashboard">Return to dashboard</Link></div>;
}
