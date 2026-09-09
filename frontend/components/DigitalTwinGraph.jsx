import { useMemo } from "react";
import ReactFlow, { Background, Controls, MarkerType } from "reactflow";
import "reactflow/dist/style.css";

const positions = {
  battery: { x: 30, y: 120 },
  thermal: { x: 260, y: 30 },
  comms: { x: 500, y: 120 },
  propulsion: { x: 740, y: 30 }
};

function statusClass(status) {
  return String(status || "NOMINAL").toLowerCase();
}

export default function DigitalTwinGraph({ nodes = [] }) {
  const flowNodes = useMemo(
    () =>
      nodes.map((n) => ({
        id: n.id,
        position: positions[n.id] || { x: 0, y: 0 },
        data: { label: `${n.label}\n${n.status} · ${n.delay}` },
        className: `twin-node ${statusClass(n.status)}`
      })),
    [nodes]
  );

  const flowEdges = [
    { id: "e1", source: "battery", target: "thermal", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: "e2", source: "thermal", target: "comms", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
    { id: "e3", source: "comms", target: "propulsion", animated: true, markerEnd: { type: MarkerType.ArrowClosed } }
  ];

  return (
    <div className="flow-wrap">
      <ReactFlow nodes={flowNodes} edges={flowEdges} fitView proOptions={{ hideAttribution: true }}>
        <Background gap={24} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
