import Link from "next/link"
import { ProviderMatch, Provider } from "@/lib/schemas"
import { MapPin, Star, ArrowRight, Check } from "lucide-react"

export interface ProviderCardProps {
  rank: number
  match: ProviderMatch
  provider?: Provider
  clusterId?: string
}

export function ProviderCard({ rank, match, provider, clusterId }: ProviderCardProps) {
  const scorePercent = Math.round(match.score * 100)
  const providerName = provider?.name || `Provider #${match.provider_id.split("-").pop()}`
  const locality = provider ? `${provider.area}, ${provider.town}` : "Verified Area"
  const price = provider?.list_price_monthly ? `₹${Math.round(provider.list_price_monthly)}` : "Contact"
  const cuisines = provider?.cuisines || []

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-5 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm hover:shadow-md transition-shadow gap-4">
      <div className="flex items-start gap-4">
        {/* Rank & Score Badge */}
        <div className="flex flex-col items-center justify-center w-14 h-14 rounded-2xl bg-orange-50 dark:bg-orange-950/60 border border-orange-200 dark:border-orange-800/60 shrink-0">
          <span className="text-[11px] font-bold text-orange-600 dark:text-orange-400">
            #{rank}
          </span>
          <span className="text-xs font-extrabold text-stone-900 dark:text-stone-100">
            {scorePercent}%
          </span>
        </div>

        <div className="flex flex-col gap-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-bold text-base text-stone-900 dark:text-stone-100">
              {providerName}
            </h3>
            {rank === 1 && (
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 text-[10px] font-semibold flex items-center gap-1">
                <Check className="w-3 h-3" /> Top Pick
              </span>
            )}
            {provider?.rating && (
              <span className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 font-medium">
                <Star className="w-3.5 h-3.5 fill-current" /> {provider.rating.toFixed(1)}
              </span>
            )}
          </div>

          <div className="flex items-center gap-1 text-xs text-stone-500 dark:text-stone-400">
            <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0" />
            <span>{locality}</span>
            <span>·</span>
            <span>{match.distance_km} km away</span>
          </div>

          <p className="text-xs font-medium text-orange-950/80 dark:text-orange-200/90 bg-orange-50/60 dark:bg-orange-950/30 px-2.5 py-1 rounded-lg border border-orange-100 dark:border-orange-900/40 inline-block">
            {match.reason}
          </p>

          {cuisines.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-0.5">
              {cuisines.map((c) => (
                <span
                  key={c}
                  className="px-2 py-0.5 rounded-md bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-400 text-[10px] capitalize font-medium"
                >
                  {c.replace("_", " ")}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-stone-100 dark:border-stone-800 gap-3 shrink-0">
        <div className="text-left sm:text-right">
          <span className="text-[11px] text-stone-500 block">List Subscription</span>
          <span className="text-lg font-bold text-stone-900 dark:text-stone-100">
            {price}
            <span className="text-xs font-normal text-stone-500">/mo</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href={`/provider/${match.provider_id}${clusterId ? `?cluster=${clusterId}` : ""}`}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-orange-600 text-white font-medium text-xs hover:bg-orange-700 transition-colors shadow-sm shadow-orange-600/20"
          >
            <span>View Menu & Deal</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  )
}
