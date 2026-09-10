import React, { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Zap,
  Battery,
  Thermometer,
  Radio,
  Rocket,
  Cpu,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from 'lucide-react';

// Status color mapping function matching contract.json specifications
const getStatusStyles = (status) => {
  switch (status?.toUpperCase()) {
    case 'NOMINAL':
      return {
        borderColor: 'border-emerald-500',
        textColor: 'text-emerald-400',
        bgColor: 'bg-emerald-950/40',
        glow: 'shadow-[0_0_15px_rgba(16,185,129,0.25)]',
        icon: <CheckCircle className="w-4 h-4 text-emerald-400" />,
      };
    case 'WATCH':
    case 'WARNING':
      return {
        borderColor: 'border-amber-500',
        textColor: 'text-amber-400',
        bgColor: 'bg-amber-950/40',
        glow: 'shadow-[0_0_15px_rgba(245,158,11,0.25)]',
        icon: <AlertTriangle className="w-4 h-4 text-amber-400 animate-pulse" />,
      };
    case 'CRITICAL':
    case 'FAILED':
      return {
        borderColor: 'border-rose-600',
        textColor: 'text-rose-500',
        bgColor: 'bg-rose-950/50',
        glow: 'shadow-[0_0_20px_rgba(225,29,72,0.4)]',
        icon: <XCircle className="w-4 h-4 text-rose-500 animate-bounce" />,
      };
    default:
      return {
        borderColor: 'border-slate-600',
        textColor: 'text-slate-400',
        bgColor: 'bg-slate-900/40',
        glow: '',
        icon: null,
      };
  }
};

// Map subsystem IDs to Lucide icons
const getNodeIcon = (id) => {
  switch (id) {
    case 'solar_power':
      return <Zap className="w-5 h-5" />;
    case 'battery':
      return <Battery className="w-5 h-5" />;
    case 'thermal':
      return <Thermometer className="w-5 h-5" />;
    case 'comms':
      return <Radio className="w-5 h-5" />;
    case 'propulsion':
      return <Rocket className="w-5 h-5" />;
    case 'payload':
      return <Cpu className="w-5 h-5" />;
    default:
      return <Cpu className="w-5 h-5" />;
  }
};

// Custom React Flow Node Component
const SubsystemNode = ({ data }) => {
  const styles = getStatusStyles(data.status);

  return (
    <div
      className={`relative min-w-[180px] rounded-xl border-2 p-3 bg-slate-950/90 backdrop-blur-md transition-all duration-300 ${styles.borderColor} ${styles.glow} cursor-pointer hover:scale-105`}
    >
      <Handle type="target" position={Position.Top} className="!bg-slate-500 !w-2 !h-2" />

      <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className={styles.textColor}>{getNodeIcon(data.id)}</span>
          <span className="font-semibold text-xs tracking-wider text-slate-200 uppercase">
            {data.label}
          </span>
        </div>
        {styles.icon}
      </div>

      <div className="flex items-center justify-between text-xs mt-1">
        <span className="text-slate-400 font-mono">STATUS:</span>
        <span className={`font-mono font-bold ${styles.textColor}`}>
          {data.status || 'UNKNOWN'}
        </span>
      </div>

      {data.delay && (
        <div className="mt-2 pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
          <span className="text-slate-500 font-mono">CASCADE PROP:</span>
          <span className="font-mono bg-slate-800/80 px-1.5 py-0.5 rounded text-amber-300 border border-amber-500/20">
            {data.delay}
          </span>
        </div>
      )}

      <Handle type="source" position={Position.Bottom} className="!bg-slate-500 !w-2 !h-2" />
    </div>
  );
};

// Master contract mock fallback data
const DEFAULT_CONTRACT = {
  telemetry: {
    solar_power: { voltage: 28.1, status: 'NOMINAL' },
    battery: { level: 31.0, status: 'CRITICAL' },
    thermal: { temp: 19.5, status: 'WATCH' },
    comms: { signal: -64.6, status: 'WATCH' },
    propulsion: { thrust: 13.8, status: 'CRITICAL' },
    payload: { power: 117.0, status: 'NOMINAL' },
  },
  graph_nodes: [
    { id: 'battery', status: 'CRITICAL', label: 'Battery (Origin)', delay: 'T+0s' },
    { id: 'thermal', status: 'WATCH', label: 'Thermal Control', delay: 'T+14s' },
    { id: 'comms', status: 'WATCH', label: 'Communication', delay: 'T+35s' },
    { id: 'propulsion', status: 'CRITICAL', label: 'Propulsion', delay: 'T+53s' },
  ],
};

export default function DigitalTwinGraph({ contractData = DEFAULT_CONTRACT, onSelectNode }) {
  const nodeTypes = useMemo(() => ({ subsystem: SubsystemNode }), []);

  // Merge contract telemetry and graph failure delay info into node layout
  const initialNodes = useMemo(() => {
    const telemetry = contractData?.telemetry || DEFAULT_CONTRACT.telemetry;
    const cascadeMap = (contractData?.graph_nodes || DEFAULT_CONTRACT.graph_nodes).reduce(
      (acc, curr) => {
        acc[curr.id] = curr;
        return acc;
      },
      {}
    );

    const layoutPositions = {
      solar_power: { x: 50, y: 50 },
      battery: { x: 300, y: 50 },
      thermal: { x: 300, y: 220 },
      comms: { x: 550, y: 220 },
      propulsion: { x: 550, y: 390 },
      payload: { x: 50, y: 220 },
    };

    const definitions = [
      { id: 'solar_power', label: 'Solar Power' },
      { id: 'battery', label: 'Battery' },
      { id: 'thermal', label: 'Thermal Control' },
      { id: 'comms', label: 'Communication' },
      { id: 'propulsion', label: 'Propulsion' },
      { id: 'payload', label: 'Payload' },
    ];

    return definitions.map((def) => {
      const nodeTelemetry = telemetry[def.id] || {};
      const cascadeInfo = cascadeMap[def.id] || {};

      return {
        id: def.id,
        type: 'subsystem',
        position: layoutPositions[def.id],
        data: {
          id: def.id,
          label: cascadeInfo.label || def.label,
          status: nodeTelemetry.status || cascadeInfo.status || 'NOMINAL',
          delay: cascadeInfo.delay || null,
        },
      };
    });
  }, [contractData]);

  // Edges mapping failure propagation path & telemetry linkages
  const initialEdges = useMemo(
    () => [
      { id: 'e-solar-battery', source: 'solar_power', target: 'battery', animated: true },
      { id: 'e-solar-payload', source: 'solar_power', target: 'payload' },
      {
        id: 'e-battery-thermal',
        source: 'battery',
        target: 'thermal',
        animated: true,
        label: 'T+14s',
        labelStyle: { fill: '#f59e0b', fontWeight: 700, fontSize: 11 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.95, rx: 4, ry: 4 },
        labelBgPadding: [6, 4],
        style: { stroke: '#ef4444', strokeWidth: 2 },
      },
      {
        id: 'e-thermal-comms',
        source: 'thermal',
        target: 'comms',
        animated: true,
        label: 'T+35s',
        labelStyle: { fill: '#f59e0b', fontWeight: 700, fontSize: 11 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.95, rx: 4, ry: 4 },
        labelBgPadding: [6, 4],
        style: { stroke: '#f59e0b', strokeWidth: 2 },
      },
      {
        id: 'e-comms-propulsion',
        source: 'comms',
        target: 'propulsion',
        animated: true,
        label: 'T+53s',
        labelStyle: { fill: '#f59e0b', fontWeight: 700, fontSize: 11 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.95, rx: 4, ry: 4 },
        labelBgPadding: [6, 4],
        style: { stroke: '#ef4444', strokeWidth: 2 },
      },
    ],
    []
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  // Handle clicking on node and passing ID to telemetry panel state
  const handleNodeClick = useCallback(
    (_, node) => {
      if (onSelectNode) {
        onSelectNode(node.id);
      }
    },
    [onSelectNode]
  );

  return (
    <div className="w-full h-[600px] bg-slate-950 rounded-2xl border border-slate-800 relative overflow-hidden shadow-2xl">
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 text-xs font-mono text-slate-300">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        SPACECRAFT DIGITAL TWIN (2D SCHEMATIC)
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
      >
        <Background color="#1e293b" gap={20} size={1} />
        <Controls className="!bg-slate-900 !border-slate-800 !fill-slate-300 !rounded-lg" />
      </ReactFlow>
    </div>
  );
}
