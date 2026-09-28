"use client"

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { ProviderOnboardingSchema, ProviderOnboarding } from "@/lib/schemas"
import { CheckCircle2, UserPlus, AlertCircle, ShieldCheck, Loader2 } from "lucide-react"

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
      <div className="max-w-xl mx-auto my-12 p-8 rounded-3xl border border-emerald-200 dark:border-emerald-900 bg-white dark:bg-stone-900 text-center flex flex-col items-center gap-4 shadow-sm">
        <div className="w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-emerald-950 text-emerald-600 flex items-center justify-center">
          <CheckCircle2 className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-bold text-stone-900 dark:text-stone-100">
          Onboarding Registration Submitted!
        </h2>
        <p className="text-xs text-stone-600 dark:text-stone-400">
          Your application ID is <strong className="font-mono">{submittedId}</strong>.
          Your mess is currently in <strong className="text-amber-600">Pending</strong> verification status.
          Our team reviews student radius coverage and hygiene standards before activating active search ranking.
        </p>
        <button
          onClick={() => {
            setSubmittedId(null)
            setFormData({ ...formData, name: "", area: "", consent_given: false })
          }}
          className="mt-4 px-5 py-2.5 rounded-xl bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900 text-xs font-semibold"
        >
          Register Another Provider
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-1.5 text-center sm:text-left">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-stone-900 dark:text-stone-100 flex items-center gap-2 justify-center sm:justify-start">
          <UserPlus className="w-6 h-6 text-orange-600" />
          Tiffin Mess Partner Onboarding
        </h1>
        <p className="text-xs sm:text-sm text-stone-500">
          Join the MessMate network to receive bulk monthly student hostel subscriptions in your town.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="p-6 sm:p-8 rounded-3xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm flex flex-col gap-5 text-xs"
      >
        {formErrors.submit && (
          <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{formErrors.submit}</span>
          </div>
        )}

        {/* Business Name */}
        <div className="flex flex-col gap-1.5">
          <label className="font-bold text-stone-700 dark:text-stone-300">
            Mess / Catering Name *
          </label>
          <input
            type="text"
            required
            value={formData.name || ""}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g. Annapurna Student Mess & Tiffin"
            className="p-3 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-orange-500 outline-none"
          />
          {formErrors.name && <span className="text-red-500 text-[11px]">{formErrors.name}</span>}
        </div>

        {/* Town & Locality */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="font-bold text-stone-700 dark:text-stone-300">Town / City *</label>
            <input
              type="text"
              required
              value={formData.town || ""}
              onChange={(e) => setFormData({ ...formData, town: e.target.value })}
              placeholder="e.g. Uluberia"
              className="p-3 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-orange-500 outline-none"
            />
            {formErrors.town && <span className="text-red-500 text-[11px]">{formErrors.town}</span>}
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="font-bold text-stone-700 dark:text-stone-300">Area / Locality *</label>
            <input
              type="text"
              required
              value={formData.area || ""}
              onChange={(e) => setFormData({ ...formData, area: e.target.value })}
              placeholder="e.g. College Para / Bazar Area"
              className="p-3 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-orange-500 outline-none"
            />
            {formErrors.area && <span className="text-red-500 text-[11px]">{formErrors.area}</span>}
          </div>
        </div>

        {/* Pricing & Capacity */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="font-bold text-stone-700 dark:text-stone-300">
              Monthly List Price (₹) *
            </label>
            <input
              type="number"
              required
              value={formData.list_price_monthly || ""}
              onChange={(e) =>
                setFormData({ ...formData, list_price_monthly: Number(e.target.value) })
              }
              className="p-3 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-orange-500 outline-none"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="font-bold text-stone-700 dark:text-stone-300">
              Raw Cost Per Meal (₹) *
            </label>
            <input
              type="number"
              required
              value={formData.cost_per_meal || ""}
              onChange={(e) => setFormData({ ...formData, cost_per_meal: Number(e.target.value) })}
              className="p-3 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-orange-500 outline-none"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="font-bold text-stone-700 dark:text-stone-300">
              Available Capacity (Students) *
            </label>
            <input
              type="number"
              required
              value={formData.capacity_available || ""}
              onChange={(e) =>
                setFormData({ ...formData, capacity_available: Number(e.target.value) })
              }
              className="p-3 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-orange-500 outline-none"
            />
          </div>
        </div>

        {/* Cuisines */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-stone-700 dark:text-stone-300">Cuisines Offered *</label>
          <div className="flex flex-wrap gap-2">
            {["bengali", "north_indian", "south_indian", "home_style"].map((c) => {
              const active = formData.cuisines?.includes(c)
              return (
                <button
                  type="button"
                  key={c}
                  onClick={() => toggleCuisine(c)}
                  className={`px-3 py-1.5 rounded-lg border capitalize font-medium ${
                    active
                      ? "border-orange-600 bg-orange-50 dark:bg-orange-950 text-orange-700 dark:text-orange-300"
                      : "border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-600 dark:text-stone-400"
                  }`}
                >
                  {c.replace("_", " ")}
                </button>
              )
            })}
          </div>
        </div>

        {/* Diet Types */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-stone-700 dark:text-stone-300">Dietary Categories Served *</label>
          <div className="flex flex-wrap gap-2">
            {(["veg", "non_veg", "egg"] as const).map((d) => {
              const active = formData.diet_types?.includes(d)
              return (
                <button
                  type="button"
                  key={d}
                  onClick={() => toggleDiet(d)}
                  className={`px-3 py-1.5 rounded-lg border capitalize font-medium ${
                    active
                      ? "border-orange-600 bg-orange-50 dark:bg-orange-950 text-orange-700 dark:text-orange-300"
                      : "border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-600 dark:text-stone-400"
                  }`}
                >
                  {d.replace("_", " ")}
                </button>
              )
            })}
          </div>
          {formErrors.diet_types && <span className="text-red-500 text-[11px]">{formErrors.diet_types}</span>}
        </div>

        {/* WhatsApp Phone */}
        <div className="flex flex-col gap-1.5">
          <label className="font-bold text-stone-700 dark:text-stone-300">
            WhatsApp Contact Number *
          </label>
          <input
            type="text"
            required
            value={formData.phone || ""}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            placeholder="+91 98300 00000"
            className="p-3 rounded-xl border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-800 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-orange-500 outline-none font-mono"
          />
          <span className="text-[11px] text-stone-500 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            Phone numbers are never logged or sold. Only used to redirect interested students directly to your WhatsApp.
          </span>
          {formErrors.phone && <span className="text-red-500 text-[11px]">{formErrors.phone}</span>}
        </div>

        {/* Mandatory Consent Checkbox */}
        <div className="p-4 rounded-xl border border-orange-200 dark:border-orange-900/40 bg-orange-50/50 dark:bg-orange-950/20 flex items-start gap-3 mt-2">
          <input
            type="checkbox"
            id="consent-checkbox"
            required
            checked={!!formData.consent_given}
            onChange={(e) => setFormData({ ...formData, consent_given: e.target.checked })}
            className="mt-1 w-4 h-4 accent-orange-600 cursor-pointer shrink-0"
          />
          <label htmlFor="consent-checkbox" className="text-xs text-stone-700 dark:text-stone-300 cursor-pointer">
            <strong className="text-stone-900 dark:text-stone-100 block">
              Explicit Privacy & Listing Consent (Required):
            </strong>
            I authorize MessMate to index my tiffin service and allow matched student hostel clusters
            to initiate contact with me via WhatsApp. I confirm my mess holds required local hygiene
            standards.
          </label>
        </div>
        {formErrors.consent_given && (
          <span className="text-red-500 text-[11px]">{formErrors.consent_given}</span>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full py-3.5 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-md shadow-orange-600/20 transition-all cursor-pointer disabled:opacity-50"
        >
          {mutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Registering Application...</span>
            </>
          ) : (
            <span>Submit Partner Application</span>
          )}
        </button>
      </form>
    </div>
  )
}
