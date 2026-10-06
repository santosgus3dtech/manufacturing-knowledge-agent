import {
  BarChart3,
  BookOpen,
  Box,
  FileText,
  Gauge,
  PanelLeftClose,
  Wrench,
} from "lucide-react";
import type { ReactNode } from "react";

export type ViewName = "overview" | "knowledge" | "machines" | "quotes" | "evaluations";

interface AppShellProps {
  currentView: ViewName;
  onViewChange: (view: ViewName) => void;
  children: ReactNode;
}

const NAVIGATION = [
  { id: "overview" as const, label: "Overview", icon: Gauge },
  { id: "knowledge" as const, label: "Knowledge", icon: BookOpen },
  { id: "machines" as const, label: "Machines", icon: Wrench },
  { id: "quotes" as const, label: "Quotes", icon: FileText },
  { id: "evaluations" as const, label: "Evaluations", icon: BarChart3 },
];

export function AppShell({ currentView, onViewChange, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            <Box size={23} strokeWidth={2} />
          </span>
          <strong className="brand-full">Manufacturing Knowledge Agent</strong>
          <strong className="brand-short">MKA</strong>
          <span className="topbar-divider" />
          <span className="demo-status"><span className="status-dot healthy" />Synthetic demo</span>
        </div>
      </header>

      <aside className="sidebar" aria-label="Primary navigation">
        <nav>
          {NAVIGATION.map(({ id, label, icon: Icon }) => (
            <button
              className={currentView === id ? "nav-item active" : "nav-item"}
              key={id}
              type="button"
              onClick={() => onViewChange(id)}
            >
              <Icon size={18} strokeWidth={1.9} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <PanelLeftClose size={18} />
          <span>Portfolio demo<br />v0.1.0</span>
        </div>
      </aside>

      <main className="workspace">{children}</main>

      <nav className="bottom-nav" aria-label="Mobile navigation">
        {NAVIGATION.map(({ id, label, icon: Icon }) => (
          <button
            className={currentView === id ? "bottom-nav-item active" : "bottom-nav-item"}
            key={id}
            type="button"
            onClick={() => onViewChange(id)}
          >
            <Icon size={21} />
            <span>{label === "Evaluations" ? "Evals" : label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
