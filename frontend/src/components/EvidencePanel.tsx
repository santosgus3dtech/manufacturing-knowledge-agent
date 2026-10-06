import { ArrowUpRight, BookOpen, ChevronDown, ChevronRight, ShieldCheck } from "lucide-react";
import { useState } from "react";

import type { AskResponse, Citation } from "../types";

interface EvidencePanelProps {
  response: AskResponse | null;
  initialCitations: Citation[];
  expanded?: boolean;
  onExpand?: () => void;
}

export function EvidencePanel({ response, initialCitations, expanded = false, onExpand }: EvidencePanelProps) {
  const citations = response?.citations ?? initialCitations;
  const [selectedCitation, setSelectedCitation] = useState<string | null>(null);
  return (
    <section className={expanded ? "panel evidence-panel expanded" : "panel evidence-panel"}>
      <header className="panel-header">
        <div><BookOpen size={18} /><h2>{response ? "Grounded answer" : "Retrieved evidence"}</h2></div>
        {onExpand ? <button className="icon-button" type="button" title="Expand evidence" aria-label="Expand evidence" onClick={onExpand}><ArrowUpRight size={16} /></button> : null}
      </header>
      {response ? (
        <div className="answer-block">
          <div className="answer-meta"><ShieldCheck size={16} /><span>{Math.round(response.confidence * 100)}% confidence</span><span>{response.provider}</span></div>
          <p>{response.answer}</p>
        </div>
      ) : null}
      <div className="evidence-list">
        {citations.length ? citations.slice(0, expanded ? 10 : 5).map((citation, index) => {
          const citationKey = `${citation.document_id}-${citation.page}`;
          const isOpen = expanded || selectedCitation === citationKey;
          return (
          <button
            className="evidence-row"
            type="button"
            key={citationKey}
            aria-expanded={isOpen}
            onClick={() => setSelectedCitation(isOpen && !expanded ? null : citationKey)}
          >
            <span className="evidence-index">{index + 1}</span>
            <span className="evidence-copy">
              <strong>{citation.document_id} · page {citation.page}</strong>
              <small>{citation.title}</small>
              {isOpen ? <span>{citation.excerpt}</span> : null}
            </span>
            <span className="relevance">{citation.score.toFixed(2)}</span>
            {isOpen ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
          </button>
          );
        }) : (
          <div className="empty-state">Ask the agent to retrieve cited evidence.</div>
        )}
      </div>
    </section>
  );
}
