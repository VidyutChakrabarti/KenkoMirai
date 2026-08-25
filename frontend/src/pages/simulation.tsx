import Head from "next/head";
import { FormEvent, useEffect, useMemo, useState } from "react";
import Header from "../../components/Header";
import MapVisualization from "../../components/Mapvisualization";
import SimulationChart from "../../components/Simulationchart";
import type { Policy, ServiceHealth, SessionCreated, SimulationAdvanceResult, SimulationHistoryPage, SimulationSnapshot, SimulationSummary } from "../types/simulation";

const SESSION_STORAGE_KEY = "kenkomirai.simulation-id";

class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

function summary(snapshot: SimulationSnapshot): SimulationSummary {
  return {
    time: snapshot.time,
    elapsed_days: snapshot.elapsed_days,
    hour_of_day: snapshot.hour_of_day,
    aggregate: snapshot.aggregate,
    lockdown: snapshot.lockdown,
    active_policy: snapshot.active_policy,
    new_exposures: snapshot.new_exposures,
    new_infectious: snapshot.new_infectious,
    new_recoveries: snapshot.new_recoveries,
    new_deaths: snapshot.new_deaths,
    exposure_ratio: snapshot.exposure_ratio,
    mobility_multiplier: snapshot.mobility_multiplier,
    mobility_date: snapshot.mobility_date,
  };
}

async function responseJson<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload.detail === "string" ? payload.detail : `Request failed with status ${response.status}`;
    throw new ApiError(detail, response.status);
  }
  return payload as T;
}

export default function SimulationPage() {
  const [numAgents, setNumAgents] = useState(500);
  const [initialInfected, setInitialInfected] = useState(20);
  const [seed, setSeed] = useState(2025);
  const [policy, setPolicy] = useState<Policy>("adaptive");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [snapshot, setSnapshot] = useState<SimulationSnapshot | null>(null);
  const [history, setHistory] = useState<SimulationSummary[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxAgents, setMaxAgents] = useState(10_000);

  const total = useMemo(() => snapshot ? Object.values(snapshot.aggregate).reduce((sum, value) => sum + value, 0) : numAgents, [snapshot, numAgents]);

  useEffect(() => {
    fetch("/api/backend/health")
      .then(responseJson<ServiceHealth>)
      .then((health) => setMaxAgents(health.limits.max_agents))
      .catch(() => undefined);
    const savedId = window.sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!savedId) return;
    let cancelled = false;
    setBusy(true);
    fetch(`/api/backend/simulations/${savedId}`)
      .then(responseJson<SimulationSnapshot>)
      .then(async (restoredSnapshot) => {
        const after = Math.max(-1, restoredSnapshot.time - 1000);
        const restoredHistory = await fetch(`/api/backend/simulations/${savedId}/history?after=${after}&limit=1000`)
          .then(responseJson<SimulationHistoryPage>);
        if (cancelled) return;
        setSessionId(savedId);
        setSnapshot(restoredSnapshot);
        setHistory(restoredHistory.items);
      })
      .catch(() => window.sessionStorage.removeItem(SESSION_STORAGE_KEY))
      .finally(() => { if (!cancelled) setBusy(false); });
    return () => { cancelled = true; };
  }, []);

  async function createScenario(event?: FormEvent) {
    event?.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (sessionId) {
        const deletion = await fetch(`/api/backend/simulations/${sessionId}`, { method: "DELETE" });
        if (!deletion.ok && deletion.status !== 404) await responseJson<unknown>(deletion);
        window.sessionStorage.removeItem(SESSION_STORAGE_KEY);
        setSessionId(null);
        setSnapshot(null);
        setHistory([]);
      }
      const response = await fetch("/api/backend/simulations", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ num_agents: numAgents, initial_infected: initialInfected, seed, policy }),
      });
      const created = await responseJson<SessionCreated>(response);
      setSessionId(created.simulation_id);
      window.sessionStorage.setItem(SESSION_STORAGE_KEY, created.simulation_id);
      setSnapshot(created.snapshot);
      setHistory([summary(created.snapshot)]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create the scenario");
    } finally {
      setBusy(false);
    }
  }

  async function advance(steps: number) {
    if (!sessionId) return;
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`/api/backend/simulations/${sessionId}/steps`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ steps, policy }),
      });
      const result = await responseJson<SimulationAdvanceResult>(response);
      setSnapshot(result.snapshot);
      setHistory((current) => [...current, ...result.history].slice(-1000));
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 404) {
        window.sessionStorage.removeItem(SESSION_STORAGE_KEY);
        setSessionId(null);
        setSnapshot(null);
        setHistory([]);
      }
      setError(caught instanceof Error ? caught.message : "Unable to advance the scenario");
    } finally {
      setBusy(false);
    }
  }

  const aggregate = snapshot?.aggregate ?? { S: total - initialInfected, E: 0, I: initialInfected, R: 0, D: 0 };

  return (
    <>
      <Head><title>Scenario lab | KenkoMirai</title></Head>
      <Header />
      <main className="lab-shell">
        <aside className="scenario-panel">
          <div><span className="eyebrow">Configuration</span><h1>Scenario lab</h1><p>Start a reproducible session, then advance it under an explicit intervention policy.</p></div>
          <form onSubmit={(event) => void createScenario(event)}>
            <label>Population<input type="number" min="10" max={maxAgents} value={numAgents} onChange={(event) => setNumAgents(Number(event.target.value))} disabled={busy} /></label>
            <label>Initially infectious<input type="number" min="0" max={numAgents} value={initialInfected} onChange={(event) => setInitialInfected(Number(event.target.value))} disabled={busy} /></label>
            <label>Random seed<input type="number" min="0" max="2147483647" value={seed} onChange={(event) => setSeed(Number(event.target.value))} disabled={busy} /></label>
            <label>Intervention<select value={policy} onChange={(event) => setPolicy(event.target.value as Policy)} disabled={busy}><option value="open">Open</option><option value="lockdown">Lockdown</option><option value="adaptive">Adaptive thresholds</option></select></label>
            <button className="button primary full" type="submit" disabled={busy || initialInfected > numAgents || numAgents > maxAgents}>{sessionId ? "Restart scenario" : "Create scenario"}</button>
          </form>
          {sessionId && <div className="step-controls"><button className="button secondary" type="button" disabled={busy} onClick={() => void advance(1)}>Advance 1 hour</button><button className="button secondary" type="button" disabled={busy} onClick={() => void advance(24)}>Advance 1 day</button></div>}
          <p className="form-note">Adaptive policy enters lockdown at 10% infectious prevalence and releases below 4%.</p>
          {error && <div className="error-message" role="alert">{error}</div>}
        </aside>

        <section className="scenario-workspace">
          <div className="workspace-heading"><div><span className="eyebrow">Live model state</span><h2>{snapshot ? `Day ${snapshot.elapsed_days.toFixed(1)} · ${String(snapshot.hour_of_day).padStart(2, "0")}:00` : "No active scenario"}</h2></div><span className={snapshot?.lockdown ? "policy-chip lockdown" : "policy-chip"}>{snapshot ? (snapshot.lockdown ? "Lockdown active" : "Mobility open") : "Awaiting run"}</span></div>
          <div className="state-cards">
            {(["S", "E", "I", "R", "D"] as const).map((state) => <article key={state}><small>{{ S: "Susceptible", E: "Exposed", I: "Infectious", R: "Recovered", D: "Deceased" }[state]}</small><strong>{aggregate[state].toLocaleString()}</strong><span>{total ? ((aggregate[state] / total) * 100).toFixed(1) : "0.0"}%</span></article>)}
          </div>
          <div className="visual-grid">
            <article className="workspace-card"><div className="card-heading"><div><span className="eyebrow">Spatial view</span><h3>Agent distribution</h3></div><span>{snapshot?.agents.length.toLocaleString() ?? 0} agents</span></div>{snapshot ? <MapVisualization agents={snapshot.agents} /> : <div className="empty-visual">Create a scenario to populate the map.</div>}</article>
            <article className="workspace-card"><div className="card-heading"><div><span className="eyebrow">Time series</span><h3>Population states</h3></div><span>{history.length} samples</span></div>{history.length ? <SimulationChart history={history} /> : <div className="empty-visual">The trajectory appears after scenario creation.</div>}</article>
          </div>
          <div className="session-metrics"><span><small>Policy</small>{snapshot?.active_policy ?? policy}</span><span><small>New exposures</small>{snapshot?.new_exposures ?? 0}</span><span><small>New infectious</small>{snapshot?.new_infectious ?? 0}</span><span><small>Exposure ratio</small>{snapshot?.exposure_ratio.toFixed(2) ?? "0.00"}</span><span><small>Effective mobility</small>{snapshot ? `${(snapshot.mobility_multiplier * 100).toFixed(0)}%` : "—"}</span><span><small>Mobility source date</small>{snapshot?.mobility_date ?? "—"}</span><span><small>Session</small>{sessionId ? sessionId.slice(0, 8) : "—"}</span></div>
        </section>
      </main>
    </>
  );
}
