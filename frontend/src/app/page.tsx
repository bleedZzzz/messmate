"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { Search, Sparkles, MapPin, IndianRupee, Utensils, ArrowRight } from "lucide-react"

const CUISINE_OPTIONS = [
  { id: "bengali", label: "Bengali" },
  { id: "north_indian", label: "North Indian" },
  { id: "south_indian", label: "South Indian" },
  { id: "home_style", label: "Home Style" },
  { id: "healthy", label: "Healthy / Low Oil" },
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

  return (
    <div className="flex flex-col gap-10">
      {/* Hero Section */}
      <section className="text-center py-6 sm:py-10 flex flex-col items-center gap-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-100 dark:bg-orange-950/70 border border-orange-200 dark:border-orange-800 text-orange-700 dark:text-orange-300 text-xs font-semibold shadow-xs">
          <Sparkles className="w-3.5 h-3.5 text-orange-600" />
          Powered by 4-Agent LangGraph Orchestration
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-stone-900 dark:text-stone-50 max-w-3xl leading-tight">
          Reliable Daily Tiffin Matches for College Students & Bachelors
        </h1>

        <p className="text-sm sm:text-base text-stone-600 dark:text-stone-400 max-w-2xl">
          Match with verified local mess providers, inspect rotating 7-day meal plans with balanced veg ratios,
          and simulate volume-discounted monthly subscription negotiations.
        </p>
      </section>

      {/* Main Search Panel */}
      <section className="w-full max-w-2xl mx-auto p-6 sm:p-8 rounded-3xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-xl shadow-orange-900/5">
        <form onSubmit={handleSearch} className="flex flex-col gap-6">
          {/* Locality Selector */}
          <div className="flex flex-col gap-2">
            <label htmlFor="area-select" className="text-xs font-bold uppercase tracking-wider text-stone-700 dark:text-stone-300 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-orange-600" /> Select College / Hostel Belts
            </label>
            <div className="relative">
              <select
                id="area-select"
                value={selectedAreaId}
                onChange={(e) => setSelectedAreaId(e.target.value)}
                className="w-full p-3.5 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/60 text-stone-900 dark:text-stone-100 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 font-medium"
                disabled={areasLoading}
              >
                <option value="">-- All Verified Towns and Localities --</option>
                {areasData?.towns.map((town) => (
                  <optgroup key={town} label={`📍 ${town}`}>
                    {areasData.areas
                      .filter((a) => a.town === town)
                      .map((area) => (
                        <option key={area.id} value={area.id}>
                          {area.area} ({area.headcount} active students)
                        </option>
                      ))}
                  </optgroup>
                ))}
              </select>
            </div>
            <span className="text-[11px] text-stone-500">
              Clusters are identified around hostel belts in Uluberia, Kharagpur, Durgapur, Kalyani, etc.
            </span>
          </div>

          {/* Diet Toggle */}
          <div className="flex flex-col gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-700 dark:text-stone-300 flex items-center gap-1.5">
              <Utensils className="w-4 h-4 text-orange-600" /> Dietary Preference
            </span>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: "veg", label: "Pure Veg" },
                { id: "non_veg", label: "Non-Veg (Fish/Chicken)" },
                { id: "egg", label: "Eggitarian" },
              ].map((d) => (
                <button
                  type="button"
                  key={d.id}
                  onClick={() => setSelectedDiet(d.id)}
                  className={`p-3 rounded-xl border text-xs font-semibold transition-all ${
                    selectedDiet === d.id
                      ? "border-orange-600 bg-orange-50 dark:bg-orange-950/60 text-orange-700 dark:text-orange-300 ring-2 ring-orange-500/20"
                      : "border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/40 text-stone-700 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-800"
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Budget Range Slider */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <label htmlFor="budget-slider" className="text-xs font-bold uppercase tracking-wider text-stone-700 dark:text-stone-300 flex items-center gap-1.5">
                <IndianRupee className="w-4 h-4 text-orange-600" /> Maximum Monthly Budget
              </label>
              <span className="font-extrabold text-sm text-orange-600 dark:text-orange-400">
                ₹{budgetMax.toLocaleString()}/mo
              </span>
            </div>
            <input
              id="budget-slider"
              type="range"
              min={1800}
              max={4500}
              step={100}
              value={budgetMax}
              onChange={(e) => setBudgetMax(Number(e.target.value))}
              className="w-full accent-orange-600 cursor-pointer h-2 bg-stone-200 dark:bg-stone-800 rounded-lg"
            />
            <div className="flex justify-between text-[11px] text-stone-400">
              <span>₹1,800 (Economy)</span>
              <span>₹3,000 (Standard)</span>
              <span>₹4,500 (Premium Deluxe)</span>
            </div>
          </div>

          {/* Cuisine Chips */}
          <div className="flex flex-col gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-700 dark:text-stone-300">
              Preferred Cuisines
            </span>
            <div className="flex flex-wrap gap-2">
              {CUISINE_OPTIONS.map((c) => {
                const isSelected = selectedCuisines.includes(c.id)
                return (
                  <button
                    type="button"
                    key={c.id}
                    onClick={() => toggleCuisine(c.id)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                      isSelected
                        ? "bg-orange-600 text-white shadow-xs"
                        : "bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-400 hover:bg-stone-200 dark:hover:bg-stone-700"
                    }`}
                  >
                    {c.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Submit Search */}
          <button
            type="submit"
            className="w-full py-4 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-orange-600/25 hover:shadow-orange-600/35 transition-all mt-2 group"
          >
            <Search className="w-4 h-4" />
            <span>Search & Optimize Tiffin Matches</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>
      </section>

      {/* Feature Highlights Grid */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto pt-6">
        <div className="p-5 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900/60 flex flex-col gap-2">
          <div className="w-9 h-9 rounded-xl bg-emerald-100 dark:bg-emerald-950 text-emerald-600 flex items-center justify-center font-bold text-sm">
            01
          </div>
          <h3 className="font-bold text-stone-900 dark:text-stone-100 text-sm">
            Deterministic Geo Match
          </h3>
          <p className="text-xs text-stone-500">
            5-factor scoring balancing Haversine proximity, cuisine weights, price ceilings, and capacity.
          </p>
        </div>

        <div className="p-5 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900/60 flex flex-col gap-2">
          <div className="w-9 h-9 rounded-xl bg-violet-100 dark:bg-violet-950 text-violet-600 flex items-center justify-center font-bold text-sm">
            02
          </div>
          <h3 className="font-bold text-stone-900 dark:text-stone-100 text-sm">
            Constraint-Checked Menus
          </h3>
          <p className="text-xs text-stone-500">
            Guaranteed 14 unique weekly slot meals with veg ratio verification and deterministic fallback.
          </p>
        </div>

        <div className="p-5 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900/60 flex flex-col gap-2">
          <div className="w-9 h-9 rounded-xl bg-orange-100 dark:bg-orange-950 text-orange-600 flex items-center justify-center font-bold text-sm">
            03
          </div>
          <h3 className="font-bold text-stone-900 dark:text-stone-100 text-sm">
            Transparent Negotiations
          </h3>
          <p className="text-xs text-stone-500">
            Mathematically bounded price compromises factoring volume discount tiers for student hostels.
          </p>
        </div>
      </section>
    </div>
  )
}
