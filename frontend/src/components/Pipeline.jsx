import { useState } from "react";

const STAGES = [
  {
    id: "red",
    label: "Red / Adversarial Agent",
    color: "block",
    desc: "Executes real attacks (SQLi) against a sandboxed target, or autonomously plans how to split a harmful objective into evasive sub-actions.",
  },
  {
    id: "blue",
    label: "Blue Agent",
    color: "escalate",
    desc: "Custom agentic tool-calling loop (local Ollama, no framework dependency). Investigates logs, decides which tool to call, proposes a remediation action.",
  },
  {
    id: "governor",
    label: "Governor",
    color: "violet",
    desc: "Two-tier local LLM review: a fast Advisor gives a first-pass risk read, a stronger Supervisor cross-checks that reasoning for signs of manipulation.",
  },
  {
    id: "opa",
    label: "OPA Policy",
    color: "cyan",
    desc: "Deterministic Rego rules make the BINDING decision — auto_approve, escalate, or block. Cannot be talked out of its rules, even if both LLM tiers are fooled.",
  },
  {
    id: "auditor",
    label: "Pattern Auditor",
    color: "approve",
    desc: "Watches the rolling history of approved actions for cumulative-risk patterns — catching an objective split into many small, individually-approved pieces.",
  },
];

const colorMap = {
  block: { text: "text-block", border: "border-block/40", bg: "bg-block/10", glow: "shadow-glowBlock" },
  escalate: { text: "text-escalate", border: "border-escalate/40", bg: "bg-escalate/10", glow: "shadow-glowEscalate" },
  violet: { text: "text-violet", border: "border-violet/40", bg: "bg-violet/10", glow: "shadow-glowViolet" },
  cyan: { text: "text-cyan", border: "border-cyan/40", bg: "bg-cyan/10", glow: "shadow-glowCyan" },
  approve: { text: "text-approve", border: "border-approve/40", bg: "bg-approve/10", glow: "shadow-glowApprove" },
};

export default function Pipeline() {
  const [selected, setSelected] = useState(STAGES[2].id);

  const activeStage = STAGES.find((s) => s.id === selected);
  const c = colorMap[activeStage.color];

  return (
    <section id="pipeline" className="px-6 py-24 border-t border-slate-800/60">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <div className="text-xs font-mono text-cyan uppercase tracking-widest mb-2">Architecture</div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Five stages. One question at the center.
          </h2>
          <p className="text-slate-400 mt-3 max-w-xl mx-auto">
            Not every stage is the contribution — the Governor and Pattern Auditor are.
            The rest is the test harness that proves they work.
          </p>
        </div>

        <div className="relative flex items-center justify-between mb-4">
          <div className="absolute left-0 right-0 top-1/2 h-px bg-slate-700/60 -translate-y-1/2" />
          {STAGES.map((stage) => {
            const sc = colorMap[stage.color];
            const isActive = selected === stage.id;
            return (
              <button
                key={stage.id}
                onClick={() => setSelected(stage.id)}
                className="relative z-10 flex flex-col items-center gap-2 group"
              >
                <div
                  className={
                    isActive
                      ? `w-4 h-4 rounded-full border-2 transition-all duration-300 ${sc.border} ${sc.bg} ${sc.glow}`
                      : "w-4 h-4 rounded-full border-2 transition-all duration-300 border-slate-600 bg-base group-hover:border-slate-400"
                  }
                />
                <span
                  className={
                    isActive
                      ? `text-xs font-mono hidden md:block transition-colors ${sc.text}`
                      : "text-xs font-mono hidden md:block transition-colors text-slate-500 group-hover:text-slate-300"
                  }
                >
                  {stage.label.split(" ")[0]}
                </span>
              </button>
            );
          })}
        </div>

        <div className={`glass rounded-2xl p-8 mt-10 border ${c.border} transition-all duration-300 animate-fade-in-up`} key={selected}>
          <div className={`inline-block text-xs font-mono px-2.5 py-1 rounded-full ${c.bg} ${c.text} mb-4`}>
            Stage {STAGES.findIndex((s) => s.id === selected) + 1} / {STAGES.length}
          </div>
          <h3 className={`text-2xl font-bold mb-3 ${c.text}`}>{activeStage.label}</h3>
          <p className="text-slate-300 leading-relaxed">{activeStage.desc}</p>
        </div>
      </div>
    </section>
  );
}