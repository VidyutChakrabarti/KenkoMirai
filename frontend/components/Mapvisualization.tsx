import type { AgentState, DiseaseState } from "../src/types/simulation";

const BOUNDS = { minLat: 33.65, maxLat: 34.85, minLng: -118.95, maxLng: -117.6 };
const COLORS: Record<DiseaseState, string> = {
  S: "#8c9b95",
  E: "#d5ad68",
  I: "#df7d7d",
  R: "#70b899",
  D: "#575d5b",
};

function position(agent: AgentState) {
  const x = ((agent.lng - BOUNDS.minLng) / (BOUNDS.maxLng - BOUNDS.minLng)) * 100;
  const y = (1 - (agent.lat - BOUNDS.minLat) / (BOUNDS.maxLat - BOUNDS.minLat)) * 100;
  return { x: Math.min(100, Math.max(0, x)), y: Math.min(100, Math.max(0, y)) };
}

export default function MapVisualization({ agents }: { agents: AgentState[] }) {
  const stride = Math.max(1, Math.ceil(agents.length / 900));
  const visibleAgents = agents.filter((_, index) => index % stride === 0);
  return (
    <div className="map-panel">
      <svg className="agent-map" viewBox="0 0 100 100" role="img" aria-label="Agent positions across the Los Angeles scenario area">
        <rect width="100" height="100" rx="3" fill="#0e1513" />
        <g className="map-grid" aria-hidden="true">
          {[20, 40, 60, 80].map((value) => <line key={`v${value}`} x1={value} y1="0" x2={value} y2="100" />)}
          {[20, 40, 60, 80].map((value) => <line key={`h${value}`} x1="0" y1={value} x2="100" y2={value} />)}
        </g>
        <path d="M8 83 C24 69 34 71 45 55 S64 39 72 25 S89 20 95 8" fill="none" stroke="#25352f" strokeWidth="1.1" />
        <path d="M2 42 C20 47 34 38 48 42 S73 56 98 51" fill="none" stroke="#1f2e29" strokeWidth="0.8" />
        {visibleAgents.map((agent) => {
          const point = position(agent);
          return <circle key={agent.id} cx={point.x} cy={point.y} r={agent.state === "I" ? 0.72 : 0.48} fill={COLORS[agent.state]} opacity={agent.state === "D" ? 0.45 : 0.82} />;
        })}
      </svg>
      <div className="map-legend" aria-label="Disease state legend">
        {(["S", "E", "I", "R", "D"] as DiseaseState[]).map((state) => (
          <span key={state}><i style={{ background: COLORS[state] }} />{{ S: "Susceptible", E: "Exposed", I: "Infectious", R: "Recovered", D: "Deceased" }[state]}</span>
        ))}
      </div>
      {stride > 1 && <p className="visual-note">Rendering every {stride}th agent for browser performance; aggregate counts remain complete.</p>}
    </div>
  );
}
