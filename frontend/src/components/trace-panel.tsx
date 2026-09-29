"use client"

import { useState } from "react"
import { TraceStep } from "@/lib/schemas"
import {
  Activity,
  Cpu,
  RotateCcw,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Terminal,
  Zap,
} from "lucide-react"

export interface AgentTracePanelProps {
  trace: TraceStep[]
  errors?: string[]
}

const AGENT_LABELS: Record<string, { title: string; desc: string }> = {
  demand: {
    title: "1. Demand Agent",
    desc: "Cluster selection & geospatial proximity filter",
  },
  match: {
    title: "2. Match Agent",
    desc: "5-factor multi-criteria scoring & rank filter",
  },
  menu: {
    title: "3. Menu Agent",
    desc: "7-day rotating meal plan with veg balance",
  },
  deal: {
    title: "4. Deal Agent",
    desc: "Autonomous price negotiation simulation",
  },
}

export function AgentTracePanel({ trace, errors = [] }: AgentTracePanelProps) {
  const [isOpen, setIsOpen] = useState(true)

  if (!trace || trace.length === 0) {
    return null
  }

  const totalDuration = trace.reduce((acc, step) => acc + step.duration_ms, 0)

  return (
    <div className="w-full rounded-2xl cyber-panel border border-white/[0.1] shadow-2xl overflow-hidden">
      {/* Telemetry Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-white/[0.03] transition-colors cursor-pointer group"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center shadow-[0_0_12px_rgba(245,158,11,0.2)] group-hover:scale-105 transition-transform">
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <h3 className="font-mono font-bold text-sm text-neutral-100 flex items-center gap-2">
              LangGraph Agent Observability Trace
              <span className="text-xs font-mono font-normal text-amber-400/90 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                ({trace.length} steps · {totalDuration}ms total)
              </span>
            </h3>
            <p className="text-[11px] text-neutral-400 font-mono flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Live multi-agent execution pipeline metrics
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-neutral-400 font-mono text-xs">
          <span className="hidden sm:inline">
            {isOpen ? "Hide Trace" : "Show Details"}
          </span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Expandable Trace Timeline Content */}
      {isOpen && (
        <div className="border-t border-white/[0.08] p-5 flex flex-col gap-4 bg-[#0a0c10]/80">
          {/* Agent Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {trace.map((step, index) => {
              const info = AGENT_LABELS[step.agent] || {
                title: `${index + 1}. ${step.agent} Agent`,
                desc: "Autonomous workflow node",
              }
              const hasError = !!step.error

              return (
                <div
                  key={`${step.agent}-${index}`}
                  className="p-4 rounded-xl border border-white/[0.08] bg-[#0e1117] flex flex-col justify-between gap-3 text-xs hover:border-amber-500/30 transition-all shadow-inner"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="font-mono font-bold text-neutral-100 block">
                        {info.title}
                      </span>
                      <span className="text-[10px] text-neutral-400 line-clamp-1 mt-0.5">
                        {info.desc}
                      </span>
                    </div>
                    {hasError ? (
                      <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                    <span className="font-mono text-xs text-neutral-300 font-semibold flex items-center gap-1">
                      <Zap className="w-3 h-3 text-amber-400" />
                      {step.duration_ms} ms
                    </span>

                    <div className="flex items-center gap-1.5">
                      {step.used_llm && (
                        <span
                          data-testid="badge-llm"
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-violet-500/15 border border-violet-500/30 text-violet-300 text-[10px] font-mono font-semibold"
                        >
                          <Cpu className="w-3 h-3 text-violet-400" /> LLM
                        </span>
                      )}
                      {step.fallback_used && (
                        <span
                          data-testid="badge-fallback"
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-mono font-semibold"
                        >
                          <RotateCcw className="w-3 h-3 text-amber-400" /> Fallback
                        </span>
                      )}
                      {!step.used_llm && !step.fallback_used && (
                        <span
                          data-testid="badge-deterministic"
                          className="inline-flex items-center px-2 py-0.5 rounded-md bg-white/[0.06] border border-white/[0.08] text-neutral-300 text-[10px] font-mono"
                        >
                          Deterministic
                        </span>
                      )}
                    </div>
                  </div>

                  {step.error && (
                    <div className="p-2.5 rounded-lg bg-red-950/40 border border-red-800/60 text-red-300 text-[11px] font-mono leading-tight">
                      {step.error}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Pipeline Warnings Alert */}
          {errors.length > 0 && (
            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs font-mono flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div className="flex flex-col gap-1">
                <span className="font-bold">Pipeline Partial Failure Warning:</span>
                <ul className="list-disc list-inside space-y-0.5 text-neutral-300">
                  {errors.map((e, idx) => (
                    <li key={idx}>{e}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
