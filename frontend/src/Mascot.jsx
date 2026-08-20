export default function Mascot({ state }) {
  // state: "idle" | "thinking" | "approve" | "escalate" | "block"
  const glow = {
    idle: "shadow-glowCyan border-cyan/50",
    thinking: "shadow-glowViolet border-violet/50",
    approve: "shadow-glowApprove border-approve/60",
    escalate: "shadow-glowEscalate border-escalate/60",
    block: "shadow-glowBlock border-block/60",
  }[state];

  const coreColor = {
    idle: "bg-cyan",
    thinking: "bg-violet",
    approve: "bg-approve",
    escalate: "bg-escalate",
    block: "bg-block",
  }[state];

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className={`relative w-16 h-16 rounded-full glass border-2 flex items-center justify-center transition-all duration-500 ${glow} ${
          state === "idle" ? "animate-pulse-glow" : ""
        }`}
      >
        <div
          className={`w-8 h-8 rounded-full ${coreColor} transition-colors duration-500 ${
            state === "thinking" ? "animate-spin-slow" : ""
          }`}
          style={{
            clipPath: state === "thinking" ? "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)" : "circle(50%)",
          }}
        />
        {/* eyes */}
        <div className="absolute top-5 flex gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-base" />
          <div className="w-1.5 h-1.5 rounded-full bg-base" />
        </div>
      </div>
      <span className="text-xs font-mono text-slate-400 tracking-wide">
        {{
          idle: "STANDBY",
          thinking: "ANALYZING",
          approve: "APPROVED",
          escalate: "ESCALATED",
          block: "BLOCKED",
        }[state]}
      </span>
    </div>
  );
}