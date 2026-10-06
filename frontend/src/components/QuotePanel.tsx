import { Calculator, RefreshCw } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { QuoteBreakdown, QuoteRequest } from "../types";

interface QuotePanelProps {
  quote: QuoteBreakdown | null;
  request: QuoteRequest;
  onEstimate: (request: QuoteRequest) => Promise<void>;
  editable?: boolean;
  onOpen?: () => void;
}

const ROWS: Array<[keyof QuoteBreakdown, string]> = [
  ["material_cost", "Material"],
  ["energy_cost", "Energy"],
  ["machine_cost", "Machine time"],
  ["labor_cost", "Labor"],
  ["packaging_cost", "Packaging"],
  ["risk_buffer", "Risk / contingency"],
];

export function QuotePanel({ quote, request, onEstimate, editable = false, onOpen }: QuotePanelProps) {
  const [draft, setDraft] = useState(request);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await onEstimate(draft);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className={editable ? "panel quote-panel expanded" : "panel quote-panel"}>
      <header className="panel-header">
        <div><Calculator size={18} /><h2>Quote breakdown</h2></div>
        {!editable && onOpen ? <button className="icon-button" type="button" title="Open quote calculator" aria-label="Open quote calculator" onClick={onOpen}><RefreshCw size={15} /></button> : null}
      </header>
      {editable ? (
        <form className="quote-form" onSubmit={submit}>
          <label>Material<select value={draft.material} onChange={(event) => setDraft({ ...draft, material: event.target.value })}><option>PLA</option><option>PETG</option><option>ABS</option><option>Tough Resin</option></select></label>
          <label>Part weight (g)<input type="number" min="1" value={draft.part_weight_g} onChange={(event) => setDraft({ ...draft, part_weight_g: Number(event.target.value) })} /></label>
          <label>Print hours<input type="number" min="0.1" step="0.1" value={draft.print_hours} onChange={(event) => setDraft({ ...draft, print_hours: Number(event.target.value) })} /></label>
          <label>Labor minutes<input type="number" min="0" value={draft.labor_minutes} onChange={(event) => setDraft({ ...draft, labor_minutes: Number(event.target.value) })} /></label>
          <label>Quantity<input type="number" min="1" value={draft.quantity} onChange={(event) => setDraft({ ...draft, quantity: Number(event.target.value) })} /></label>
          <label>Failure risk (%)<input type="number" min="0" max="99" value={draft.failure_rate_percent} onChange={(event) => setDraft({ ...draft, failure_rate_percent: Number(event.target.value) })} /></label>
          <button className="primary-button" type="submit" disabled={loading}><RefreshCw size={17} className={loading ? "spin" : ""} />Recalculate</button>
        </form>
      ) : null}
      {quote ? (
        <div className="quote-breakdown">
          <div className="quote-context"><strong>{quote.material}</strong><span>{quote.quantity} unit{quote.quantity === 1 ? "" : "s"}</span></div>
          {ROWS.map(([key, label]) => <div className="quote-row" key={key}><span>{label}</span><strong>${Number(quote[key]).toFixed(2)}</strong></div>)}
          <div className="quote-row quote-total"><span>Total (USD)</span><strong>${quote.total_price.toFixed(2)}</strong></div>
        </div>
      ) : <div className="empty-state">Quote data is loading.</div>}
    </section>
  );
}
