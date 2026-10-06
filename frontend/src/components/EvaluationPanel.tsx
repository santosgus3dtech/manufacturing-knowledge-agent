import { BarChart3, CheckCircle2, Target, XCircle } from "lucide-react";

import type { EvaluationSummary } from "../types";

interface EvaluationPanelProps {
  evaluation: EvaluationSummary | null;
}

export function EvaluationPanel({ evaluation }: EvaluationPanelProps) {
  if (!evaluation) return <section className="panel empty-state">Evaluation data is loading.</section>;
  return (
    <section className="evaluation-layout">
      <div className="evaluation-summary">
        <div><Target size={22} /><strong>{evaluation.cases}</strong><span>Versioned cases</span></div>
        <div><BarChart3 size={22} /><strong>{Math.round(evaluation.recall_at_3 * 100)}%</strong><span>Recall@3</span></div>
        <div><CheckCircle2 size={22} /><strong>{evaluation.mean_reciprocal_rank.toFixed(2)}</strong><span>Mean reciprocal rank</span></div>
      </div>
      <section className="panel evaluation-panel">
        <header className="panel-header"><div><BarChart3 size={18} /><h2>Retrieval evaluation cases</h2></div><span className="evaluation-target">Target ≥ 0.90</span></header>
        <div className="evaluation-table" role="table">
          <div className="evaluation-row evaluation-head"><span>Case</span><span>Question</span><span>Expected</span><span>Retrieved</span><span>Hit@3</span><span>RR</span></div>
          {evaluation.results.map((result) => (
            <div className="evaluation-row" key={result.id}>
              <code>{result.id}</code><span>{result.question}</span><span>{result.expected_document_ids.join(", ")}</span><span>{result.retrieved_document_ids.slice(0, 3).join(", ")}</span><span className={result.hit_at_3 ? "pass" : "fail"}>{result.hit_at_3 ? <CheckCircle2 size={16} /> : <XCircle size={16} />}{result.hit_at_3 ? "Pass" : "Fail"}</span><strong>{result.reciprocal_rank.toFixed(2)}</strong>
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
