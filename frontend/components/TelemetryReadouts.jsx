export default function TelemetryReadouts({ telemetry = {} }) {
  const items = [
    ["solar_power", "Solar Power", "voltage", "V"],
    ["battery", "Battery", "level", "%"],
    ["thermal", "Thermal", "temp", "°C"],
    ["comms", "Comms Signal", "signal", "dBm"],
    ["propulsion", "Propulsion", "thrust", "N"],
    ["payload", "Payload Power", "power", "W"]
  ];

  return (
    <div className="telemetry-grid">
      {items.map(([id, label, key, unit]) => {
        const item = telemetry[id] || {};
        return (
          <div className="telemetry-card" key={id}>
            <div className="telemetry-label">{label}</div>
            <div className="telemetry-value">{item[key] ?? "--"} <small>{unit}</small></div>
            <div className={`status ${String(item.status || "NOMINAL").toLowerCase()}`}>
              {item.status || "NOMINAL"}
            </div>
          </div>
        );
      })}
    </div>
  );
}
