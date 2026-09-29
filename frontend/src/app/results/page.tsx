"use client"

import { Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { api } from "@/lib/api"
import { ProviderCard } from "@/components/provider-card"
import { AgentTracePanel } from "@/components/trace-panel"
import { SkeletonLoader } from "@/components/skeleton-loader"
import { Users, MapPin, IndianRupee, ArrowLeft, RefreshCw, AlertCircle, Compass, Sparkles, Filter } from "lucide-react"

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
      <div className="flex flex-col gap-8 py-6">
        <div className="cyber-panel p-6 rounded-3xl border border-white/[0.08] flex flex-col gap-3">
          <div className="h-6 bg-white/[0.08] rounded-xl w-64 animate-pulse" />
          <div className="h-4 bg-white/[0.05] rounded-xl w-96 animate-pulse" />
        </div>
        <SkeletonLoader count={4} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded-3xl border border-red-500/30 bg-red-950/20 gap-5 my-8 cyber-panel">
        <div className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
          <AlertCircle className="w-7 h-7" />
        </div>
        <div className="flex flex-col gap-1 max-w-md">
          <h2 className="text-lg font-bold font-mono text-red-200">
            Optimization Pipeline Execution Error
          </h2>
          <p className="text-xs text-neutral-400 leading-relaxed">
            {error instanceof Error ? error.message : "Unable to reach FastAPI backend server. Ensure backend is running at http://localhost:8000."}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-mono text-xs font-bold transition-all shadow-lg cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Re-trigger Pipeline
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
      {/* Top Breadcrumb & Controls */}
      <div className="flex flex-col gap-4">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-mono font-semibold text-neutral-400 hover:text-amber-400 transition-colors self-start px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08]"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Return to Swarm Console
        </Link>

        {/* Matched Demand Cluster Mission Briefing */}
        {cluster ? (
          <div className="p-6 sm:p-8 rounded-3xl cyber-panel-glow flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
            <div className="flex flex-col gap-2 relative z-10">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 font-mono text-[10px] uppercase font-bold w-fit">
                <Compass className="w-3 h-3 text-amber-400" />
                <span>Geospatial Demand Cluster Found</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white flex items-center gap-2.5">
                <MapPin className="w-6 h-6 text-amber-400 shrink-0" />
                {cluster.area}, {cluster.town}
              </h1>
              <p className="text-xs text-neutral-400 font-mono">
                Centroid: {cluster.lat.toFixed(4)}°N, {cluster.lon.toFixed(4)}°E · Radius: {radiusKm} km
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-neutral-300 bg-[#0a0c10]/90 p-4 rounded-2xl border border-white/[0.1] relative z-10 shadow-inner">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-amber-400" />
                <span>
                  <strong className="text-white text-sm">{cluster.headcount}</strong> Students
                </span>
              </div>
              <span className="text-neutral-600">|</span>
              <div className="flex items-center gap-2">
                <IndianRupee className="w-4 h-4 text-emerald-400" />
                <span>
                  Ceiling: <strong className="text-white text-sm">₹{Math.round(cluster.budget_ceiling_monthly)}</strong>/mo
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 rounded-2xl cyber-panel text-xs font-mono text-amber-300 border border-amber-500/30">
            Town-wide broad search active. Displaying top qualifying verified mess providers.
          </div>
        )}
      </div>

      {/* Agent Observability Trace Panel */}
      <AgentTracePanel trace={trace} errors={errors} />

      {/* Ranked Results List */}
      <section className="flex flex-col gap-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/[0.08] pb-3">
          <div className="flex items-center gap-2">
            <h2 className="font-mono font-bold text-lg text-white">
              Ranked Tiffin Providers
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 font-bold">
              {matches.length} Verified
            </span>
          </div>

          <span className="text-xs font-mono text-neutral-500">
            Deterministic 5-Factor Weighted Score
          </span>
        </div>

        {matches.length === 0 ? (
          <div className="p-16 text-center rounded-3xl cyber-panel border border-white/[0.08] flex flex-col items-center gap-4">
            <MapPin className="w-10 h-10 text-neutral-600" />
            <div className="flex flex-col gap-1 max-w-sm">
              <h3 className="font-mono font-bold text-white text-base">
                No Qualifying Tiffins Located
              </h3>
              <p className="text-xs text-neutral-400">
                Try expanding the search radius or raising the monthly budget ceiling.
              </p>
            </div>
            <Link
              href="/"
              className="mt-2 px-5 py-2.5 rounded-xl bg-amber-500 text-neutral-950 font-mono text-xs font-bold hover:bg-amber-400 transition-colors"
            >
              Adjust Telemetry Filters
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {matches.map((match, index) => (
              <ProviderCard
                key={match.provider_id}
                rank={index + 1}
                match={match}
                provider={match.provider_id === data?.top_provider?.id ? data?.top_provider : undefined}
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
    <Suspense
      fallback={
        <div className="py-12 flex flex-col gap-6">
          <div className="h-24 bg-white/[0.05] rounded-3xl animate-pulse" />
          <SkeletonLoader count={3} />
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  )
}
