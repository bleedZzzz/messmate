"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import {
  Search,
  Sparkles,
  MapPin,
  IndianRupee,
  Utensils,
  ArrowRight,
  ShieldCheck,
  Zap,
  Cpu,
  Layers,
  Flame,
  CheckCircle2,
} from "lucide-react"

const CUISINE_OPTIONS = [
  { id: "bengali", label: "Bengali Traditional", icon: "🐟" },
  { id: "north_indian", label: "North Indian / Roti", icon: "🫓" },
  { id: "south_indian", label: "South Indian / Rice", icon: "🍛" },
  { id: "home_style", label: "Home Style Comfort", icon: "🍲" },
  { id: "healthy", label: "Low-Oil / High-Protein", icon: "🥗" },
]

const QUICK_PRESETS = [
  {
    label: "Uluberia Engineering",
    town: "Uluberia",
    diet: "bengali",
    dietType: "non_veg",
    budget: 2700,
    areaMatch: "uluberia",
  },
  {
    label: "Kharagpur Tech Hostels",
    town: "Kharagpur",
    diet: "north_indian",
    dietType: "veg",
    budget: 3200,
    areaMatch: "kharagpur",
  },
  {
    label: "Kalyani Medical Belts",
    town: "Kalyani",
    diet: "home_style",
    dietType: "egg",
    budget: 3000,
    areaMatch: "kalyani",
  },
  {
    label: "Durgapur NIT Saver",
    town: "Durgapur",
    diet: "healthy",
    dietType: "veg",
    budget: 2300,
    areaMatch: "durgapur",
  },
]

export default function SearchPage() {
  const router = useRouter()
  const [selectedAreaId, setSelectedAreaId] = useState<string>("")
  const [selectedDiet, setSelectedDiet] = useState<string>("veg")
  const [budgetMax, setBudgetMax] = useState<number>(3000)
  const radiusKm = 5.0
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>(["bengali"])

  const { data: areasData, isLoading: areasLoading } = useQuery({
    queryKey: ["areas"],
    queryFn: () => api.getAreas(),
  })

  const toggleCuisine = (cuisineId: string) => {
    setSelectedCuisines((prev) =>
      prev.includes(cuisineId) ? prev.filter((c) => c !== cuisineId) : [...prev, cuisineId]
    )
  }

  const applyPreset = (preset: (typeof QUICK_PRESETS)[0]) => {
    setBudgetMax(preset.budget)
    setSelectedDiet(preset.dietType)
    setSelectedCuisines([preset.diet])

    if (areasData?.areas) {
      const match = areasData.areas.find(
        (a) =>
          a.town.toLowerCase().includes(preset.areaMatch) ||
          a.area.toLowerCase().includes(preset.areaMatch)
      )
      if (match) {
        setSelectedAreaId(match.id)
      }
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (selectedAreaId) {
      params.set("area_id", selectedAreaId)
    }
    if (selectedDiet) {
      params.set("diet", selectedDiet)
    }
    if (budgetMax) {
      params.set("budget_max", budgetMax.toString())
    }
    if (radiusKm) {
      params.set("radius_km", radiusKm.toString())
    }
    if (selectedCuisines.length > 0) {
      params.set("cuisines", selectedCuisines.join(","))
    }
    router.push(`/results?${params.toString()}`)
  }

  // Estimated per-meal cost based on 60 meals/month (2 meals/day * 30 days)
  const estPerMeal = Math.round(budgetMax / 60)

  return (
    <div className="flex flex-col gap-12 sm:gap-16 py-4">
      {/* Hero Section with AI Swarm Cockpit */}
      <section className="text-center flex flex-col items-center gap-5 relative">
        {/* Luminous Swarm Badge */}
        <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-amber-500/[0.08] border border-amber-500/30 text-amber-300 text-xs font-mono font-medium shadow-[0_0_20px_rgba(245,158,11,0.15)]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block" />
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>4-Agent LangGraph Swarm · Autonomous Tiffin Intelligence</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight max-w-4xl leading-[1.12]">
          Reliable Daily Tiffin Matches for College Students & Bachelors <br />
          <span className="gradient-text-cyber">Solve Menus & Negotiate Deals.</span>
        </h1>

        <p className="text-sm sm:text-base text-neutral-400 max-w-2xl leading-relaxed">
          Four coordinated AI agents match student hostel clusters, construct verified 7-day non-repeating rotating menus, and mathematically negotiate group subscription discounts.
        </p>

        {/* Quick Scenario Preset Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
          <span className="text-[11px] font-mono text-neutral-500 uppercase tracking-wider flex items-center gap-1 mr-1">
            <Zap className="w-3.5 h-3.5 text-amber-400" /> Quick Belts:
          </span>
          {QUICK_PRESETS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => applyPreset(preset)}
              className="text-xs font-mono px-3 py-1.5 rounded-xl bg-neutral-900/90 border border-white/[0.08] text-neutral-300 hover:text-amber-300 hover:border-amber-500/40 hover:bg-neutral-800/90 transition-all cursor-pointer shadow-xs"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </section>

      {/* Main AI Filter & Optimizer Console */}
      <section className="w-full max-w-3xl mx-auto cyber-panel-glow rounded-3xl p-6 sm:p-9 relative overflow-hidden">
        {/* Subtle decorative grid overlay */}
        <div className="absolute inset-0 ai-dot-pattern opacity-30 pointer-events-none" />

        <form onSubmit={handleSearch} className="relative z-10 flex flex-col gap-7">
          {/* Header Bar */}
          <div className="flex items-center justify-between pb-4 border-b border-white/[0.08]">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-400" />
              <span className="font-mono text-xs uppercase tracking-wider text-amber-300 font-bold">
                Telemetry Parameters
              </span>
            </div>
            <span className="text-[11px] font-mono text-neutral-400 bg-white/[0.04] px-2.5 py-1 rounded-lg border border-white/[0.05]">
              Radius: 5.0 km
            </span>
          </div>

          {/* 01 Locality Selector */}
          <div className="flex flex-col gap-2.5">
            <div className="flex items-center justify-between">
              <label
                htmlFor="area-select"
                className="text-xs font-mono font-bold uppercase tracking-wider text-neutral-300 flex items-center gap-1.5"
              >
                <MapPin className="w-4 h-4 text-amber-400" />
                <span className="text-amber-400/90">[ 01 ]</span> Target College / Hostel Belt
              </label>
              <span className="text-[11px] font-mono text-neutral-500">Synthetic Census</span>
            </div>

            <div className="relative">
              <select
                id="area-select"
                value={selectedAreaId}
                onChange={(e) => setSelectedAreaId(e.target.value)}
                className="w-full p-4 rounded-2xl border border-white/[0.12] bg-[#0c0e14] text-neutral-100 text-sm focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 font-medium transition-all cursor-pointer"
                disabled={areasLoading}
              >
                <option value="">-- All Verified Towns & Student Belts --</option>
                {areasData?.towns.map((town) => (
                  <optgroup key={town} label={`📍 ${town}`} className="bg-[#12141c] text-amber-400 font-bold">
                    {areasData.areas
                      .filter((a) => a.town === town)
                      .map((area) => (
                        <option key={area.id} value={area.id} className="bg-[#0c0e14] text-neutral-200 font-normal">
                          {area.area} ({area.headcount} active students)
                        </option>
                      ))}
                  </optgroup>
                ))}
              </select>
            </div>
            <span className="text-[11px] text-neutral-500 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              Includes Uluberia, Kharagpur, Kalyani, Durgapur, Kolkata, Burdwan, Shibpur, Medinipur
            </span>
          </div>

          {/* 02 Diet Matrix */}
          <div className="flex flex-col gap-2.5">
            <label className="text-xs font-mono font-bold uppercase tracking-wider text-neutral-300 flex items-center gap-1.5">
              <Utensils className="w-4 h-4 text-amber-400" />
              <span className="text-amber-400/90">[ 02 ]</span> Dietary Classification
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: "veg", label: "Pure Veg", desc: "No Onion/Garlic opts", tag: "🥦 Veg" },
                { id: "non_veg", label: "Non-Veg", desc: "Bengali Fish & Chicken", tag: "🍗 Non-Veg" },
                { id: "egg", label: "Eggitarian", desc: "Egg Curry & Omelettes", tag: "🍳 Egg" },
              ].map((d) => {
                const isActive = selectedDiet === d.id
                return (
                  <button
                    type="button"
                    key={d.id}
                    onClick={() => setSelectedDiet(d.id)}
                    className={`p-3.5 rounded-2xl border text-left flex flex-col gap-1 transition-all cursor-pointer relative ${
                      isActive
                        ? "border-amber-500/80 bg-amber-500/[0.12] text-white shadow-[0_0_20px_rgba(245,158,11,0.2)]"
                        : "border-white/[0.08] bg-[#0c0e14] text-neutral-400 hover:border-white/[0.16] hover:text-neutral-200"
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="text-xs font-bold font-mono">{d.tag}</span>
                      {isActive && <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />}
                    </div>
                    <span className="text-[10px] text-neutral-400 line-clamp-1">{d.desc}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* 03 Monthly Budget Slider */}
          <div className="flex flex-col gap-3 p-4 rounded-2xl bg-[#0c0e14]/70 border border-white/[0.08]">
            <div className="flex items-center justify-between">
              <label
                htmlFor="budget-slider"
                className="text-xs font-mono font-bold uppercase tracking-wider text-neutral-300 flex items-center gap-1.5"
              >
                <IndianRupee className="w-4 h-4 text-amber-400" />
                <span className="text-amber-400/90">[ 03 ]</span> Max Monthly Budget
              </label>

              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-neutral-400">
                  ≈ ₹{estPerMeal}/meal
                </span>
                <span className="font-mono font-black text-base text-amber-400 bg-amber-500/10 px-3 py-1 rounded-xl border border-amber-500/30 shadow-[0_0_12px_rgba(245,158,11,0.15)]">
                  ₹{budgetMax.toLocaleString()}/mo
                </span>
              </div>
            </div>

            <input
              id="budget-slider"
              type="range"
              min={1800}
              max={4500}
              step={100}
              value={budgetMax}
              onChange={(e) => setBudgetMax(Number(e.target.value))}
              className="w-full cursor-pointer h-2.5 bg-neutral-800 rounded-lg appearance-none"
            />

            <div className="flex justify-between text-[11px] font-mono text-neutral-500">
              <span>₹1,800 (Economy)</span>
              <span>₹3,000 (Standard PG)</span>
              <span>₹4,500 (Deluxe Protein)</span>
            </div>
          </div>

          {/* 04 Cuisine Selection */}
          <div className="flex flex-col gap-2.5">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-neutral-300 flex items-center gap-1.5">
              <span className="text-amber-400/90">[ 04 ]</span> Cuisines & Regional Preferences
            </span>
            <div className="flex flex-wrap gap-2.5">
              {CUISINE_OPTIONS.map((c) => {
                const isSelected = selectedCuisines.includes(c.id)
                return (
                  <button
                    type="button"
                    key={c.id}
                    onClick={() => toggleCuisine(c.id)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-medium transition-all flex items-center gap-2 cursor-pointer ${
                      isSelected
                        ? "bg-amber-500 text-neutral-950 font-bold shadow-[0_0_16px_rgba(245,158,11,0.35)]"
                        : "bg-[#0c0e14] border border-white/[0.08] text-neutral-400 hover:border-white/[0.2] hover:text-neutral-200"
                    }`}
                  >
                    <span>{c.icon}</span>
                    <span>{c.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-amber-500 via-amber-400 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-neutral-950 font-black text-sm tracking-wide flex items-center justify-center gap-3 shadow-[0_0_30px_rgba(245,158,11,0.35)] hover:shadow-[0_0_40px_rgba(245,158,11,0.5)] transition-all cursor-pointer group mt-2"
          >
            <Search className="w-4 h-4 text-neutral-950 stroke-[2.5]" />
            <span>Search & Optimize Tiffin Matches</span>
            <ArrowRight className="w-4 h-4 text-neutral-950 stroke-[2.5] group-hover:translate-x-1.5 transition-transform" />
          </button>
        </form>
      </section>

      {/* 4-Agent Orchestration Pipeline Visualizer */}
      <section className="flex flex-col gap-6 max-w-5xl mx-auto w-full pt-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/[0.08] pb-3">
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400 font-bold">
              Autonomous Architecture
            </span>
            <h2 className="text-xl font-bold text-white">
              The 4 LangGraph Agent Pipeline
            </h2>
          </div>
          <span className="text-xs font-mono text-neutral-500">
            Stateful Execution · Deterministic Fallbacks
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Agent 1 */}
          <div className="p-5 rounded-2xl cyber-panel border border-white/[0.08] hover:border-amber-500/40 transition-all flex flex-col justify-between gap-4 group">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 font-mono font-bold flex items-center justify-center text-xs">
                  01
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.05] text-neutral-400">
                  Geo Cluster
                </span>
              </div>
              <h3 className="font-bold text-white text-sm group-hover:text-amber-400 transition-colors">
                Demand Agent
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Aggregates student headcount, coordinates, and budget ceilings around university hostel belts.
              </p>
            </div>
            <div className="pt-3 border-t border-white/[0.05] text-[11px] font-mono text-amber-400/80">
              Haversine Centroid Engine
            </div>
          </div>

          {/* Agent 2 */}
          <div className="p-5 rounded-2xl cyber-panel border border-white/[0.08] hover:border-emerald-500/40 transition-all flex flex-col justify-between gap-4 group">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono font-bold flex items-center justify-center text-xs">
                  02
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400">
                  Deterministic
                </span>
              </div>
              <h3 className="font-bold text-white text-sm group-hover:text-emerald-400 transition-colors">
                Match Agent
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Applies 5-factor weighted formula (Proximity, Cuisine, Price, Capacity, Rating) with zero LLM variance.
              </p>
            </div>
            <div className="pt-3 border-t border-white/[0.05] text-[11px] font-mono text-emerald-400/80">
              Scored 0.00 – 1.00 Matrix
            </div>
          </div>

          {/* Agent 3 */}
          <div className="p-5 rounded-2xl cyber-panel border border-white/[0.08] hover:border-violet-500/40 transition-all flex flex-col justify-between gap-4 group">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-8 h-8 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-400 font-mono font-bold flex items-center justify-center text-xs">
                  03
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400">
                  LLM + Rules
                </span>
              </div>
              <h3 className="font-bold text-white text-sm group-hover:text-violet-400 transition-colors">
                Menu Agent
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Builds 14 weekly meals enforcing zero slot repeat, veg ratio tolerances, and deterministic rotation fallbacks.
              </p>
            </div>
            <div className="pt-3 border-t border-white/[0.05] text-[11px] font-mono text-violet-400/80">
              Constraint Verification Pass
            </div>
          </div>

          {/* Agent 4 */}
          <div className="p-5 rounded-2xl cyber-panel border border-white/[0.08] hover:border-cyan-500/40 transition-all flex flex-col justify-between gap-4 group">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-mono font-bold flex items-center justify-center text-xs">
                  04
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400">
                  Game Theory
                </span>
              </div>
              <h3 className="font-bold text-white text-sm group-hover:text-cyan-400 transition-colors">
                Deal Agent
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Simulates 5-round bargaining between cluster budget ceilings and provider cost floors with volume discounts.
              </p>
            </div>
            <div className="pt-3 border-t border-white/[0.05] text-[11px] font-mono text-cyan-400/80">
              Volume Discount Tiers
            </div>
          </div>
        </div>
      </section>

      {/* Telemetry Highlights Bento Grid */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-5 max-w-5xl mx-auto w-full">
        <div className="p-6 rounded-2xl cyber-panel border border-white/[0.08] flex flex-col gap-2">
          <div className="flex items-center gap-2 text-amber-400 font-mono text-xs">
            <Flame className="w-4 h-4" />
            <span>Zero Hallucination</span>
          </div>
          <div className="text-2xl font-black text-white font-mono">100%</div>
          <p className="text-xs text-neutral-400">
            Deterministic fallback algorithms guarantee menu and deal generation even if cloud LLM providers suffer downtime.
          </p>
        </div>

        <div className="p-6 rounded-2xl cyber-panel border border-white/[0.08] flex flex-col gap-2">
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs">
            <ShieldCheck className="w-4 h-4" />
            <span>Auditable Ranking</span>
          </div>
          <div className="text-2xl font-black text-white font-mono">5 Factors</div>
          <p className="text-xs text-neutral-400">
            Distance, cuisine compatibility, price ceiling compliance, capacity, and ratings with natural language reasons.
          </p>
        </div>

        <div className="p-6 rounded-2xl cyber-panel border border-white/[0.08] flex flex-col gap-2">
          <div className="flex items-center gap-2 text-violet-400 font-mono text-xs">
            <Layers className="w-4 h-4" />
            <span>Hostel Belts</span>
          </div>
          <div className="text-2xl font-black text-white font-mono">8+ Towns</div>
          <p className="text-xs text-neutral-400">
            Pre-seeded synthetic student demand clusters mapping Uluberia, Kharagpur, Kalyani, Durgapur, Kolkata, and beyond.
          </p>
        </div>
      </section>
    </div>
  )
}
