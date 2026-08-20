export default function Footer() {
  return (
    <footer className="px-6 py-20 border-t border-slate-800/60">
      <div className="max-w-3xl mx-auto text-center">
        <div className="text-xs font-mono text-cyan uppercase tracking-widest mb-3">The Point</div>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-6 leading-tight">
          Not another agent that detects threats.
          <br />
          <span className="text-gradient">A safety layer for the ones that already do.</span>
        </h2>
        <p className="text-slate-400 leading-relaxed mb-10 max-w-xl mx-auto">
          As organizations hand more autonomy to AI-driven security response, almost nobody is
          building the layer that decides how much autonomy is actually safe to grant. ThresholdGuard
          sits between any detection system and the moment its response executes — locally,
          transparently, and without trusting a single model to get it right every time.
        </p>

        <div className="flex items-center justify-center gap-4 mb-14">
          <a
            href="#dashboard"
            className="glow-border-cyan glass rounded-lg px-6 py-3 font-mono text-sm text-cyan hover:shadow-glowCyan transition-all"
          >
            Explore the Console
          </a>
        </div>

        <div className="grid grid-cols-3 gap-4 max-w-lg mx-auto text-left mb-14">
          <div>
            <div className="text-xs font-mono text-slate-500 mb-1">STATUS</div>
            <div className="text-sm text-slate-300">v1.2 — evaluated prototype</div>
          </div>
          <div>
            <div className="text-xs font-mono text-slate-500 mb-1">INFERENCE</div>
            <div className="text-sm text-slate-300">100% local, zero external calls</div>
          </div>
          <div>
            <div className="text-xs font-mono text-slate-500 mb-1">STACK</div>
            <div className="text-sm text-slate-300">Ollama · OPA · FastAPI</div>
          </div>
        </div>

        <div className="text-xs text-slate-600 font-mono">
          ThresholdGuard — agentic AI security governance
        </div>
      </div>
    </footer>
  );
}