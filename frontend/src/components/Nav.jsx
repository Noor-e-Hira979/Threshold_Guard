export default function Nav({ active, setActive }) {
  const links = [
    { id: "home", label: "Overview" },
    { id: "pipeline", label: "Architecture" },
    { id: "dashboard", label: "Live Console" },
    { id: "evaluation", label: "Evaluation" },
  ];

  const goTo = (id) => {
    setActive(id);
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (id === "home") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <nav className="sticky top-0 z-50 glass border-b border-slate-800/60 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan to-violet flex items-center justify-center text-base font-bold text-sm">
            TG
          </div>
          <span className="font-bold tracking-tight text-slate-100">
            Threshold<span className="text-cyan">Guard</span>
          </span>
        </div>

        <div className="hidden md:flex items-center gap-1">
          {links.map((link) => (
            <button
              key={link.id}
              onClick={() => goTo(link.id)}
              className={
                active === link.id
                  ? "px-4 py-2 rounded-lg text-sm font-medium transition-all text-cyan bg-cyan/10 border border-cyan/30"
                  : "px-4 py-2 rounded-lg text-sm font-medium transition-all text-slate-400 hover:text-slate-200"
              }
            >
              {link.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => goTo("dashboard")}
          className="glow-border-cyan glass rounded-lg px-4 py-2 text-sm font-mono text-cyan hover:shadow-glowCyan transition-all"
        >
          Launch Console
        </button>
      </div>
    </nav>
  );
}