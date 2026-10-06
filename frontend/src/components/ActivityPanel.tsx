import { Activity, Check, Clock3, RefreshCw } from "lucide-react";

import type { ToolTrace } from "../types";

interface ActivityPanelProps {
  traces: ToolTrace[];
  expanded?: boolean;
}

export function ActivityPanel({ traces, expanded = false }: ActivityPanelProps) {
  return (
    <section className={expanded ? "panel activity-panel expanded" : "panel activity-panel"}>
      <header className="panel-header">
        <div><Activity size={18} /><h2>Agent tool activity</h2></div>
        <span className="live-label"><span className="status-dot healthy" />Live</span>
      </header>
      <div className="activity-table" role="table" aria-label="Agent tool activity">
        <div className="activity-row activity-head" role="row"><span>Time</span><span>Tool</span><span>Input</span><span>Result</span><span>Duration</span></div>
        {traces.slice(0, expanded ? 20 : 6).map((trace) => (
          <div className="activity-row" role="row" key={trace.id}>
            <span><Clock3 size={13} />{new Date(trace.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</span>
            <code>{trace.tool}</code>
            <span className="activity-input">{trace.input_summary}</span>
            <span className={`trace-result ${trace.result}`}>
              {trace.result === "success" ? <Check size={15} /> : <RefreshCw size={14} />}{trace.result}
            </span>
            <span>{trace.duration_ms} ms</span>
          </div>
        ))}
      </div>
    </section>
  );
}
