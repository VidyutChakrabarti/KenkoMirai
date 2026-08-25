import Head from "next/head";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import Header from "../../components/Header";
import type { ServiceHealth } from "../types/simulation";

export default function Dashboard() {
  const [health, setHealth] = useState<ServiceHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checkedAt, setCheckedAt] = useState<Date | null>(null);

  const refresh = useCallback(async () => {
    try {
      const response = await fetch("/api/backend/health", { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      setHealth(await response.json() as ServiceHealth);
      setError(null);
    } catch (caught) {
      setHealth(null);
      setError(caught instanceof Error ? caught.message : "Unable to reach the API");
    } finally {
      setCheckedAt(new Date());
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 15_000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  return (
    <>
      <Head><title>Operations | KenkoMirai</title></Head>
      <Header />
      <main className="page-shell compact">
        <div className="page-heading">
          <div><span className="eyebrow">Operations</span><h1>Service readiness</h1><p>Live status from the same-origin frontend gateway.</p></div>
          <button className="button secondary" type="button" onClick={() => void refresh()}>Refresh</button>
        </div>

        <section className="health-grid">
          <article className="health-primary">
            <div className="status-line"><span className={health ? "status-light ok" : "status-light error"} /><span>{health ? "API available" : "API unavailable"}</span></div>
            <strong>{health?.status ?? "offline"}</strong>
            <p>{error ?? "Health endpoint responded successfully."}</p>
          </article>
          <article><small>Version</small><strong>{health?.version ?? "—"}</strong><p>Published backend contract</p></article>
          <article><small>Environment</small><strong>{health?.environment ?? "—"}</strong><p>Runtime configuration profile</p></article>
          <article><small>Active sessions</small><strong>{health?.active_sessions ?? "—"}</strong><p>In-memory bounded scenarios</p></article>
          <article><small>Data fingerprint</small><strong>{health?.resource_fingerprint.slice(0, 8) ?? "—"}</strong><p>Mobility and geography inputs</p></article>
        </section>

        <section className="operations-grid">
          <article className="operations-card">
            <span className="eyebrow">Request path</span><h2>Browser to simulator</h2>
            <ol className="data-path"><li>Same-origin Next.js route</li><li>Versioned FastAPI endpoint</li><li>Validated session manager</li><li>Seeded SEIRD environment</li></ol>
          </article>
          <article className="operations-card">
            <span className="eyebrow">Session policy</span><h2>Bounded by default</h2>
            <ul className="plain-list"><li>Agent and step limits enforced server-side</li><li>Idle sessions expire automatically</li><li>Request IDs returned for tracing</li><li>No patient records or clinical recommendations</li></ul>
          </article>
        </section>

        <div className="operations-footer"><span>Last checked {checkedAt ? checkedAt.toLocaleTimeString() : "—"}</span><Link href="/simulation">Open scenario lab →</Link></div>
      </main>
    </>
  );
}
