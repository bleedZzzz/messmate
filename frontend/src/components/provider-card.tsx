import Link from "next/link"
import { ProviderMatch, Provider } from "@/lib/schemas"
import { MapPin, Star, ArrowRight, CheckCircle2, Utensils, Users, Sparkles, ShieldCheck } from "lucide-react"

export interface ProviderCardProps {
  rank: number
  match: ProviderMatch
  provider?: Provider
  clusterId?: string
}

export function ProviderCard({ rank, match, provider, clusterId }: ProviderCardProps) {
  const scorePercent = Math.round(match.score * 100)
  const providerName = provider?.name || `Provider #${match.provider_id.split("-").pop()}`
  const locality = provider ? `${provider.area}, ${provider.town}` : "Verified University Belt"
  const price = provider?.list_price_monthly ? `₹${Math.round(provider.list_price_monthly)}` : "Contact"
  const cuisines = provider?.cuisines || []

  // Factor breakdown computation for display
  const distanceScore = Math.max(0, Math.min(100, Math.round((1 - Math.min(match.distance_km, 5) / 5) * 100)))
  const isTopPick = rank === 1

  return (
    <div
      className={`p-6 rounded-3xl cyber-panel transition-all flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative overflow-hidden group hover:border-amber-500/50 hover:shadow-[0_0_30px_rgba(245,158,11,0.15)] ${
        isTopPick ? "border-amber-500/40 bg-gradient-to-r from-amber-500/[0.04] to-transparent" : "border-white/[0.08]"
      }`}
    >
      {/* Top Banner Ribbon for Rank 1 */}
      {isTopPick && (
        <div className="absolute top-0 right-0 bg-gradient-to-l from-amber-500 to-amber-600 text-neutral-950 font-mono text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-bl-xl shadow-md flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-neutral-950 fill-neutral-950" />
          <span>Top AI Recommendation</span>
        </div>
      )}

      {/* Left side: Rank badge + Provider Info */}
      <div className="flex items-start gap-4 sm:gap-5 w-full lg:w-auto">
        {/* Score & Rank Dial Badge */}
        <div className="flex flex-col items-center justify-center w-16 h-16 rounded-2xl bg-[#0c0e14] border border-amber-500/30 text-center shrink-0 shadow-[0_0_15px_rgba(245,158,11,0.1)] group-hover:border-amber-500/60 transition-colors">
          <span className="font-mono text-[10px] font-bold text-amber-400">
            #{rank.toString().padStart(2, "0")}
          </span>
          <span className="font-mono font-black text-base text-white">
            {scorePercent}%
          </span>
          <span className="text-[8px] font-mono text-neutral-400 uppercase">Match</span>
        </div>

        {/* Content Block */}
        <div className="flex flex-col gap-2 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-black text-lg text-white group-hover:text-amber-300 transition-colors">
              {providerName}
            </h3>

            {provider?.rating && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-xs font-mono font-bold text-amber-300">
                <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                {provider.rating.toFixed(1)}
              </span>
            )}

            {provider?.capacity_available !== undefined && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-mono text-emerald-300">
                <Users className="w-3 h-3 text-emerald-400" />
                {provider.capacity_available} seats open
              </span>
            )}
          </div>

          {/* Location & Distance */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-neutral-400 font-mono">
            <span className="flex items-center gap-1 text-neutral-300">
              <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              {locality}
            </span>
            <span>·</span>
            <span className="text-amber-400 font-semibold">{match.distance_km} km radius</span>
          </div>

          {/* AI Agent Reasoning Quote Box */}
          <div className="p-3 rounded-xl bg-amber-500/[0.06] border border-amber-500/20 text-neutral-200 text-xs leading-relaxed mt-1 flex items-start gap-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-mono text-[10px] uppercase font-bold text-amber-400 mr-1.5">
                Match Agent Rationale:
              </span>
              <span>{match.reason}</span>
            </div>
          </div>

          {/* Cuisines & Diet Tags */}
          {cuisines.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-1">
              {cuisines.map((c) => (
                <span
                  key={c}
                  className="px-2.5 py-0.5 rounded-lg bg-white/[0.05] border border-white/[0.08] text-neutral-300 text-[11px] font-mono capitalize"
                >
                  {c.replace("_", " ")}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right side: Pricing & Actions */}
      <div className="flex lg:flex-col items-center lg:items-end justify-between w-full lg:w-auto pt-4 lg:pt-0 border-t lg:border-t-0 border-white/[0.08] gap-4 shrink-0">
        <div className="text-left lg:text-right">
          <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-400 block">
            List Subscription
          </span>
          <span className="font-mono font-black text-2xl text-white">
            {price}
            <span className="text-xs font-normal text-neutral-400 ml-1">/mo</span>
          </span>
          <span className="text-[10px] text-emerald-400 font-mono block">
            Eligible for volume discount
          </span>
        </div>

        <Link
          href={`/provider/${match.provider_id}${clusterId ? `?cluster=${clusterId}` : ""}`}
          className="inline-flex items-center gap-2 px-5 py-3 rounded-2xl bg-amber-500 hover:bg-amber-400 text-neutral-950 font-black text-xs font-mono uppercase tracking-wider shadow-[0_0_20px_rgba(245,158,11,0.25)] hover:shadow-[0_0_25px_rgba(245,158,11,0.4)] transition-all cursor-pointer group/btn"
        >
          <span>Simulate Deal & Menu</span>
          <ArrowRight className="w-3.5 h-3.5 text-neutral-950 stroke-[2.5] group-hover/btn:translate-x-1 transition-transform" />
        </Link>
      </div>
    </div>
  )
}
