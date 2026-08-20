export default function Mascot({ state }) {
  const ring = {
    idle: "border-cyan/50 shadow-glowCyan",
    thinking: "border-violet/50 shadow-glowViolet",
    approve: "border-approve/60 shadow-glowApprove",
    escalate: "border-escalate/60 shadow-glowEscalate",
    block: "border-block/60 shadow-glowBlock",
  }[state];

  const core = {
    idle: "bg-cyan",
    thinking: "bg-violet",
    approve: "bg-approve",
    escalate: "bg-escalate",
    block: "bg-block",
  }[state];

  const label = {
    idle: "STANDBY",
    thinking: "ANALYZING",
    approve: "APPROVED",
    escalate: "ESCALATED",
    block: "BLOCKED",
  }[state];

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`relative w-14 h-14 rounded-full glass border-2 flex items-center justify-center transition-all duration-500 ${ring} ${state === "idle" ? "animate-pulse-glow" : ""}`}>
        <div className={`w-7 h-7 rounded-full ${core} transition-colors duration-500 ${state === "thinking" ? "animate-spin-slow" : ""}`} />
        <div className="absolute top-4 flex gap-1.5">
          <div className="w-1 h-1 rounded-full bg-base" />
          <div className="w-1 h-1 rounded-full bg-base" />
        </div>
      </div>
      <span className="text-[10px] font-mono text-slate-400 tracking-widest">{label}</span>
    </div>
  );
}