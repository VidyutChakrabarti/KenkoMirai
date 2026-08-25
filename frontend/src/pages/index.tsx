import Head from "next/head";
import Link from "next/link";
import Header from "../../components/Header";

const capabilities = [
  ["Reproducible scenarios", "Every run is driven by an explicit seed and validated model parameters."],
  ["Transparent interventions", "Compare open, lockdown, and adaptive threshold policies without hidden reasoning traces."],
  ["Operational API", "Create bounded sessions, advance them safely, or run deterministic batch scenarios."],
];

export default function Home() {
  return (
    <>
      <Head>
        <title>KenkoMirai | Urban health scenario laboratory</title>
        <meta name="description" content="A reproducible SEIRD agent simulation for exploring urban outbreak interventions." />
      </Head>
      <Header />
      <main className="page-shell">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow">Urban health scenario laboratory</span>
            <h1>Explore intervention trade-offs with a transparent digital twin.</h1>
            <p>
              KenkoMirai combines a seeded agent-based SEIRD model with an operational API and an interactive scenario workspace. It is designed for engineering exploration—not clinical prediction.
            </p>
            <div className="hero-actions">
              <Link className="button primary" href="/simulation">Open scenario lab</Link>
              <Link className="button secondary" href="/dashboard">View operations</Link>
            </div>
          </div>
          <div className="hero-visual" aria-label="Illustrative urban health model">
            <div className="visual-header"><span>Los Angeles model</span><span className="live-chip">Seeded run</span></div>
            <div className="mini-map">
              {Array.from({ length: 54 }, (_, index) => (
                <i key={index} className={index % 13 === 0 ? "infectious" : index % 7 === 0 ? "exposed" : index % 5 === 0 ? "recovered" : "susceptible"} style={{ left: `${8 + ((index * 17) % 86)}%`, top: `${8 + ((index * 29) % 82)}%` }} />
              ))}
            </div>
            <div className="visual-metrics"><span><small>Model</small>SEIRD</span><span><small>Policy</small>Adaptive</span><span><small>State</small>Reproducible</span></div>
          </div>
        </section>

        <section className="capability-grid" aria-label="Core capabilities">
          {capabilities.map(([title, description], index) => (
            <article key={title}><span className="capability-number">0{index + 1}</span><h2>{title}</h2><p>{description}</p></article>
          ))}
        </section>

        <section className="model-note">
          <div><span className="eyebrow">Scope</span><h2>Built for auditable experiments</h2></div>
          <p>Parameters, seeds, state transitions, and policy actions are explicit. Results depend on model assumptions and must not be interpreted as public-health forecasts or medical advice.</p>
        </section>
      </main>
    </>
  );
}
