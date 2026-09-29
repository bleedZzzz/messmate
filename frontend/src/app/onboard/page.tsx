"use client"

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { ProviderOnboardingSchema, ProviderOnboarding } from "@/lib/schemas"
import {
  CheckCircle2,
  UserPlus,
  AlertCircle,
  ShieldCheck,
  Loader2,
  ArrowRight,
  Sparkles,
  Building,
  DollarSign,
  Phone,
  FileCheck,
} from "lucide-react"

export default function OnboardPage() {
  const [formData, setFormData] = useState<Partial<ProviderOnboarding>>({
    name: "",
    town: "Uluberia",
    area: "",
    lat: 22.4722,
    lon: 88.1125,
    cuisines: ["bengali"],
    diet_types: ["veg", "non_veg"],
    capacity_total: 50,
    capacity_available: 30,
    list_price_monthly: 2800,
    cost_per_meal: 35,
    min_margin: 0.15,
    flexibility: 0.20,
    phone: "+91 ",
    consent_given: false,
  })

  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [submittedId, setSubmittedId] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (data: ProviderOnboarding) => api.onboardProvider(data),
    onSuccess: (data) => {
      setSubmittedId(data.id)
    },
    onError: (err: Error) => {
      setFormErrors({ submit: err.message || "Failed to submit onboarding form." })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setFormErrors({})

    const validation = ProviderOnboardingSchema.safeParse(formData)
    if (!validation.success) {
      const errors: Record<string, string> = {}
      validation.error.issues.forEach((issue) => {
        const key = issue.path[0] as string
        errors[key] = issue.message
      })
      setFormErrors(errors)
      return
    }

    mutation.mutate(validation.data)
  }

  const toggleCuisine = (c: string) => {
    const current = formData.cuisines || []
    setFormData({
      ...formData,
      cuisines: current.includes(c) ? current.filter((item) => item !== c) : [...current, c],
    })
  }

  const toggleDiet = (d: "veg" | "non_veg" | "egg") => {
    const current = formData.diet_types || []
    setFormData({
      ...formData,
      diet_types: current.includes(d) ? current.filter((item) => item !== d) : [...current, d],
    })
  }

  if (submittedId) {
    return (
      <div className="max-w-xl mx-auto my-12 p-8 sm:p-10 rounded-3xl cyber-panel-glow text-center flex flex-col items-center gap-5 shadow-2xl">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center justify-center shadow-[0_0_20px_rgba(16,185,129,0.3)]">
          <CheckCircle2 className="w-9 h-9" />
        </div>
        <div className="flex flex-col gap-2">
          <h2 className="text-2xl font-black font-mono text-white">
            Registration Submitted to Swarm
          </h2>
          <p className="text-xs font-mono text-neutral-300 leading-relaxed">
            Application ID: <strong className="text-amber-400 font-bold">{submittedId}</strong>
            <br />
            Status: <span className="text-amber-400 font-bold">Pending Radius Verification</span>.
            Our telemetry verifies local hostel proximity and hygiene standards before activating active 5-factor ranking.
          </p>
        </div>
        <button
          onClick={() => {
            setSubmittedId(null)
            setFormData({ ...formData, name: "", area: "", consent_given: false })
          }}
          className="mt-3 px-6 py-3 rounded-2xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-mono text-xs font-bold transition-all shadow-[0_0_15px_rgba(245,158,11,0.3)] cursor-pointer"
        >
          Register Another Mess Provider
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-8 py-2">
      <div className="flex flex-col gap-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 font-mono text-[11px] uppercase font-bold w-fit">
          <Building className="w-3.5 h-3.5 text-amber-400" />
          <span>Provider Network Onboarding</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white">
          List Your Mess on <span className="gradient-text-cyber">MessMate AI Swarm</span>
        </h1>
        <p className="text-xs sm:text-sm font-mono text-neutral-400">
          Connect directly with high-volume student demand clusters around college hostels in your town.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="p-6 sm:p-9 rounded-3xl cyber-panel border border-white/[0.1] shadow-2xl flex flex-col gap-6 text-xs font-mono"
      >
        {formErrors.submit && (
          <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{formErrors.submit}</span>
          </div>
        )}

        {/* Business Name */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-neutral-200">
            Mess / Catering Name *
          </label>
          <input
            type="text"
            required
            value={formData.name || ""}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g. Annapurna Student Mess & Tiffin"
            className="p-3.5 rounded-xl border border-white/[0.12] bg-[#0c0e14] text-white focus:border-amber-500 focus:outline-none transition-all"
          />
          {formErrors.name && <span className="text-red-400 text-[11px]">{formErrors.name}</span>}
        </div>

        {/* Town & Locality */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex flex-col gap-2">
            <label className="font-bold text-neutral-200">Town / City *</label>
            <input
              type="text"
              required
              value={formData.town || ""}
              onChange={(e) => setFormData({ ...formData, town: e.target.value })}
              placeholder="e.g. Uluberia"
              className="p-3.5 rounded-xl border border-white/[0.12] bg-[#0c0e14] text-white focus:border-amber-500 focus:outline-none transition-all"
            />
            {formErrors.town && <span className="text-red-400 text-[11px]">{formErrors.town}</span>}
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-bold text-neutral-200">Area / Locality *</label>
            <input
              type="text"
              required
              value={formData.area || ""}
              onChange={(e) => setFormData({ ...formData, area: e.target.value })}
              placeholder="e.g. College Para / Station Road"
              className="p-3.5 rounded-xl border border-white/[0.12] bg-[#0c0e14] text-white focus:border-amber-500 focus:outline-none transition-all"
            />
            {formErrors.area && <span className="text-red-400 text-[11px]">{formErrors.area}</span>}
          </div>
        </div>

        {/* Pricing & Capacity */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex flex-col gap-2">
            <label className="font-bold text-neutral-200">
              Monthly List Price (₹) *
            </label>
            <input
              type="number"
              required
              value={formData.list_price_monthly || ""}
              onChange={(e) =>
                setFormData({ ...formData, list_price_monthly: Number(e.target.value) })
              }
              className="p-3.5 rounded-xl border border-white/[0.12] bg-[#0c0e14] text-white focus:border-amber-500 focus:outline-none transition-all"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-bold text-neutral-200">
              Cost Per Meal (₹) *
            </label>
            <input
              type="number"
              required
              value={formData.cost_per_meal || ""}
              onChange={(e) => setFormData({ ...formData, cost_per_meal: Number(e.target.value) })}
              className="p-3.5 rounded-xl border border-white/[0.12] bg-[#0c0e14] text-white focus:border-amber-500 focus:outline-none transition-all"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="font-bold text-neutral-200">
              Available Capacity (Seats) *
            </label>
            <input
              type="number"
              required
              value={formData.capacity_available || ""}
              onChange={(e) =>
                setFormData({ ...formData, capacity_available: Number(e.target.value) })
              }
              className="p-3.5 rounded-xl border border-white/[0.12] bg-[#0c0e14] text-white focus:border-amber-500 focus:outline-none transition-all"
            />
          </div>
        </div>

        {/* Cuisines */}
        <div className="flex flex-col gap-2.5">
          <label className="font-bold text-neutral-200">Cuisines Offered *</label>
          <div className="flex flex-wrap gap-2">
            {["bengali", "north_indian", "south_indian", "home_style"].map((c) => {
              const active = formData.cuisines?.includes(c)
              return (
                <button
                  type="button"
                  key={c}
                  onClick={() => toggleCuisine(c)}
                  className={`px-3.5 py-2 rounded-xl border capitalize font-mono text-xs transition-all cursor-pointer ${
                    active
                      ? "border-amber-500 bg-amber-500/20 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.2)]"
                      : "border-white/[0.08] bg-[#0c0e14] text-neutral-400 hover:text-white"
                  }`}
                >
                  {c.replace("_", " ")}
                </button>
              )
            })}
          </div>
        </div>

        {/* Diet Types */}
        <div className="flex flex-col gap-2.5">
          <label className="font-bold text-neutral-200">Dietary Categories Served *</label>
          <div className="flex flex-wrap gap-2">
            {(["veg", "non_veg", "egg"] as const).map((d) => {
              const active = formData.diet_types?.includes(d)
              return (
                <button
                  type="button"
                  key={d}
                  onClick={() => toggleDiet(d)}
                  className={`px-3.5 py-2 rounded-xl border capitalize font-mono text-xs transition-all cursor-pointer ${
                    active
                      ? "border-amber-500 bg-amber-500/20 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.2)]"
                      : "border-white/[0.08] bg-[#0c0e14] text-neutral-400 hover:text-white"
                  }`}
                >
                  {d.replace("_", " ")}
                </button>
              )
            })}
          </div>
          {formErrors.diet_types && <span className="text-red-400 text-[11px]">{formErrors.diet_types}</span>}
        </div>

        {/* WhatsApp Phone */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-neutral-200">
            WhatsApp Contact Number *
          </label>
          <input
            type="text"
            required
            value={formData.phone || ""}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            placeholder="+91 98300 00000"
            className="p-3.5 rounded-xl border border-white/[0.12] bg-[#0c0e14] text-white focus:border-amber-500 focus:outline-none transition-all font-mono"
          />
          <span className="text-[11px] text-neutral-500 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Direct WhatsApp routing only. Never sold or shared with advertisers.
          </span>
          {formErrors.phone && <span className="text-red-400 text-[11px]">{formErrors.phone}</span>}
        </div>

        {/* Consent Checkbox */}
        <div className="p-4 rounded-2xl bg-amber-500/[0.05] border border-amber-500/20 flex items-start gap-3 mt-2">
          <input
            type="checkbox"
            id="consent-checkbox"
            required
            checked={!!formData.consent_given}
            onChange={(e) => setFormData({ ...formData, consent_given: e.target.checked })}
            className="mt-1 w-4 h-4 accent-amber-500 cursor-pointer shrink-0"
          />
          <label htmlFor="consent-checkbox" className="text-xs text-neutral-300 cursor-pointer leading-relaxed">
            <strong className="text-amber-400 block mb-0.5">
              Privacy & Listing Consent:
            </strong>
            I authorize MessMate to index my tiffin service and allow matched student hostel clusters
            to initiate contact with me via WhatsApp. I confirm my mess adheres to local hygiene standards.
          </label>
        </div>
        {formErrors.consent_given && (
          <span className="text-red-400 text-[11px]">{formErrors.consent_given}</span>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-amber-500 via-amber-400 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-neutral-950 font-black font-mono text-sm tracking-wide flex items-center justify-center gap-2 shadow-[0_0_25px_rgba(245,158,11,0.35)] transition-all cursor-pointer disabled:opacity-50 mt-2"
        >
          {mutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-neutral-950" />
              <span>TRANSMITTING TO TELEMETRY SWARM...</span>
            </>
          ) : (
            <>
              <span>SUBMIT APPLICATION TO MESSMATE SWARM</span>
              <ArrowRight className="w-4 h-4 text-neutral-950 stroke-[2.5]" />
            </>
          )}
        </button>
      </form>
    </div>
  )
}
