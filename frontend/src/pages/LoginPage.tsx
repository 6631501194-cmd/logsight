import { Eye, EyeOff, Shield } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { auth } from "../services/auth";

export function LoginPage({ onLogin }: { onLogin: () => void }) {
  const navigate = useNavigate(); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [showPassword, setShowPassword] = useState(false); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) { event.preventDefault(); setError(""); if (!email.trim() || !password) { setError("Enter your email and password."); return; } setLoading(true); try { auth.set(await api.login(email.trim(), password)); onLogin(); navigate("/dashboard", { replace: true }); } catch { setError("Sign-in failed. Check your email and password."); } finally { setLoading(false); } }
  return <div className="login-page"><section className="login-card"><div className="login-brand"><Shield size={32}/><div><h1>LogSight</h1><p>Security visibility, clearly organized.</p></div></div><form onSubmit={submit} noValidate><label>Email<input type="email" value={email} onChange={event => setEmail(event.target.value)} autoComplete="email" placeholder="you@example.com" disabled={loading}/></label><label>Password<div className="password-input"><input type={showPassword ? "text" : "password"} value={password} onChange={event => setPassword(event.target.value)} autoComplete="current-password" placeholder="Enter your password" disabled={loading}/><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div></label>{error && <p className="form-error" role="alert">{error}</p>}<button className="primary-button login-button" disabled={loading}>{loading ? "Signing in…" : "Sign in"}</button></form><p className="login-note">Use the demo account configured in your local environment.</p></section></div>;
}
