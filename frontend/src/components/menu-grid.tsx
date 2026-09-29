import { MenuPlan } from "@/lib/schemas"
import { Calendar, Sparkles, RotateCcw, Moon, Sun, Utensils, CheckCircle } from "lucide-react"

export interface MenuGridProps {
  menu: MenuPlan
}

const DAY_NAMES = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
]

export function MenuGrid({ menu }: MenuGridProps) {
  return (
    <div className="flex flex-col gap-6">
      {/* Top Banner with AI Verification State */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl cyber-panel border border-white/[0.08] bg-[#0c0e14]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center shrink-0">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-mono font-bold text-white text-base flex items-center gap-2">
              7-Day Rotating Weekly Meal Schedule
            </h3>
            <p className="text-xs text-neutral-400 font-mono mt-0.5">
              14 unique slot meals · Zero repeat within 7-day window · Balanced veg/protein ratios
            </p>
          </div>
        </div>

        <div className="self-start sm:self-auto">
          {menu.source === "llm" ? (
            <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-violet-500/15 border border-violet-500/30 text-violet-300 font-mono text-xs font-bold shadow-[0_0_15px_rgba(139,92,246,0.2)]">
              <Sparkles className="w-3.5 h-3.5 text-violet-400" /> AI LLM Structured Plan
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 font-mono text-xs font-bold shadow-[0_0_15px_rgba(245,158,11,0.2)]">
              <RotateCcw className="w-3.5 h-3.5 text-amber-400" /> Deterministic Rotation Engine
            </span>
          )}
        </div>
      </div>

      {/* Rationale Quote */}
      {menu.rationale && (
        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] text-xs font-mono text-neutral-300 flex items-start gap-2.5">
          <span className="text-amber-400 font-bold shrink-0">AI RATIONALE //</span>
          <span className="italic leading-relaxed">&ldquo;{menu.rationale}&rdquo;</span>
        </div>
      )}

      {/* 7-Day Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3.5">
        {menu.days.map((d) => {
          const dayName = DAY_NAMES[d.day - 1] || `Day ${d.day}`
          const isWeekend = d.day === 6 || d.day === 7

          return (
            <div
              key={d.day}
              className={`flex flex-col rounded-2xl cyber-panel border p-4 gap-3.5 transition-all hover:border-amber-500/40 hover:-translate-y-0.5 ${
                isWeekend
                  ? "border-amber-500/30 bg-amber-500/[0.03]"
                  : "border-white/[0.08] bg-[#0c0e14]/90"
              }`}
            >
              {/* Day Header */}
              <div className="flex items-center justify-between border-b border-white/[0.06] pb-2.5">
                <span className="font-mono font-bold text-xs text-white">
                  {dayName}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white/[0.05] text-amber-400">
                  D{d.day}
                </span>
              </div>

              {/* Lunch Slot */}
              <div className="flex flex-col gap-1.5">
                <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-amber-400 flex items-center gap-1">
                  <Sun className="w-3 h-3 text-amber-400" /> Lunch
                </span>
                <div className="p-3 rounded-xl bg-[#12141c] border border-white/[0.06] flex flex-col gap-1 shadow-inner">
                  <span className="text-xs font-medium text-neutral-100 leading-snug">
                    {d.lunch.name}
                  </span>
                  <span className="text-[9px] font-mono text-neutral-500">
                    ID: #{d.lunch.dish_id.split("-").slice(-1)[0]}
                  </span>
                </div>
              </div>

              {/* Dinner Slot */}
              <div className="flex flex-col gap-1.5">
                <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-violet-400 flex items-center gap-1">
                  <Moon className="w-3 h-3 text-violet-400" /> Dinner
                </span>
                <div className="p-3 rounded-xl bg-[#12141c] border border-white/[0.06] flex flex-col gap-1 shadow-inner">
                  <span className="text-xs font-medium text-neutral-100 leading-snug">
                    {d.dinner.name}
                  </span>
                  <span className="text-[9px] font-mono text-neutral-500">
                    ID: #{d.dinner.dish_id.split("-").slice(-1)[0]}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
