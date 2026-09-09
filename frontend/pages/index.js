import { useEffect, useMemo, useState } from "react";
import DigitalTwinGraph from "../components/DigitalTwinGraph";
import TelemetryReadouts from "../components/TelemetryReadouts";
import CopilotCards from "../components/CopilotCards";

const API = "http://localhost:8000";

const initialState = {
  active_scenario: "battery_cascade",
  telemetry: {},
  graph_nodes: [],
  collision_data: {
    imminent: false,
    distance_km: 10,
    time_to_impact_sec: 0,
    debris_id: "DEBRIS-4092"
  },
  copilot_recommendation: {
    primary_action: "Loading...",
    survival_prob: 0,
    explanation: "Connecting to mission-control backend..."
  }
};

export default function Home() {
  const [state, setState] = useState(initialState);
  const [connected, setConnected] = useState(false);

  async function refresh() {
    const res = await fetch(`${API}/api/state`);
    setState(await res.json());
  }

  async function post(path) {
    const res = await fetch(`${API}${path}`, { method: "POST" });
    setState(await res.json());
  }

  useEffect(() => {
    refresh().catch(() => {});

    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => setState(JSON.parse(event.data));

    return () => ws.close();
  }, []);

  const collision = state.collision_data || {};
  const critical = collision.imminent;

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <div className="eyebrow">MISSION CONTROL / DIGITAL TWIN</div>
          <h1>SPACE<span>WISE</span></h1>
        </div>
        <div className="connection">
          <span className={connected ? "dot online" : "dot"} />
          {connected ? "LIVE LINK" : "OFFLINE"}
        </div>
      </header>

      {critical && (
        <div className="danger-banner">
          <strong>⚠ DEBRIS APPROACH</strong>
          <span>{collision.debris_id} · {collision.distance_km} km · T−{collision.time_to_impact_sec}s</span>
        </div>
      )}

      <section className="metrics">
        <div className="metric"><small>DEBRIS RANGE</small><b>{collision.distance_km} km</b></div>
        <div className="metric"><small>TIME TO IMPACT</small><b>{collision.time_to_impact_sec}s</b></div>
        <div className="metric"><small>DEBRIS ID</small><b>{collision.debris_id}</b></div>
        <div className="metric"><small>SCENARIO</small><b>{state.active_scenario}</b></div>
      </section>

      <section className="grid">
        <div className="panel graph-panel">
          <div className="panel-title">
            <span>SPACECRAFT DIGITAL TWIN</span>
            <span className="muted">FAILURE PROPAGATION MAP</span>
          </div>
          <DigitalTwinGraph nodes={state.graph_nodes} />
        </div>

        <div className="panel telemetry-panel">
          <div className="panel-title">
            <span>LIVE TELEMETRY</span>
            <span className="muted">SIMULATED</span>
          </div>
          <TelemetryReadouts telemetry={state.telemetry} />
        </div>

        <div className="panel copilot-panel">
          <div className="panel-title">
            <span>AI FLIGHT COPILOT</span>
            <span className="muted">GROQ / FALLBACK</span>
          </div>
          <CopilotCards recommendation={state.copilot_recommendation} />
        </div>

        <div className="panel controls-panel">
          <div className="panel-title">
            <span>SIMULATION CONTROLS</span>
            <span className="muted">DEMO MODE</span>
          </div>
          <div className="button-row">
            <button onClick={() => post("/api/debris/trigger")}>TRIGGER DEBRIS APPROACH</button>
            <button onClick={() => post("/api/debris/advance")}>ADVANCE 20 SEC</button>
            <button onClick={() => post("/api/reset")} className="secondary">RESET SIMULATION</button>
          </div>
          <p className="hint">
            The debris engine uses a deterministic mock trajectory. It is intentionally not a real orbital propagator.
          </p>
        </div>
      </section>
    </main>
  );
}
