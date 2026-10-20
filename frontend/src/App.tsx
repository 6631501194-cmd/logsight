import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AlertsPage } from "./pages/AlertsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { LogsPage } from "./pages/LogsPage";
import { auth } from "./services/auth";

function Protected({ children }: { children: React.ReactNode }) { const session = auth.get(); return session ? <Layout session={session} onLogout={() => { auth.clear(); window.location.assign("/login"); }}>{children}</Layout> : <Navigate to="/login" replace />; }
export default function App() { const [, update] = useState(0); const navigate = useNavigate(); useEffect(() => { const handler = () => { update(v => v + 1); navigate("/login", { replace: true }); }; window.addEventListener("logsight:unauthorized", handler); return () => window.removeEventListener("logsight:unauthorized", handler); }, [navigate]); return <Routes><Route path="/login" element={auth.get() ? <Navigate to="/dashboard" replace/> : <LoginPage onLogin={() => update(v => v + 1)}/>}/><Route path="/dashboard" element={<Protected><DashboardPage/></Protected>}/><Route path="/logs" element={<Protected><LogsPage/></Protected>}/><Route path="/alerts" element={<Protected><AlertsPage/></Protected>}/><Route path="*" element={<Navigate to="/dashboard" replace/>}/></Routes>; }
