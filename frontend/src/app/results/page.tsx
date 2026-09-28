"use client"

import { Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { api } from "@/lib/api"
import { ProviderCard } from "@/components/provider-card"
import { AgentTracePanel } from "@/components/trace-panel"
import { SkeletonLoader } from "@/components/skeleton-loader"
import { Users, MapPin, IndianRupee, ArrowLeft, RefreshCw, AlertCircle } from "lucide-react"

function ResultsContent() {
  const searchParams = useSearchParams()
  const areaId = searchParams.get("area_id") || undefined
  const area = searchParams.get("area") || undefined
  const diet = (searchParams.get("diet") as "veg" | "non_veg" | "egg") || undefined
  const budgetMax = searchParams.get("budget_max") ? Number(searchParams.get("budget_max")) : undefined
  const radiusKm = searchParams.get("radius_km") ? Number(searchParams.get("radius_km")) : 5.0
  const cuisines = searchParams.get("cuisines") ? searchParams.get("cuisines")!.split(",") : []

  // Invoke full optimization pipeline
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["optimize", areaId, area, diet, budgetMax, radiusKm, cuisines.join(",")],
    queryFn: () =>
      api.optimize({
        area_id: areaId,
        area: area,
        diet: diet,
        budget_max: budgetMax,
        radius_km: radiusKm,
        cuisines: cuisines,
        top_n: 10,
      }),
  })

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-2">
            <div className="h-7 bg-stone-200 dark:bg-stone-800 rounded-md w-64 animate-pulse" />
            <div className="h-4 bg-stone-200 dark:bg-stone-800 rounded-md w-96 animate-pulse" />
          </div>
        </div>
        <SkeletonLoader count={4} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded-3xl border border-red-200 dark:border-red-900/60 bg-red-50/50 dark:bg-red-950/20 gap-4 my-8">
        <AlertCircle className="w-10 h-10 text-red-500" />
        <h2 className="text-lg font-bold text-red-900 dark:text-red-200">
          Optimization Pipeline Encountered An Error
        </h2>
        <p className="text-xs text-red-700 dark:text-red-300 max-w-md">
          {error instanceof Error ? error.message : "Unable to reach server. Please ensure the backend is running."}
        </p>
        <button
          onClick={() => refetch()}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-600 text-white text-xs font-semibold hover:bg-red-700 transition-colors shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Try Again
        </button>
      </div>
    )
  }

  const cluster = data?.cluster
  const matches = data?.matches || []
  const trace = data?.trace || []
  const errors = data?.errors || []

  return (
    <div className="flex flex-col gap-8">
      {/* Top Navigation & Cluster Banner */}
      <div className="flex flex-col gap-4">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 dark:text-stone-400 hover:text-orange-600 transition-colors self-start"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Search Filter
        </Link>

        {cluster ? (
          <div className="p-5 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex flex-col gap-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-orange-600">
                Matched Demand Cluster
              </span>
              <h2 className="text-xl font-bold text-stone-900 dark:text-stone-100 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-orange-600 shrink-0" />
                {cluster.area}, {cluster.town}
              </h2>
              <p className="text-xs text-stone-500">
                Local student cluster with shared dietary and price preferences
              </p>
            </div>

            <div className="flex items-center gap-4 text-xs font-medium text-stone-600 dark:text-stone-400 bg-stone-50 dark:bg-stone-800/60 p-3 rounded-xl border border-stone-100 dark:border-stone-800">
              <span className="flex items-center gap-1">
                <Users className="w-4 h-4 text-orange-500" />
                <strong>{cluster.headcount}</strong> Students
              </span>
              <span>·</span>
              <span className="flex items-center gap-1">
                <IndianRupee className="w-4 h-4 text-emerald-500" />
                Ceiling: <strong>₹{Math.round(cluster.budget_ceiling_monthly)}</strong>/mo
              </span>
            </div>
          </div>
        ) : (
          <div className="p-4 rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50/50 dark:bg-amber-950/20 text-xs text-amber-800 dark:text-amber-300">
            No specific cluster selected; ranking active providers across town.
          </div>
        )}
      </div>

      {/* Agent Observability Trace Panel */}
      <AgentTracePanel trace={trace} errors={errors} />

      {/* Ranked Results List */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-lg text-stone-900 dark:text-stone-100">
            Ranked Tiffin Providers ({matches.length})
          </h2>
          <span className="text-xs text-stone-500">
            Sorted by 5-Factor Match Quality
          </span>
        </div>

        {matches.length === 0 ? (
          <div className="p-12 text-center rounded-3xl border border-dashed border-stone-300 dark:border-stone-800 bg-white/40 dark:bg-stone-900/40 flex flex-col items-center gap-3">
            <MapPin className="w-8 h-8 text-stone-400" />
            <h3 className="font-bold text-stone-800 dark:text-stone-200 text-sm">
              No Qualifying Providers Found
            </h3>
            <p className="text-xs text-stone-500 max-w-sm">
              Try increasing your radius slider or relaxing diet constraints to match more mess operators.
            </p>
            <Link
              href="/"
              className="mt-2 px-4 py-2 rounded-xl bg-orange-600 text-white text-xs font-semibold hover:bg-orange-700 transition-colors"
            >
              Modify Search
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {matches.map((m, idx) => (
              <ProviderCard
                key={m.provider_id}
                rank={idx + 1}
                match={m}
                provider={data?.top_provider?.id === m.provider_id ? data.top_provider : undefined}
                clusterId={cluster?.id}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<SkeletonLoader count={4} />}>
      <ResultsContent />
    </Suspense>
  )
}
