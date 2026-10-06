import { BarChart3, Factory, FileSearch, TriangleAlert } from "lucide-react";

import type { DashboardSummary } from "../types";

interface MetricStripProps {
  summary: DashboardSummary;
}

export function MetricStrip({ summary }: MetricStripProps) {
  const metrics = [
    { label: "Machines", value: summary.machines, icon: Factory, tone: "default" },
    { label: "Needs attention", value: summary.needs_attention, icon: TriangleAlert, tone: "warning" },
    { label: "Knowledge chunks", value: summary.knowledge_chunks, icon: FileSearch, tone: "default" },
    { label: "Citation precision", value: `${Math.round(summary.citation_precision * 100)}%`, icon: BarChart3, tone: "default" },
  ];

  return (
    <section className="metric-strip" aria-label="Operations summary">
      {metrics.map(({ label, value, icon: Icon, tone }) => (
        <div className={`metric ${tone}`} key={label}>
          <Icon size={24} strokeWidth={1.8} />
          <div>
            <strong>{value}</strong>
            <span>{label}</span>
          </div>
        </div>
      ))}
    </section>
  );
}
