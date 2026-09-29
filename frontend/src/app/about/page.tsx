import Link from "next/link"
import {
  Network,
  ArrowRight,
  ExternalLink,
  Cpu,
  ShieldCheck,
  Zap,
  Terminal,
  Layers,
  Sparkles,
  GitBranch,
} from "lucide-react"

export default function AboutPage() {
  return (
    <div className="flex flex-col gap-10 max-w-4xl mx-auto py-2">
      {/* Title */}
      <div className="flex flex-col gap-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-mono text-[11px] uppercase font-bold w-fit">
          <Terminal className="w-3.5 h-3.5 text-amber-400" />
          <span>LangGraph Multi-Agent Architecture</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black text-white">
          Under the Hood: <span className="gradient-text-cyber">MessMate AI Swarm</span>
        </h1>
        <p className="text-sm text-neutral-400 leading-relaxed max-w-2xl font-mono">
          Stateful multi-agent system addressing the unorganized student mess market across West Bengal and Indian college towns.
        </p>
      </div>

      {/* Architecture Flow Diagram */}
      <section className="p-6 sm:p-8 rounded-3xl cyber-panel border border-white/[0.1] shadow-2xl flex flex-col gap-6">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
          <h2 className="text-base font-bold font-mono text-white flex items-center gap-2">
            <Network className="w-4 h-4 text-amber-400" />
            LangGraph Stateful Agent Pipeline
          </h2>
          <span className="text-[11px] font-mono text-neutral-500">
            Autonomous Node Progression
          </span>
        </div>

        {/* Visual Graph Diagram */}
        <div className="p-6 rounded-2xl bg-[#0c0e14] border border-white/[0.08] flex flex-col md:flex-row items-center justify-between gap-4 font-mono">
          <div className="flex flex-col items-center gap-2 text-center p-4 rounded-xl bg-[#12141c] border border-amber-500/30 w-full md:w-40 shadow-inner">
            <span className="w-7 h-7 rounded-lg bg-amber-500/15 border border-amber-500/30 text-amber-400 font-bold flex items-center justify-center text-xs">
              01
            </span>
            <strong className="text-white text-xs">Demand Agent</strong>
            <span className="text-[10px] text-neutral-400">Centroid & Headcount</span>
          </div>

          <div className="text-amber-500/60 hidden md:block">➔</div>

          <div className="flex flex-col items-center gap-2 text-center p-4 rounded-xl bg-[#12141c] border border-emerald-500/30 w-full md:w-40 shadow-inner">
            <span className="w-7 h-7 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-bold flex items-center justify-center text-xs">
              02
            </span>
            <strong className="text-white text-xs">Match Agent</strong>
            <span className="text-[10px] text-neutral-400">5-Factor Scoring</span>
          </div>

          <div className="text-emerald-500/60 hidden md:block">➔</div>

          <div className="flex flex-col items-center gap-2 text-center p-4 rounded-xl bg-[#12141c] border border-violet-500/30 w-full md:w-40 shadow-inner">
            <span className="w-7 h-7 rounded-lg bg-violet-500/15 border border-violet-500/30 text-violet-400 font-bold flex items-center justify-center text-xs">
              03
            </span>
            <strong className="text-white text-xs">Menu Agent</strong>
            <span className="text-[10px] text-neutral-400">14-Meal Constraint</span>
          </div>

          <div className="text-violet-500/60 hidden md:block">➔</div>

          <div className="flex flex-col items-center gap-2 text-center p-4 rounded-xl bg-[#12141c] border border-cyan-500/30 w-full md:w-40 shadow-inner">
            <span className="w-7 h-7 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-400 font-bold flex items-center justify-center text-xs">
              04
            </span>
            <strong className="text-white text-xs">Deal Agent</strong>
            <span className="text-[10px] text-neutral-400">Game Theory Loop</span>
          </div>
        </div>
      </section>

      {/* The 4 Agents Deep Dive */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="p-6 rounded-2xl cyber-panel border border-white/[0.08] hover:border-amber-500/40 transition-all flex flex-col gap-2.5">
          <span className="text-xs font-mono font-bold text-amber-400">01. DEMAND AGENT</span>
          <h3 className="font-bold text-base text-white">
            Geospatial Student Belts
          </h3>
          <p className="text-xs text-neutral-400 leading-relaxed font-mono">
            Locates demand clusters around hostel belts (headcount 8–80) using Haversine centroid distance, dietary preferences (veg, non-veg, egg ratios), and shared budget ceilings (₹2,000–₹3,500/mo).
          </p>
        </div>

        <div className="p-6 rounded-2xl cyber-panel border border-white/[0.08] hover:border-emerald-500/40 transition-all flex flex-col gap-2.5">
          <span className="text-xs font-mono font-bold text-emerald-400">02. MATCH AGENT</span>
          <h3 className="font-bold text-base text-white">
            Deterministic 5-Factor Ranking
          </h3>
          <p className="text-xs text-neutral-400 leading-relaxed font-mono">
            Ranks providers on an auditable 0.00–1.00 scale: Distance (30%), Cuisine Fit (25%), Price Ceiling Fit (25%), Available Capacity (15%), and Verified Rating (5%). Zero LLM variance.
          </p>
        </div>

        <div className="p-6 rounded-2xl cyber-panel border border-white/[0.08] hover:border-violet-500/40 transition-all flex flex-col gap-2.5">
          <span className="text-xs font-mono font-bold text-violet-400">03. MENU AGENT</span>
          <h3 className="font-bold text-base text-white">
            Constraint-Enforced Meal Rotation
          </h3>
          <p className="text-xs text-neutral-400 leading-relaxed font-mono">
            Produces 14 slot meals (7 lunches, 7 dinners). Enforces zero slot repeats, veg ratio tolerance (±10%), and max 3 occurrences of any main ingredient. Deterministic fallback planner activates on LLM failure.
          </p>
        </div>

        <div className="p-6 rounded-2xl cyber-panel border border-white/[0.08] hover:border-cyan-500/40 transition-all flex flex-col gap-2.5">
          <span className="text-xs font-mono font-bold text-cyan-400">04. DEAL AGENT</span>
          <h3 className="font-bold text-base text-white">
            Game-Theoretic Negotiation
          </h3>
          <p className="text-xs text-neutral-400 leading-relaxed font-mono">
            Simulates up to 5 bargaining rounds between provider cost floors and student budget ceilings. Applies headcount volume discounts (0%, 5%, 10%) with invariant boundary guarantees.
          </p>
        </div>
      </section>

      {/* Tech Stack Details */}
      <section className="p-6 sm:p-8 rounded-3xl cyber-panel border border-white/[0.1] shadow-2xl flex flex-col gap-5">
        <h2 className="text-base font-bold font-mono text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-amber-400" />
          Production Engineering Stack
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
          <div className="flex flex-col gap-1 p-3.5 rounded-xl bg-[#0c0e14] border border-white/[0.06]">
            <span className="font-bold text-white">Backend</span>
            <span className="text-neutral-400 text-[11px]">FastAPI, Python 3.12, Uvicorn, uv</span>
          </div>
          <div className="flex flex-col gap-1 p-3.5 rounded-xl bg-[#0c0e14] border border-white/[0.06]">
            <span className="font-bold text-white">Orchestration</span>
            <span className="text-neutral-400 text-[11px]">LangGraph Swarm, Pydantic v2</span>
          </div>
          <div className="flex flex-col gap-1 p-3.5 rounded-xl bg-[#0c0e14] border border-white/[0.06]">
            <span className="font-bold text-white">Frontend</span>
            <span className="text-neutral-400 text-[11px]">Next.js 16, Tailwind CSS, TanStack Query</span>
          </div>
          <div className="flex flex-col gap-1 p-3.5 rounded-xl bg-[#0c0e14] border border-white/[0.06]">
            <span className="font-bold text-white">Assurance</span>
            <span className="text-neutral-400 text-[11px]">Pytest, Hypothesis, Vitest, Playwright</span>
          </div>
        </div>

        <div className="pt-4 border-t border-white/[0.08] flex items-center justify-between">
          <a
            href="https://github.com/bleedZzzz/messmate"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-neutral-900 border border-white/[0.12] text-white font-mono text-xs font-bold hover:border-amber-500/40 hover:text-amber-300 transition-all"
          >
            <span>GitHub Repository</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-amber-400 hover:text-amber-300 transition-colors"
          >
            <span>Launch Live Swarm</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
