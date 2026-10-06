import { ChevronRight, HeartPulse, MoreVertical, RefreshCw, SlidersHorizontal, Thermometer, X } from "lucide-react";
import { useState } from "react";

import type { Machine } from "../types";

interface MachineTableProps {
  machines: Machine[];
  expanded?: boolean;
  onRefresh: () => Promise<void>;
}

const IMAGE_BY_MACHINE: Record<string, string> = {
  "atlas-one": "/machines/atlas-one.png",
  "cedar-mini": "/machines/cedar-mini.png",
  "northstar-cell": "/machines/northstar-cell.png",
};

function temperature(current: number | null, target: number | null) {
  if (current == null) return "N/A";
  return target == null ? `${Math.round(current)}°` : `${Math.round(current)} / ${Math.round(target)}°`;
}

function stateLabel(state: Machine["state"]) {
  return state.charAt(0).toUpperCase() + state.slice(1);
}

export function MachineTable({ machines, expanded = false, onRefresh }: MachineTableProps) {
  const [attentionOnly, setAttentionOnly] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null);
  const visibleMachines = attentionOnly
    ? machines.filter((machine) => machine.health !== "healthy")
    : machines;
  const selectedMachine = machines.find((machine) => machine.id === selectedMachineId) ?? null;

  async function refresh() {
    setRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <section className={expanded ? "panel machine-panel expanded" : "panel machine-panel"}>
      <header className="panel-header">
        <div><HeartPulse size={18} /><h2>Machine status</h2></div>
        <div className="panel-actions">
          <button className="text-button" type="button" title="Refresh machine status" onClick={() => void refresh()} disabled={refreshing}><RefreshCw size={15} className={refreshing ? "spin" : ""} />Refresh</button>
          <button className="text-button desktop-only" type="button" title="Filter machines" aria-pressed={attentionOnly} onClick={() => setAttentionOnly((active) => !active)}><SlidersHorizontal size={15} />{attentionOnly ? "Needs attention" : "All machines"}</button>
        </div>
      </header>

      <div className="machine-table desktop-machine-table" role="table" aria-label="Synthetic machine status">
        <div className="machine-row machine-head" role="row">
          <span>Machine</span><span>State</span><span>Current job</span><span>Progress</span><span>Nozzle / Bed</span><span>Health</span><span />
        </div>
        {visibleMachines.map((machine) => (
          <div className="machine-row" role="row" key={machine.id}>
            <div className="machine-identity">
              <img src={IMAGE_BY_MACHINE[machine.id]} alt="" />
              <span><strong>{machine.name}</strong><small>{machine.process} · {machine.workspace_mm}</small></span>
            </div>
            <span className={`state-label ${machine.state}`}><span className={`status-dot ${machine.health}`} />{stateLabel(machine.state)}</span>
            <span className="job-cell"><strong>{machine.job?.reference ?? "—"}</strong><small>{machine.job?.part ?? "No job queued"}</small></span>
            <span className="progress-cell">
              <strong>{machine.job ? `${machine.job.progress_percent}%` : "—"}</strong>
              <span className="progress-track"><span style={{ width: `${machine.job?.progress_percent ?? 0}%` }} /></span>
            </span>
            <span>{temperature(machine.nozzle.current, machine.nozzle.target)} / {temperature(machine.bed.current, machine.bed.target)}</span>
            <span className={`health-label ${machine.health}`}><span className={`status-dot ${machine.health}`} />{machine.health === "healthy" ? "Healthy" : "Needs attention"}</span>
            <button className="icon-button" type="button" title={`Open ${machine.name}`} aria-label={`Open ${machine.name}`} onClick={() => setSelectedMachineId(machine.id)}><MoreVertical size={16} /></button>
          </div>
        ))}
      </div>

      <div className="mobile-machine-list">
        {visibleMachines.map((machine) => (
          <article className="mobile-machine" key={machine.id}>
            <div className="mobile-machine-main">
              <img src={IMAGE_BY_MACHINE[machine.id]} alt={`${machine.name} synthetic machine`} />
              <div className="mobile-machine-copy">
                <div><strong>{machine.name}</strong><span className={`state-label ${machine.state}`}><span className={`status-dot ${machine.health}`} />{stateLabel(machine.state)}</span></div>
                <span>{machine.job ? `Job: ${machine.job.reference}` : "No active job"}</span>
                <small>{machine.job?.material ?? machine.process}</small>
              </div>
              <button className="icon-button" type="button" title={`Open ${machine.name}`} aria-label={`Open ${machine.name}`} onClick={() => setSelectedMachineId(machine.id)}><ChevronRight size={20} /></button>
            </div>
            <div className="mobile-machine-progress">
              <span className="progress-track"><span style={{ width: `${machine.job?.progress_percent ?? 0}%` }} /></span>
              <strong>{machine.job?.progress_percent ?? 0}%</strong>
            </div>
            <div className="mobile-machine-stats">
              <span><Thermometer size={18} /><strong>{temperature(machine.nozzle.current, null)}</strong><small>Nozzle</small></span>
              <span><Thermometer size={18} /><strong>{temperature(machine.bed.current, null)}</strong><small>Bed</small></span>
              <span className={machine.health}><HeartPulse size={18} /><strong>{machine.health === "healthy" ? "Healthy" : "Check required"}</strong><small>{machine.status_message}</small></span>
            </div>
          </article>
        ))}
      </div>

      {selectedMachine ? (
        <div className="drawer-backdrop" role="presentation" onClick={() => setSelectedMachineId(null)}>
          <section className="machine-drawer" role="dialog" aria-modal="true" aria-labelledby="machine-drawer-title" onClick={(event) => event.stopPropagation()}>
            <header>
              <div><span className={`status-dot ${selectedMachine.health}`} /><h2 id="machine-drawer-title">{selectedMachine.name}</h2></div>
              <button className="icon-button" type="button" title="Close machine details" aria-label="Close machine details" onClick={() => setSelectedMachineId(null)}><X size={18} /></button>
            </header>
            <img src={IMAGE_BY_MACHINE[selectedMachine.id]} alt={`${selectedMachine.name} synthetic machine`} />
            <dl>
              <div><dt>Process</dt><dd>{selectedMachine.process}</dd></div>
              <div><dt>Workspace</dt><dd>{selectedMachine.workspace_mm} mm</dd></div>
              <div><dt>State</dt><dd>{stateLabel(selectedMachine.state)}</dd></div>
              <div><dt>Health</dt><dd>{selectedMachine.health === "healthy" ? "Healthy" : "Needs attention"}</dd></div>
              <div><dt>Current job</dt><dd>{selectedMachine.job?.reference ?? "No active job"}</dd></div>
              <div><dt>Status</dt><dd>{selectedMachine.status_message}</dd></div>
            </dl>
          </section>
        </div>
      ) : null}
    </section>
  );
}
