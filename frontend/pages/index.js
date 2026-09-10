import { useState } from 'react';
import DigitalTwinGraph from '../components/DigitalTwinGraph';

export default function Home() {
  const [selectedSubsystem, setSelectedSubsystem] = useState('battery');

  return (
    <main className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-6xl mx-auto space-y-4">
        <h1 className="text-2xl font-bold font-mono">SpaceWise Control Center</h1>
        <p className="text-sm text-slate-400">Active Node Selected: <span className="text-amber-400 font-mono">{selectedSubsystem}</span></p>
        
        {/* Person 2's Interactive Graph Component */}
        <DigitalTwinGraph onSelectNode={(id) => setSelectedSubsystem(id)} />
      </div>
    </main>
  );
}