import { useState } from "react"
import { TraceStep } from "@/lib/schemas"
import { Activity, Cpu, RotateCcw, AlertTriangle, ChevronDown, ChevronUp, CheckCircle2 } from "lucide-react"

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
    <div className="w-full rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm overflow-hidden">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-stone-50 dark:hover:bg-stone-800/40 transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-950/60 text-orange-600 dark:text-orange-400 flex items-center justify-center">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-stone-900 dark:text-stone-100 flex items-center gap-2">
              LangGraph Agent Observability Trace
              <span className="text-xs font-normal text-stone-500">
                ({trace.length} steps · {totalDuration}ms total)
              </span>
            </h3>
            <p className="text-xs text-stone-500">
              Live multi-agent execution pipeline metrics
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-stone-400">
          <span className="text-xs hidden sm:inline">
            {isOpen ? "Hide Trace" : "Show Details"}
          </span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="border-t border-stone-100 dark:border-stone-800/80 px-5 py-4 flex flex-col gap-3">
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
                  className="p-3.5 rounded-xl border border-stone-100 dark:border-stone-800 bg-stone-50/60 dark:bg-stone-900/60 flex flex-col justify-between gap-3 text-xs"
                >
                  <div className="flex items-start justify-between gap-1.5">
                    <div>
                      <span className="font-medium text-stone-900 dark:text-stone-100 block">
                        {info.title}
                      </span>
                      <span className="text-[11px] text-stone-500 dark:text-stone-400 line-clamp-1">
                        {info.desc}
                      </span>
                    </div>
                    {hasError ? (
                      <AlertTriangle className="w-4 h-4 text-red-500 shrink-0" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-1 border-t border-stone-200/60 dark:border-stone-800/60">
                    <span className="font-mono text-stone-600 dark:text-stone-400">
                      {step.duration_ms} ms
                    </span>

                    <div className="flex items-center gap-1.5">
                      {step.used_llm && (
                        <span
                          data-testid="badge-llm"
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-violet-100 dark:bg-violet-950/60 text-violet-700 dark:text-violet-300 text-[10px] font-semibold"
                        >
                          <Cpu className="w-3 h-3" /> LLM
                        </span>
                      )}
                      {step.fallback_used && (
                        <span
                          data-testid="badge-fallback"
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 text-[10px] font-semibold"
                        >
                          <RotateCcw className="w-3 h-3" /> Fallback
                        </span>
                      )}
                      {!step.used_llm && !step.fallback_used && (
                        <span
                          data-testid="badge-deterministic"
                          className="inline-flex items-center px-1.5 py-0.5 rounded-md bg-stone-200/70 dark:bg-stone-800 text-stone-600 dark:text-stone-300 text-[10px] font-medium"
                        >
                          Deterministic
                        </span>
                      )}
                    </div>
                  </div>

                  {step.error && (
                    <div className="p-2 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 text-[11px] leading-tight">
                      {step.error}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {errors && errors.length > 0 && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex flex-col gap-1">
              <span className="font-semibold flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Pipeline Partial Failure Warning:
              </span>
              <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                {errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
