import Link from "next/link"
import { Network, ArrowRight, ExternalLink } from "lucide-react"

export default function AboutPage() {
  return (
    <div className="flex flex-col gap-10 max-w-4xl mx-auto">
      {/* Title */}
      <div className="flex flex-col gap-2 text-center sm:text-left">
        <span className="text-xs font-bold uppercase tracking-wider text-orange-600">
          Under The Hood
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-stone-900 dark:text-stone-100">
          How MessMate Multi-Agent AI Works
        </h1>
        <p className="text-sm text-stone-600 dark:text-stone-400">
          A distributed multi-agent system solving the informal, unorganized tiffin market in Indian university towns.
        </p>
      </div>

      {/* Architecture Flow Diagram */}
      <section className="p-6 sm:p-8 rounded-3xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm flex flex-col gap-5">
        <h2 className="text-lg font-bold text-stone-900 dark:text-stone-100 flex items-center gap-2">
          <Network className="w-5 h-5 text-orange-600" />
          LangGraph Stateful Agent Pipeline
        </h2>

        {/* Visual Graph Diagram */}
        <div className="p-6 rounded-2xl bg-stone-50 dark:bg-stone-950/60 border border-stone-200 dark:border-stone-800/80 flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-medium">
          <div className="flex flex-col items-center gap-2 text-center p-3 rounded-xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 w-full md:w-36 shadow-xs">
            <span className="w-6 h-6 rounded-full bg-orange-100 dark:bg-orange-950 text-orange-600 font-bold flex items-center justify-center text-[11px]">
              1
            </span>
            <strong className="text-stone-900 dark:text-stone-100">Demand Agent</strong>
            <span className="text-[10px] text-stone-500">Geospatial Cluster Proximity</span>
          </div>

          <div className="text-stone-300 dark:text-stone-700 hidden md:block">→</div>

          <div className="flex flex-col items-center gap-2 text-center p-3 rounded-xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 w-full md:w-36 shadow-xs">
            <span className="w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-600 font-bold flex items-center justify-center text-[11px]">
              2
            </span>
            <strong className="text-stone-900 dark:text-stone-100">Match Agent</strong>
            <span className="text-[10px] text-stone-500">5-Factor Scoring (0-1)</span>
          </div>

          <div className="text-stone-300 dark:text-stone-700 hidden md:block">→</div>

          <div className="flex flex-col items-center gap-2 text-center p-3 rounded-xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 w-full md:w-36 shadow-xs">
            <span className="w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-950 text-violet-600 font-bold flex items-center justify-center text-[11px]">
              3
            </span>
            <strong className="text-stone-900 dark:text-stone-100">Menu Agent</strong>
            <span className="text-[10px] text-stone-500">LLM + Constraint Validator</span>
          </div>

          <div className="text-stone-300 dark:text-stone-700 hidden md:block">→</div>

          <div className="flex flex-col items-center gap-2 text-center p-3 rounded-xl bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 w-full md:w-36 shadow-xs">
            <span className="w-6 h-6 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-600 font-bold flex items-center justify-center text-[11px]">
              4
            </span>
            <strong className="text-stone-900 dark:text-stone-100">Deal Agent</strong>
            <span className="text-[10px] text-stone-500">Volume Negotiation Loop</span>
          </div>
        </div>
      </section>

      {/* The 4 Agents Deep Dive */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="p-6 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 flex flex-col gap-2.5">
          <span className="text-xs font-bold text-orange-600">01. DEMAND AGENT</span>
          <h3 className="font-bold text-base text-stone-900 dark:text-stone-100">
            Geospatial Student Belts
          </h3>
          <p className="text-xs text-stone-600 dark:text-stone-400 leading-relaxed">
            Identifies clusters around college hostels (headcount 8–80) using Haversine distance,
            diet distribution (e.g. 70% veg, 30% non-veg), and shared budget ceilings (₹2,000–₹3,500/mo).
          </p>
        </div>

        <div className="p-6 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 flex flex-col gap-2.5">
          <span className="text-xs font-bold text-emerald-600">02. MATCH AGENT</span>
          <h3 className="font-bold text-base text-stone-900 dark:text-stone-100">
            Deterministic 5-Factor Ranking
          </h3>
          <p className="text-xs text-stone-600 dark:text-stone-400 leading-relaxed">
            Scores providers on a 0–1 scale: Distance (30%), Cuisine Fit (25%), Price Ceiling Fit (25%),
            Available Capacity (15%), and Verified Rating (5%). Generates transparent natural language reasons.
          </p>
        </div>

        <div className="p-6 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 flex flex-col gap-2.5">
          <span className="text-xs font-bold text-violet-600">03. MENU AGENT</span>
          <h3 className="font-bold text-base text-stone-900 dark:text-stone-100">
            Constraint-Enforced Meal Rotation
          </h3>
          <p className="text-xs text-stone-600 dark:text-stone-400 leading-relaxed">
            Generates 14 meals (7 lunches, 7 dinners). Enforces zero slot repeats, veg ratio tolerance (±10%),
            and maximum 3 occurrences of any main ingredient. Automatically falls back to a deterministic planner if the LLM fails.
          </p>
        </div>

        <div className="p-6 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 flex flex-col gap-2.5">
          <span className="text-xs font-bold text-amber-600">04. DEAL AGENT</span>
          <h3 className="font-bold text-base text-stone-900 dark:text-stone-100">
            Game-Theoretic Negotiation
          </h3>
          <p className="text-xs text-stone-600 dark:text-stone-400 leading-relaxed">
            Simulates up to 5 rounds of price convergence between provider cost floor and student budget ceiling.
            Applies volume discounts (0%, 5%, 10%) based on group headcount with proven invariant guarantees.
          </p>
        </div>
      </section>

      {/* Tech Stack Details */}
      <section className="p-6 sm:p-8 rounded-3xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm flex flex-col gap-4">
        <h2 className="text-lg font-bold text-stone-900 dark:text-stone-100">Technology Stack</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div className="flex flex-col gap-1 p-3 rounded-xl bg-stone-50 dark:bg-stone-800/40">
            <span className="font-semibold text-stone-900 dark:text-stone-100">Backend API</span>
            <span className="text-stone-500">FastAPI, Python 3.12, Uvicorn, uv</span>
          </div>
          <div className="flex flex-col gap-1 p-3 rounded-xl bg-stone-50 dark:bg-stone-800/40">
            <span className="font-semibold text-stone-900 dark:text-stone-100">Agent Framework</span>
            <span className="text-stone-500">LangGraph (StateGraph), Pydantic v2</span>
          </div>
          <div className="flex flex-col gap-1 p-3 rounded-xl bg-stone-50 dark:bg-stone-800/40">
            <span className="font-semibold text-stone-900 dark:text-stone-100">Frontend UI</span>
            <span className="text-stone-500">Next.js 16, Tailwind CSS, 21st UI, TanStack Query</span>
          </div>
          <div className="flex flex-col gap-1 p-3 rounded-xl bg-stone-50 dark:bg-stone-800/40">
            <span className="font-semibold text-stone-900 dark:text-stone-100">Verification</span>
            <span className="text-stone-500">Pytest, Hypothesis, Vitest, Playwright</span>
          </div>
        </div>

        <div className="pt-4 border-t border-stone-100 dark:border-stone-800 flex items-center justify-between">
          <a
            href="https://github.com/bleedZzzz/messmate"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900 text-xs font-semibold hover:opacity-90 transition-opacity"
          >
            <span>View Source on GitHub</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <Link
            href="/"
            className="inline-flex items-center gap-1 text-xs font-semibold text-orange-600 hover:underline"
          >
            <span>Try Search Optimizer</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
