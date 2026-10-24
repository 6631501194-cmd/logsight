import { AlertTriangle, BarChart3, FileText, LogOut, Settings, Shield, X } from "lucide-react";
import { NavLink } from "react-router-dom";
import type { AuthSession } from "../types/api";

const links = [{ to: "/dashboard", label: "Dashboard", icon: BarChart3 }, { to: "/logs", label: "Log explorer", icon: FileText }, { to: "/alerts", label: "Security alerts", icon: AlertTriangle }];

export function Layout({ session, onLogout, children }: { session: AuthSession; onLogout: () => void; children: React.ReactNode }) {
  const visibleLinks = session.role === "admin" ? [...links, { to: "/administration", label: "Administration", icon: Settings }] : links;
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><Shield /> <span>LogSight</span></div><p className="tenant-badge">{session.tenant}</p><nav>{visibleLinks.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}><Icon size={18} />{label}</NavLink>)}</nav><div className="sidebar-footer"><strong>{session.role === "admin" ? "Administrator" : "Viewer"}</strong><span>Tenant: {session.tenant}</span><button className="logout-button" onClick={onLogout}><LogOut size={16} /> Sign out</button></div></aside><main className="content"><header className="mobile-header"><div className="brand"><Shield /> LogSight</div><button onClick={onLogout} aria-label="Sign out"><X size={18} /></button></header>{children}</main></div>;
}
