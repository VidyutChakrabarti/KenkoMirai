import type { DiseaseState, SimulationSummary } from "../src/types/simulation";

const SERIES: Array<{ key: DiseaseState; label: string; color: string }> = [
  { key: "S", label: "Susceptible", color: "#8c9b95" },
  { key: "E", label: "Exposed", color: "#d5ad68" },
  { key: "I", label: "Infectious", color: "#df7d7d" },
  { key: "R", label: "Recovered", color: "#70b899" },
  { key: "D", label: "Deceased", color: "#575d5b" },
];

function points(history: SimulationSummary[], state: DiseaseState, total: number) {
  if (history.length === 1) return `0,${100 - (history[0].aggregate[state] / total) * 100} 100,${100 - (history[0].aggregate[state] / total) * 100}`;
  return history.map((step, index) => {
    const x = (index / (history.length - 1)) * 100;
    const y = 100 - (step.aggregate[state] / total) * 100;
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ");
}

export default function SimulationChart({ history }: { history: SimulationSummary[] }) {
  const total = history.length ? Object.values(history[0].aggregate).reduce((sum, value) => sum + value, 0) : 1;
  return (
    <div className="chart-panel">
      <svg className="simulation-chart" viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="SEIRD population counts over simulation steps">
        <g className="chart-grid" aria-hidden="true">
          {[0, 25, 50, 75, 100].map((value) => <line key={`h${value}`} x1="0" y1={value} x2="100" y2={value} />)}
          {[0, 25, 50, 75, 100].map((value) => <line key={`v${value}`} x1={value} y1="0" x2={value} y2="100" />)}
        </g>
        {history.length > 0 && SERIES.map((series) => (
          <polyline key={series.key} points={points(history, series.key, total)} fill="none" stroke={series.color} strokeWidth="1.35" vectorEffect="non-scaling-stroke" />
        ))}
      </svg>
      <div className="chart-legend">
        {SERIES.map((series) => <span key={series.key}><i style={{ background: series.color }} />{series.label}</span>)}
      </div>
    </div>
  );
}
