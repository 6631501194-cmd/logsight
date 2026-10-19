import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const api = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [status, setStatus] = React.useState("Checking API…");
  React.useEffect(() => {
    fetch(`${api}/health`).then((response) => response.ok ? response.json() : Promise.reject()).then(() => setStatus("API and database are healthy")).catch(() => setStatus("API is unavailable"));
  }, []);
  return <main><h1>LogSight</h1><p>Log management system</p><p className="status">{status}</p><p>Dashboard authentication, search, and alerts are delivered in Phase 2.</p></main>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
