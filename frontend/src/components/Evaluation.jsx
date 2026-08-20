const RESULTS = [
  {
    title: "Jailbreak Resistance",
    metric: "100%",
    submetric: "policy catch rate",
    color: "cyan",
    detail:
      "The LLM Advisor was fooled by adversarial prompts in 1/4 test cases (25%). The deterministic OPA policy layer still correctly blocked or escalated the action in 4/4 cases (100%) — regardless of what the LLM was tricked into recommending.",
  },
  {
    title: "Policy Robustness",
    metric: "0/6",
    submetric: "gaps after redesign",
    color: "violet",
    detail:
      "Initial denylist-based policy design had a real gap — action types not explicitly listed were auto-approved by default. Redesigned as an allowlist (fail-safe by default) and fixed a substring-matching bug. Re-tested: 0 gaps found across 6 adversarial probes.",
  },
  {
    title: "Two-Tier Supervisor",
    metric: "Validated",
    submetric: "weak vs. strong model",
    color: "approve",
    detail:
      "A fast/weak supervisor model failed to catch an obviously manipulated verdict. The stronger local supervisor correctly identified the mismatch between stated risk and the action's actual scope and irreversibility — proving supervisor capability matters, not just its presence.",
  },
  {
    title: "Log Injection Resistance",
    metric: "75%",
    submetric: "resistance rate, backstop closes rest",
    color: "escalate",
    detail:
      "The Blue Agent resisted 3/4 realistic manipulation attempts embedded directly in log content. The one successful manipulation was caught by a deterministic Detection Auditor backstop — a non-LLM signature scan that flags mismatches for mandatory human review.",
  },
  {
    title: "Cumulative Evasion Detection",
    metric: "Caught",
    submetric: "non-scripted adversarial test",
    color: "cyan",
    detail:
      "An autonomous planning agent — given only a harmful objective, no script — decided on its own to split it into 5 individually-approved actions. Each passed single-action review. The Pattern Auditor correctly flagged the cumulative pattern anyway.",
  },
  {
    title: "Audit Trail Integrity",
    metric: "Tamper-evident",
    submetric: "hash-chained records",
    color: "violet",
    detail:
      "Every governance decision is hash-chained to the previous record. A deliberate tampering test — directly modifying a stored record via SQL — was correctly detected, proving the integrity check works, not just that it exists.",
  },
];

const colorMap = {
  cyan: "text-cyan border-cyan/30 shadow-glowCyan",
  violet: "text-violet border-violet/30 shadow-glowViolet",
  approve: "text-approve border-approve/30 shadow-glowApprove",
  escalate: "text-escalate border-escalate/30 shadow-glowEscalate",
};

export default function Evaluation() {
  return (
    <section id="evaluation" className="px-6 py-24 border-t border-slate-800/60">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <div className="text-xs font-mono text-cyan uppercase tracking-widest mb-2">Evaluation</div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Every claim, backed by a test.
          </h2>
          <p className="text-slate-400 mt-3 max-w-xl mx-auto">
            Not benchmarks chosen to flatter the system — adversarial tests designed to
            break it, with the results reported either way.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {RESULTS.map((r, i) => (
            <div
              key={r.title}
              className={`glass rounded-2xl p-6 border hover:scale-[1.01] transition-transform duration-300 animate-fade-in-up ${colorMap[r.color].split(" ")[1]}`}
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="flex items-baseline justify-between mb-3">
                <h3 className="font-semibold text-slate-200">{r.title}</h3>
              </div>
              <div className="flex items-baseline gap-2 mb-4">
                <span className={`text-3xl font-bold ${colorMap[r.color].split(" ")[0]}`}>{r.metric}</span>
                <span className="text-xs text-slate-500 font-mono">{r.submetric}</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">{r.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}