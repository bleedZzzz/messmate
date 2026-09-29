"use client"

import { use, useState } from "react"
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
  Sparkles,
  CheckCircle2,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
} from "lucide-react"

export default function ProviderDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id: providerId } = use(params)
  const searchParams = useSearchParams()
  const clusterId = searchParams.get("cluster") || undefined
  const [activeTab, setActiveTab] = useState<"menu" | "negotiation">("menu")

  // 1. Fetch Provider Profile
  const {
    data: provider,
    isLoading: providerLoading,
    isError: providerError,
  } = useQuery({
    queryKey: ["provider", providerId],
    queryFn: () => api.getProvider(providerId),
  })

  // 2. Fetch Menu Plan
  const { data: menu, isLoading: menuLoading } = useQuery({
    queryKey: ["menu", providerId, clusterId],
    queryFn: () => (clusterId ? api.getMenu(providerId, clusterId) : null),
    enabled: !!clusterId,
  })

  // 3. Fetch Negotiation Result
  const { data: negotiation, isLoading: negotiationLoading } = useQuery({
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
        <div className="h-8 w-48 bg-white/[0.06] rounded-xl animate-pulse" />
        <SkeletonLoader count={2} />
      </div>
    )
  }

  if (providerError || !provider) {
    return (
      <div className="p-16 text-center cyber-panel rounded-3xl border border-white/[0.08] flex flex-col items-center gap-4 my-8">
        <h2 className="text-xl font-bold font-mono text-white">
          Provider Telemetry Not Found
        </h2>
        <p className="text-xs text-neutral-400">
          The requested provider does not exist or may still be pending verification.
        </p>
        <Link
          href="/"
          className="mt-2 px-5 py-2.5 rounded-xl bg-amber-500 text-neutral-950 font-mono text-xs font-bold hover:bg-amber-400 transition-colors"
        >
          Return to Search Console
        </Link>
      </div>
    )
  }

  const capacityPercent = Math.round(
    ((provider.capacity_total - provider.capacity_available) / provider.capacity_total) * 100
  )

  return (
    <div className="flex flex-col gap-8 py-2">
      {/* Back button */}
      <Link
        href="/results"
        className="inline-flex items-center gap-2 text-xs font-mono font-semibold text-neutral-400 hover:text-amber-400 transition-colors self-start px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08]"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Ranked Results
      </Link>

      {/* Provider Hero Header */}
      <div className="p-6 sm:p-9 rounded-3xl cyber-panel-glow border border-white/[0.1] flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8 relative overflow-hidden">
        <div className="flex flex-col gap-3 max-w-2xl relative z-10">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl sm:text-4xl font-black text-white">
              {provider.name}
            </h1>
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-semibold">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Verified Partner
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3.5 text-xs font-mono text-neutral-400">
            <span className="flex items-center gap-1 text-neutral-300">
              <MapPin className="w-3.5 h-3.5 text-amber-400" />
              {provider.area}, {provider.town}
            </span>
            <span>·</span>
            <span className="flex items-center gap-1 text-amber-400 font-bold">
              <Star className="w-3.5 h-3.5 fill-amber-400" /> {provider.rating.toFixed(1)} / 5.0 Rating
            </span>
            <span>·</span>
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5 text-neutral-400" />
              {provider.capacity_available} / {provider.capacity_total} Seats Available
            </span>
          </div>

          {/* Capacity Progress Bar */}
          <div className="flex items-center gap-3 pt-1">
            <div className="w-48 h-2 bg-neutral-800 rounded-full overflow-hidden border border-white/[0.06]">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-emerald-400 rounded-full transition-all"
                style={{ width: `${Math.min(100, capacityPercent)}%` }}
              />
            </div>
            <span className="text-[10px] font-mono text-neutral-400">
              {capacityPercent}% Occupancy
            </span>
          </div>

          {/* Cuisine Chips */}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {provider.cuisines.map((c) => (
              <span
                key={c}
                className="px-3 py-1 rounded-xl bg-white/[0.05] border border-white/[0.08] text-neutral-300 text-xs font-mono capitalize"
              >
                {c.replace("_", " ")}
              </span>
            ))}
          </div>
        </div>

        {/* Pricing & WhatsApp Contact CTA */}
        <div className="flex flex-col sm:items-end gap-4 w-full lg:w-auto p-5 rounded-2xl bg-[#0c0e14] border border-white/[0.08] relative z-10 shrink-0">
          <div className="text-left sm:text-right">
            <span className="text-[10px] font-mono uppercase tracking-wider text-neutral-400 block">
              Base List Subscription
            </span>
            <span className="text-3xl font-black font-mono text-white">
              ₹{Math.round(provider.list_price_monthly)}
              <span className="text-xs font-normal text-neutral-400 ml-1">/mo</span>
            </span>
            <span className="text-[11px] font-mono text-neutral-400 block mt-0.5">
              60 Meals (2 meals/day × 30 days)
            </span>
          </div>

          {contact?.whatsapp_url ? (
            <a
              href={contact.whatsapp_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-mono font-bold text-xs shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all cursor-pointer group"
            >
              <MessageCircle className="w-4 h-4 fill-white" />
              <span>Direct WhatsApp Contact</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </a>
          ) : (
            <button
              disabled
              className="px-6 py-3 rounded-2xl bg-neutral-800 text-neutral-500 font-mono text-xs cursor-not-allowed"
            >
              Contact Unavailable
            </button>
          )}
        </div>
      </div>

      {/* Cockpit Sub-Navigation Tabs */}
      <div className="flex items-center gap-3 border-b border-white/[0.08] pb-1">
        <button
          type="button"
          onClick={() => setActiveTab("menu")}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl font-mono text-xs font-bold transition-all cursor-pointer ${
            activeTab === "menu"
              ? "bg-amber-500 text-neutral-950 shadow-[0_0_15px_rgba(245,158,11,0.3)]"
              : "text-neutral-400 hover:text-white hover:bg-white/[0.04]"
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>7-Day Rotating Menu Plan</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("negotiation")}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl font-mono text-xs font-bold transition-all cursor-pointer ${
            activeTab === "negotiation"
              ? "bg-amber-500 text-neutral-950 shadow-[0_0_15px_rgba(245,158,11,0.3)]"
              : "text-neutral-400 hover:text-white hover:bg-white/[0.04]"
          }`}
        >
          <Percent className="w-4 h-4" />
          <span>Deal Agent Negotiation Simulator</span>
          {negotiation && (
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1" />
          )}
        </button>
      </div>

      {/* Tab 1: Menu Grid Section */}
      {activeTab === "menu" && (
        <section className="flex flex-col gap-4">
          {menuLoading ? (
            <SkeletonLoader count={1} />
          ) : menu ? (
            <MenuGrid menu={menu} />
          ) : (
            <div className="p-12 rounded-3xl cyber-panel border border-white/[0.08] text-center text-xs font-mono text-neutral-400 flex flex-col items-center gap-2">
              <Calendar className="w-8 h-8 text-neutral-600 mb-1" />
              <span>Select a student demand cluster from search to inspect personalized rotating meal plans.</span>
            </div>
          )}
        </section>
      )}

      {/* Tab 2: Negotiation Simulation */}
      {activeTab === "negotiation" && (
        <section className="flex flex-col gap-6">
          {negotiation ? (
            <div className="p-6 sm:p-9 rounded-3xl cyber-panel border border-white/[0.1] shadow-2xl flex flex-col gap-7">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.08] pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center shrink-0">
                    <Percent className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold font-mono text-white">
                      AI Deal Agent Negotiation Simulator
                    </h2>
                    <p className="text-xs text-neutral-400 font-mono mt-0.5">
                      Autonomous game-theory rounds between hostel group demand & provider economics
                    </p>
                  </div>
                </div>

                <span className="px-3.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-bold uppercase tracking-wider self-start sm:self-auto">
                  Status: {negotiation.status.replace("_", " ")}
                </span>
              </div>

              {/* Outcome Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-[#0c0e14] border border-amber-500/30 flex flex-col gap-1 shadow-[0_0_15px_rgba(245,158,11,0.1)]">
                  <span className="text-[11px] font-mono text-neutral-400">Suggested Final Rate</span>
                  <span className="text-2xl font-black font-mono text-amber-300">
                    ₹{negotiation.final_price ? Math.round(negotiation.final_price) : "N/A"}
                    <span className="text-xs font-normal text-neutral-400 ml-1">/mo</span>
                  </span>
                  <span className="text-[10px] text-neutral-400">Group subscription rate</span>
                </div>

                <div className="p-4 rounded-2xl bg-[#0c0e14] border border-emerald-500/30 flex flex-col gap-1 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                  <span className="text-[11px] font-mono text-neutral-400">Volume Cluster Discount</span>
                  <span className="text-2xl font-black font-mono text-emerald-400 flex items-center gap-1.5">
                    <TrendingDown className="w-5 h-5" />
                    {Math.round(negotiation.volume_discount * 100)}% Off
                  </span>
                  <span className="text-[10px] text-emerald-400/80">Applied for group headcount</span>
                </div>

                <div className="p-4 rounded-2xl bg-[#0c0e14] border border-white/[0.08] flex flex-col gap-1">
                  <span className="text-[11px] font-mono text-neutral-400">Provider Cost Floor</span>
                  <span className="text-2xl font-black font-mono text-neutral-300">
                    ₹{Math.round(negotiation.floor)}
                  </span>
                  <span className="text-[10px] text-neutral-400">Non-negotiable operational baseline</span>
                </div>

                <div className="p-4 rounded-2xl bg-[#0c0e14] border border-white/[0.08] flex flex-col gap-1">
                  <span className="text-[11px] font-mono text-neutral-400">Student Budget Ceiling</span>
                  <span className="text-2xl font-black font-mono text-neutral-300">
                    ₹{Math.round(negotiation.ceiling)}
                  </span>
                  <span className="text-[10px] text-neutral-400">Target cluster monthly max</span>
                </div>
              </div>

              {/* AI Negotiation Summary Note */}
              <div className="p-4 rounded-xl bg-amber-500/[0.06] border border-amber-500/20 text-xs font-mono text-neutral-200 leading-relaxed flex items-start gap-2.5">
                <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-amber-400 block mb-0.5">Negotiation Outcome Analysis:</strong>
                  {negotiation.note}
                </div>
              </div>

              {/* Composable Timeline of Rounds */}
              <div className="flex flex-col gap-4 pt-2">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-neutral-400">
                  Round-by-Round Bargaining Transcript
                </h3>

                <Timeline>
                  {negotiation.rounds.map((round) => {
                    const isFinal = round.round === negotiation.rounds.length
                    return (
                      <TimelineItem key={round.round}>
                        <TimelinePoint active={isFinal}>
                          <span className="text-[10px] font-mono font-bold">{round.round}</span>
                        </TimelinePoint>
                        <TimelineContent>
                          <div className="flex items-center gap-3">
                            <span className="font-mono font-bold text-xs text-white">
                              Round {round.round}
                            </span>
                            {isFinal && (
                              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                                Final Agreement Reached
                              </span>
                            )}
                          </div>
                          <div className="flex flex-wrap items-center gap-4 text-xs font-mono mt-1.5 p-3 rounded-xl bg-[#0c0e14] border border-white/[0.06]">
                            <span className="text-neutral-300">
                              Provider Ask: <strong className="text-white">₹{Math.round(round.provider_ask)}</strong>
                            </span>
                            <span className="text-neutral-600">·</span>
                            <span className="text-neutral-300">
                              Student Bid: <strong className="text-amber-400">₹{Math.round(round.cluster_bid)}</strong>
                            </span>
                            <span className="text-neutral-600">·</span>
                            <span className="text-neutral-400 text-[11px]">
                              Spread: ₹{Math.round(round.provider_ask - round.cluster_bid)}
                            </span>
                          </div>
                        </TimelineContent>
                      </TimelineItem>
                    )
                  })}
                </Timeline>
              </div>
            </div>
          ) : (
            <div className="p-12 rounded-3xl cyber-panel border border-white/[0.08] text-center text-xs font-mono text-neutral-400 flex flex-col items-center gap-2">
              <Percent className="w-8 h-8 text-neutral-600 mb-1" />
              <span>Cluster context required to run automated deal negotiation simulation.</span>
            </div>
          )}
        </section>
      )}

      {/* Pricing Disclaimer */}
      <div className="flex items-start gap-3 p-4 rounded-2xl cyber-panel border border-amber-500/20 text-xs font-mono text-neutral-300">
        <ShieldAlert className="w-5 h-5 shrink-0 text-amber-400 mt-0.5" />
        <p>
          <strong className="text-amber-400">Disclaimer:</strong> The suggested group subscription rate and volume discount percentage are heuristic references generated by the multi-agent optimization model. Delivery logistics and trial meals are finalized directly with the mess proprietor.
        </p>
      </div>
    </div>
  )
}
