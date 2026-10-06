import { Search, Send, Sparkles } from "lucide-react";
import { useState, type FormEvent } from "react";

interface AgentComposerProps {
  loading: boolean;
  onAsk: (question: string) => Promise<void>;
}

export function AgentComposer({ loading, onAsk }: AgentComposerProps) {
  const [question, setQuestion] = useState("Why does Northstar Cell need attention?");

  async function submit(event: FormEvent) {
    event.preventDefault();
    const value = question.trim();
    if (value.length < 3 || loading) return;
    await onAsk(value);
  }

  return (
    <form className="agent-composer" onSubmit={submit}>
      <Search size={20} aria-hidden="true" />
      <input
        aria-label="Question for the manufacturing agent"
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="Ask about a machine, material, incident, or quote"
        maxLength={500}
      />
      <button className="primary-button" type="submit" disabled={loading || question.trim().length < 3}>
        {loading ? <Sparkles className="spin" size={18} /> : <Send size={18} />}
        <span>{loading ? "Working" : "Ask agent"}</span>
      </button>
    </form>
  );
}
