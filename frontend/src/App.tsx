import { Activity, BookOpen, Factory } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "./api";
import { ActivityPanel } from "./components/ActivityPanel";
import { AgentComposer } from "./components/AgentComposer";
import { AppShell, type ViewName } from "./components/AppShell";
import { EvaluationPanel } from "./components/EvaluationPanel";
import { EvidencePanel } from "./components/EvidencePanel";
import { MachineTable } from "./components/MachineTable";
import { MetricStrip } from "./components/MetricStrip";
import { QuotePanel } from "./components/QuotePanel";
import type {
  AskResponse,
  Citation,
  DashboardSummary,
  EvaluationSummary,
  Machine,
  QuoteBreakdown,
  QuoteRequest,
  ToolTrace,
} from "./types";

const DEFAULT_QUOTE: QuoteRequest = {
  material: "PETG",
  part_weight_g: 72,
  print_hours: 3.5,
  labor_minutes: 18,
  quantity: 1,
  failure_rate_percent: 8,
  margin_percent: 35,
};

const VIEW_COPY: Record<ViewName, { title: string; subtitle: string }> = {
  overview: { title: "Operations workspace", subtitle: "Query operational data, documentation and past experience across your 3D printing operation." },
  knowledge: { title: "Knowledge", subtitle: "Grounded answers with inspectable sources and page-level citations." },
  machines: { title: "Machines", subtitle: "Normalized synthetic telemetry across FDM and SLA equipment." },
  quotes: { title: "Quotes", subtitle: "Deterministic cost calculation with an explicit risk buffer and margin." },
  evaluations: { title: "Evaluations", subtitle: "Versioned retrieval checks that run against every change." },
};

type MobileTab = "machines" | "evidence" | "activity";

function App() {
  const [view, setView] = useState<ViewName>("overview");
  const [mobileTab, setMobileTab] = useState<MobileTab>("machines");
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [activity, setActivity] = useState<ToolTrace[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
  const [quote, setQuote] = useState<QuoteBreakdown | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [answer, setAnswer] = useState<AskResponse | null>(null);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const [dashboard, machineData, toolActivity, evalData, quoteData, searchData] = await Promise.all([
          api.dashboard(),
          api.machines(),
          api.activity(),
          api.evaluations(),
          api.quote(DEFAULT_QUOTE),
          api.search("Northstar Cell resin flow fault"),
        ]);
        if (!active) return;
        setSummary(dashboard);
        setMachines(machineData);
        setActivity(toolActivity);
        setEvaluation(evalData);
        setQuote(quoteData);
        setCitations(searchData.results);
      } catch (loadError) {
        if (active) setError(loadError instanceof Error ? loadError.message : "Unable to load the workspace");
      }
    }
    void load();
    return () => { active = false; };
  }, []);

  async function ask(question: string) {
    setAsking(true);
    setError(null);
    try {
      const response = await api.ask(question);
      setAnswer(response);
      setCitations(response.citations);
      setActivity(await api.activity());
      setMobileTab("evidence");
    } catch (askError) {
      setError(askError instanceof Error ? askError.message : "The agent could not answer");
    } finally {
      setAsking(false);
    }
  }

  async function estimate(request: QuoteRequest) {
    setError(null);
    try {
      setQuote(await api.quote(request));
    } catch (quoteError) {
      setError(quoteError instanceof Error ? quoteError.message : "The quote could not be calculated");
    }
  }

  async function refreshMachines() {
    setError(null);
    try {
      const [machineData, dashboard] = await Promise.all([api.machines(), api.dashboard()]);
      setMachines(machineData);
      setSummary(dashboard);
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : "Machine status could not be refreshed");
    }
  }

  const copy = VIEW_COPY[view];

  return (
    <AppShell currentView={view} onViewChange={setView}>
      <header className="workspace-heading">
        <h1>{copy.title}</h1>
        <p>{copy.subtitle}</p>
      </header>

      {error ? <div className="error-banner" role="alert">{error}</div> : null}

      {(view === "overview" || view === "knowledge") ? <AgentComposer loading={asking} onAsk={ask} /> : null}

      {view === "overview" && summary ? (
        <>
          <MetricStrip summary={summary} />
          <div className="mobile-section-tabs" role="tablist" aria-label="Overview sections">
            <button className={mobileTab === "machines" ? "active" : ""} onClick={() => setMobileTab("machines")} type="button"><Factory size={18} />Machines</button>
            <button className={mobileTab === "evidence" ? "active" : ""} onClick={() => setMobileTab("evidence")} type="button"><BookOpen size={18} />Evidence</button>
            <button className={mobileTab === "activity" ? "active" : ""} onClick={() => setMobileTab("activity")} type="button"><Activity size={18} />Activity</button>
          </div>
          <div className="overview-grid">
            <div className="overview-main">
              <div className={`mobile-pane ${mobileTab === "machines" ? "active" : ""}`}><MachineTable machines={machines} onRefresh={refreshMachines} /></div>
              <div className={`mobile-pane ${mobileTab === "activity" ? "active" : ""}`}><ActivityPanel traces={activity} /></div>
            </div>
            <aside className="overview-inspector">
              <div className={`mobile-pane ${mobileTab === "evidence" ? "active" : ""}`}><EvidencePanel response={answer} initialCitations={citations} onExpand={() => setView("knowledge")} /></div>
              <div className="desktop-only"><QuotePanel quote={quote} request={DEFAULT_QUOTE} onEstimate={estimate} onOpen={() => setView("quotes")} /></div>
            </aside>
          </div>
        </>
      ) : null}

      {view === "knowledge" ? <EvidencePanel response={answer} initialCitations={citations} expanded /> : null}
      {view === "machines" ? <MachineTable machines={machines} onRefresh={refreshMachines} expanded /> : null}
      {view === "quotes" ? <QuotePanel quote={quote} request={DEFAULT_QUOTE} onEstimate={estimate} editable /> : null}
      {view === "evaluations" ? <EvaluationPanel evaluation={evaluation} /> : null}
    </AppShell>
  );
}

export default App;
