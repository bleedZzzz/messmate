import { MenuPlan } from "@/lib/schemas"
import { Calendar, Sparkles, RotateCcw, Moon, Sun } from "lucide-react"

export interface MenuGridProps {
  menu: MenuPlan
}

const DAY_NAMES = [
  "Monday (Day 1)",
  "Tuesday (Day 2)",
  "Wednesday (Day 3)",
  "Thursday (Day 4)",
  "Friday (Day 5)",
  "Saturday (Day 6)",
  "Sunday (Day 7)",
]

export function MenuGrid({ menu }: MenuGridProps) {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-orange-50/70 dark:bg-orange-950/20 border border-orange-200 dark:border-orange-900/40">
        <div>
          <h3 className="font-semibold text-stone-900 dark:text-stone-100 flex items-center gap-2 text-base">
            <Calendar className="w-4 h-4 text-orange-600" />
            7-Day Weekly Meal Rotation
          </h3>
          <p className="text-xs text-stone-600 dark:text-stone-400 mt-0.5">
            Balanced weekly schedule satisfying dietary constraints and slot variety
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          {menu.source === "llm" ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 dark:bg-violet-950 text-violet-700 dark:text-violet-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" /> AI Model Plan
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 text-xs font-semibold">
              <RotateCcw className="w-3.5 h-3.5" /> Deterministic Fallback Plan
            </span>
          )}
        </div>
      </div>

      {menu.rationale && (
        <p className="text-xs text-stone-600 dark:text-stone-400 italic px-2">
          &ldquo;{menu.rationale}&rdquo;
        </p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-7 gap-3">
        {menu.days.map((d) => {
          const dayTitle = DAY_NAMES[d.day - 1] || `Day ${d.day}`
          const isWeekend = d.day === 6 || d.day === 7

          return (
            <div
              key={d.day}
              className={`flex flex-col rounded-2xl border p-3.5 gap-3 transition-shadow hover:shadow-md ${
                isWeekend
                  ? "border-orange-200 dark:border-orange-900/40 bg-orange-50/20 dark:bg-orange-950/10"
                  : "border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900"
              }`}
            >
              <div className="flex items-center justify-between border-b border-stone-100 dark:border-stone-800/80 pb-2">
                <span className="font-bold text-xs text-stone-900 dark:text-stone-100">
                  {dayTitle.split(" ")[0]}
                </span>
                <span className="text-[10px] text-stone-400 font-medium">Day {d.day}</span>
              </div>

              {/* Lunch Pick */}
              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase tracking-wider font-semibold text-amber-700 dark:text-amber-400 flex items-center gap-1">
                  <Sun className="w-3 h-3" /> Lunch
                </span>
                <div className="p-2 rounded-xl bg-stone-50 dark:bg-stone-800/50 border border-stone-100 dark:border-stone-800 flex flex-col gap-0.5">
                  <span className="text-xs font-medium text-stone-900 dark:text-stone-100 leading-snug line-clamp-2">
                    {d.lunch.name}
                  </span>
                  <span className="text-[9px] font-mono text-stone-400 truncate">
                    #{d.lunch.dish_id.split("-").slice(-2).join("-")}
                  </span>
                </div>
              </div>

              {/* Dinner Pick */}
              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase tracking-wider font-semibold text-indigo-700 dark:text-indigo-400 flex items-center gap-1">
                  <Moon className="w-3 h-3" /> Dinner
                </span>
                <div className="p-2 rounded-xl bg-stone-50 dark:bg-stone-800/50 border border-stone-100 dark:border-stone-800 flex flex-col gap-0.5">
                  <span className="text-xs font-medium text-stone-900 dark:text-stone-100 leading-snug line-clamp-2">
                    {d.dinner.name}
                  </span>
                  <span className="text-[9px] font-mono text-stone-400 truncate">
                    #{d.dinner.dish_id.split("-").slice(-2).join("-")}
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
