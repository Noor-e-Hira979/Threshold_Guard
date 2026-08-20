export default function Hero({ setActive }) {
  return (
    <section className="relative overflow-hidden px-6 pt-20 pb-24">
      <div className="absolute top-10 left-1/4 w-72 h-72 bg-cyan/10 rounded-full blur-3xl animate-float" />
      <div className="absolute top-40 right-1/4 w-72 h-72 bg-violet/10 rounded-full blur-3xl animate-float" style={{ animationDelay: "1.5s" }} />

      <div className="relative max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-1.5 mb-6 text-xs font-mono text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full bg-approve animate-pulse" />
          Fully local inference — zero data leaves the system
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight leading-tight mb-6">
          Autonomous agents are acting.
          <br />
          <span className="text-gradient">Who decides if it's safe?</span>
        </h1>

        <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          ThresholdGuard is a governance layer for autonomous security agents — evaluating
          every proposed action through a two-tier LLM review and a deterministic policy
          engine that can't be talked out of its rules, even if the AI is manipulated.
        </p>

        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => setActive("dashboard")}
            className="glow-border-cyan glass rounded-lg px-6 py-3 font-mono text-sm text-cyan hover:shadow-glowCyan transition-all"
          >
            ▶ Try the Live Console
          </button>
          <button
            onClick={() => setActive("evaluation")}
            className="rounded-lg px-6 py-3 font-mono text-sm text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-500 transition-all"
          >
            View Evaluation Results
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-16 max-w-2xl mx-auto">
          <div className="glass rounded-xl p-4">
            <div className="text-2xl font-bold text-approve">100%</div>
            <div className="text-xs text-slate-500 mt-1 font-mono">policy catch rate<br />even when LLM is fooled</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="text-2xl font-bold text-cyan">2-tier</div>
            <div className="text-xs text-slate-500 mt-1 font-mono">local LLM review<br />+ deterministic policy</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="text-2xl font-bold text-violet">0/6</div>
            <div className="text-xs text-slate-500 mt-1 font-mono">policy gaps after<br />adversarial testing</div>
          </div>
        </div>
      </div>
    </section>
  );
}