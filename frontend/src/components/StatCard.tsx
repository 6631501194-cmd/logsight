import type { LucideIcon } from "lucide-react";
export function StatCard({ title, value, icon: Icon, accent }: { title: string; value: number; icon: LucideIcon; accent: string }) { return <article className={`stat-card ${accent}`}><div><span>{title}</span><strong>{value.toLocaleString()}</strong></div><Icon size={24} /></article>; }
