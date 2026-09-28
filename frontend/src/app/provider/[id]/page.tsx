"use client"

import { use } from "react"
import { useSearchParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { api } from "@/lib/api"
import { MenuGrid } from "@/components/menu-grid"
import {
  Timeline,
  TimelineItem,
  TimelinePoint,
  TimelineContent,
} from "@/components/timeline"
import { SkeletonLoader } from "@/components/skeleton-loader"
import {
  ArrowLeft,
  MapPin,
  Star,
  Users,
  MessageCircle,
  ShieldAlert,
  Percent,
  TrendingDown,
} from "lucide-react"

export default function ProviderDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id: providerId } = use(params)
  const searchParams = useSearchParams()
  const clusterId = searchParams.get("cluster") || undefined

  // 1. Fetch Provider Profile
  const {
    data: provider,
    isLoading: providerLoading,
    isError: providerError,
  } = useQuery({
    queryKey: ["provider", providerId],
    queryFn: () => api.getProvider(providerId),
  })

  // 2. Fetch Menu Plan (if clusterId provided, otherwise fallback to provider alone)
  const { data: menu, isLoading: menuLoading } = useQuery({
    queryKey: ["menu", providerId, clusterId],
    queryFn: () => (clusterId ? api.getMenu(providerId, clusterId) : null),
    enabled: !!clusterId,
  })

  // 3. Fetch Negotiation Result
  const { data: negotiation } = useQuery({
    queryKey: ["negotiate", providerId, clusterId],
    queryFn: () => (clusterId ? api.negotiate(providerId, clusterId, 5) : null),
    enabled: !!clusterId,
  })

  // 4. Fetch WhatsApp Contact URL
  const { data: contact } = useQuery({
    queryKey: ["contact", providerId],
    queryFn: () => api.getContact(providerId),
  })

  if (providerLoading) {
    return (
      <div className="py-8 flex flex-col gap-6">
        <div className="h-6 w-32 bg-stone-200 dark:bg-stone-800 rounded-md animate-pulse" />
        <SkeletonLoader count={2} />
      </div>
    )
  }

  if (providerError || !provider) {
    return (
      <div className="p-12 text-center flex flex-col items-center gap-3">
        <h2 className="text-lg font-bold text-stone-900 dark:text-stone-100">
          Provider Not Found
        </h2>
        <p className="text-xs text-stone-500">
          The requested provider does not exist or may be awaiting approval.
        </p>
        <Link
          href="/"
          className="mt-2 px-4 py-2 rounded-xl bg-orange-600 text-white text-xs font-semibold"
        >
          Back to Search
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Back button */}
      <Link
        href="/results"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 dark:text-stone-400 hover:text-orange-600 transition-colors self-start"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Match Results
      </Link>

      {/* Provider Hero Header */}
      <div className="p-6 sm:p-8 rounded-3xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-stone-900 dark:text-stone-100">
              {provider.name}
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 text-xs font-semibold">
              Verified Partner
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-stone-500 dark:text-stone-400">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-stone-400" />
              {provider.area}, {provider.town}
            </span>
            <span>·</span>
            <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400 font-semibold">
              <Star className="w-3.5 h-3.5 fill-current" /> {provider.rating.toFixed(1)} / 5.0
            </span>
            <span>·</span>
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5 text-stone-400" />
              {provider.capacity_available} / {provider.capacity_total} Seats Available
            </span>
          </div>

          <div className="flex flex-wrap gap-1.5 mt-1">
            {provider.cuisines.map((c) => (
              <span
                key={c}
                className="px-2.5 py-0.5 rounded-md bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 text-xs capitalize font-medium"
              >
                {c.replace("_", " ")}
              </span>
            ))}
          </div>
        </div>

        {/* Pricing & Contact CTA */}
        <div className="flex flex-col sm:items-end gap-3 w-full md:w-auto p-4 rounded-2xl bg-orange-50/50 dark:bg-orange-950/20 border border-orange-100 dark:border-orange-900/40">
          <div className="text-left sm:text-right">
            <span className="text-[11px] text-stone-500 block">Base Subscription</span>
            <span className="text-2xl font-black text-stone-900 dark:text-stone-100">
              ₹{Math.round(provider.list_price_monthly)}
              <span className="text-xs font-normal text-stone-500">/month</span>
            </span>
            <span className="text-[10px] text-stone-400 block mt-0.5">
              Includes 60 meals (2 meals/day x 30 days)
            </span>
          </div>

          {contact?.whatsapp_url ? (
            <a
              href={contact.whatsapp_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-600/20 transition-all"
            >
              <MessageCircle className="w-4 h-4" />
              <span>Contact on WhatsApp</span>
            </a>
          ) : (
            <button
              disabled
              className="px-5 py-2.5 rounded-xl bg-stone-200 dark:bg-stone-800 text-stone-400 text-xs font-semibold cursor-not-allowed"
            >
              Contact Unavailable
            </button>
          )}
        </div>
      </div>

      {/* Menu Grid Section */}
      <section className="flex flex-col gap-4">
        {menuLoading ? (
          <SkeletonLoader count={1} />
        ) : menu ? (
          <MenuGrid menu={menu} />
        ) : (
          <div className="p-6 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 text-center text-xs text-stone-500">
            Select a student demand cluster from search to view tailored rotating meal plans.
          </div>
        )}
      </section>

      {/* Negotiation Simulation Timeline */}
      {negotiation && (
        <section className="p-6 sm:p-8 rounded-3xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 shadow-sm flex flex-col gap-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 dark:border-stone-800 pb-4">
            <div>
              <h2 className="text-lg font-bold text-stone-900 dark:text-stone-100 flex items-center gap-2">
                <Percent className="w-5 h-5 text-orange-600" />
                AI Deal Agent Negotiation Simulation
              </h2>
              <p className="text-xs text-stone-500">
                Simulated bargaining rounds between hostel group demand and provider economics
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-orange-100 dark:bg-orange-950 text-orange-800 dark:text-orange-300 text-xs font-bold uppercase tracking-wider">
                Status: {negotiation.status.replace("_", " ")}
              </span>
            </div>
          </div>

          {/* Outcome Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl border border-stone-100 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/40 flex flex-col gap-0.5">
              <span className="text-[11px] text-stone-400">Suggested Final Rate</span>
              <span className="text-lg font-extrabold text-stone-900 dark:text-stone-100">
                ₹{negotiation.final_price ? Math.round(negotiation.final_price) : "N/A"}
                <span className="text-xs font-normal text-stone-400">/mo</span>
              </span>
            </div>

            <div className="p-3.5 rounded-xl border border-stone-100 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/40 flex flex-col gap-0.5">
              <span className="text-[11px] text-stone-400">Volume Discount</span>
              <span className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <TrendingDown className="w-4 h-4" />
                {Math.round(negotiation.volume_discount * 100)}%
              </span>
            </div>

            <div className="p-3.5 rounded-xl border border-stone-100 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/40 flex flex-col gap-0.5">
              <span className="text-[11px] text-stone-400">Provider Cost Floor</span>
              <span className="text-lg font-bold text-stone-700 dark:text-stone-300">
                ₹{Math.round(negotiation.floor)}
              </span>
            </div>

            <div className="p-3.5 rounded-xl border border-stone-100 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/40 flex flex-col gap-0.5">
              <span className="text-[11px] text-stone-400">Student Budget Ceiling</span>
              <span className="text-lg font-bold text-stone-700 dark:text-stone-300">
                ₹{Math.round(negotiation.ceiling)}
              </span>
            </div>
          </div>

          {/* AI Negotiation Summary Note */}
          <div className="p-4 rounded-xl border border-orange-100 dark:border-orange-950 bg-orange-50/40 dark:bg-orange-950/20 text-xs text-orange-950 dark:text-orange-200">
            <strong className="font-semibold block mb-0.5">Negotiation Outcome Summary:</strong>
            {negotiation.note}
          </div>

          {/* Composable Timeline of Rounds */}
          <div className="flex flex-col gap-3 mt-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-stone-500">
              Round-by-Round Bargaining Transcript
            </h3>

            <Timeline>
              {negotiation.rounds.map((round) => {
                const isFinal = round.round === negotiation.rounds.length
                return (
                  <TimelineItem key={round.round}>
                    <TimelinePoint active={isFinal}>
                      <span className="text-[10px] font-bold">{round.round}</span>
                    </TimelinePoint>
                    <TimelineContent>
                      <div className="flex items-center gap-3">
                        <span className="font-semibold text-xs text-stone-900 dark:text-stone-100">
                          Round {round.round}
                        </span>
                        {isFinal && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                            Final Round
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-4 text-xs mt-1">
                        <span className="text-stone-600 dark:text-stone-400">
                          Provider Ask: <strong>₹{Math.round(round.provider_ask)}</strong>
                        </span>
                        <span>·</span>
                        <span className="text-stone-600 dark:text-stone-400">
                          Student Bid: <strong>₹{Math.round(round.cluster_bid)}</strong>
                        </span>
                        <span>·</span>
                        <span className="text-stone-400 text-[11px]">
                          Spread: ₹{Math.round(round.provider_ask - round.cluster_bid)}
                        </span>
                      </div>
                    </TimelineContent>
                  </TimelineItem>
                )
              })}
            </Timeline>
          </div>
        </section>
      )}

      {/* Pricing Disclaimer */}
      <div className="flex items-start gap-3 p-4 rounded-2xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/50 dark:bg-amber-950/20 text-xs text-amber-900 dark:text-amber-200">
        <ShieldAlert className="w-5 h-5 shrink-0 text-amber-600 dark:text-amber-400" />
        <p>
          <strong className="font-semibold">Notice:</strong> Negotiated rates displayed above are
          algorithmic references calculated from volume discount tiers and provider cost floors. They
          are intended to empower student group conversations and do not constitute legal contracts.
        </p>
      </div>
    </div>
  )
}
