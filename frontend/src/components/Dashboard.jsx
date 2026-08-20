import { useState } from "react";
import Mascot from "./Mascot";

const API_BASE = "http://localhost:8000";
const API_KEY = "674653f092c20da7d2b18417a8173353147563c95797358e319120240b1ec2c1"; // must match backend/.env THRESHOLDGUARD_API_KEY

const decisionStyle = {
  auto_approve: "text-approve border-approve/40 bg-approve/10",
  escalate: "text-escalate border-escalate/40 bg-escalate/10",
  block: "text-block border-block/40 bg-block/10",
};

function DecisionBadge({ decision }) {
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-semibold border ${decisionStyle[decision] || "border-slate-600 text-slate-400"}`}>
      {decision?.toUpperCase()}
    </span>
  );
}

function EvidenceChainCard({ action, index }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="glass rounded-xl p-4 animate-fade-in-up" style={{ animationDelay: `${index * 80}ms` }}>
      <div className="flex items-center justify-between">
        <div>
          <div className="font-mono text-sm text-slate-300">{action.proposed_action?.action_type}</div>
          <div className="text-xs text-slate-500">{action.proposed_action?.target}</div>
        </div>
        <DecisionBadge decision={action.final_decision} />
      </div>

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-3 text-xs text-cyan hover:text-cyan/80 font-mono flex items-center gap-1"
      >
        {expanded ? "hide" : "show"} evidence chain →
      </button>

      {expanded && (
        <div className="mt-3 space-y-2 border-t border-slate-700/50 pt-3">
          <div className="text-xs">
            <span className="text-violet font-semibold">Advisor:</span>{" "}
            <span className="text-slate-400">{action.llm_advisory?.explanation}</span>
          </div>
          {action.supervisor_check && (
            <div className="text-xs">
              <span className="text-violet font-semibold">Supervisor:</span>{" "}
              <span className="text-slate-400">
                {action.supervisor_check.manipulation_suspected
                  ? `⚠ ${action.supervisor_check.concerns}`
                  : "reasoning holds up, no manipulation detected"}
              </span>
            </div>
          )}
          <div className="text-xs">
            <span className="text-cyan font-semibold">OPA (binding):</span>{" "}
            <span className="text-slate-400">{action.final_decision} — deterministic policy, not LLM-dependent</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [mascotState, setMascotState] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runInvestigation = async () => {
    setMascotState("thinking");
    setError(null);
    setResult(null);
    try {
      const resp = await fetch(`${API_BASE}/investigate`, {
        method: "POST",
        headers: { "x-api-key": API_KEY },
      });
      if (!resp.ok) throw new Error(`Request failed: ${resp.status}`);
      const data = await resp.json();
      setResult(data);

      const decisions = data.governed_actions?.map((a) => a.final_decision) || [];
      if (decisions.includes("block")) setMascotState("block");
      else if (decisions.includes("escalate")) setMascotState("escalate");
      else if (decisions.length > 0) setMascotState("approve");
      else setMascotState("idle");
    } catch (e) {
      setError(e.message);
      setMascotState("idle");
    }
  };

  return (
    <section id="dashboard" className="px-6 py-24 border-t border-slate-800/60">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-10">
          <div className="text-xs font-mono text-cyan uppercase tracking-widest mb-2">Live Console</div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">See it govern a real attack</h2>
          <p className="text-slate-400 mt-3">
            Runs the actual pipeline against a live sandboxed target — not a simulation of the demo.
          </p>
        </div>

        <div className="glass rounded-2xl p-8 flex flex-col items-center gap-6">
          <Mascot state={mascotState} />

          <button
            onClick={runInvestigation}
            disabled={mascotState === "thinking"}
            className="glow-border-cyan glass rounded-lg px-6 py-3 font-mono text-sm text-cyan hover:shadow-glowCyan transition-all disabled:opacity-50 w-full max-w-xs"
          >
            {mascotState === "thinking" ? "Running full pipeline..." : "▶ Run Investigation"}
          </button>

          {mascotState === "thinking" && (
            <p className="text-xs text-slate-500 font-mono text-center">
              Local CPU inference — the Supervisor tier can take several minutes.
            </p>
          )}
        </div>

        {error && (
          <div className="mt-4 glass border border-block/40 rounded-lg p-4 text-block text-sm font-mono">
            Error: {error}
          </div>
        )}

        {result && (
          <div className="mt-8 space-y-6">
            {result.pattern_audit?.cumulative_risk_flagged && (
              <div className="glass border border-escalate/50 rounded-xl p-4 shadow-glowEscalate">
                <div className="text-escalate font-semibold text-sm mb-1">⚠ Cumulative Risk Pattern Detected</div>
                {result.pattern_audit.patterns_detected.map((p, i) => (
                  <div key={i} className="text-xs text-slate-400">{p.explanation}</div>
                ))}
              </div>
            )}

            <div>
              <h3 className="text-sm font-mono text-slate-400 mb-3 uppercase tracking-wider">Governed Actions</h3>
              <div className="space-y-3">
                {result.blue_agent_status === "error" && (
                    <div className="glass border border-block/40 rounded-lg p-4 text-block text-sm font-mono">
                      ⚠ Blue Agent investigation failed to complete: {result.blue_agent_error}
                      <div className="text-xs text-slate-500 mt-1">
                        This is NOT "no threats found" — the analysis didn't finish. Likely cause: local model timeout under resource contention.
                      </div>
                    </div>
                  )}
                {result.governed_actions?.length ? (
                  result.governed_actions.map((action, i) => (
                    <EvidenceChainCard key={i} action={action} index={i} />
                  ))
                ) : (
                  <div className="text-sm text-slate-500 font-mono">No threats detected this run.</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}