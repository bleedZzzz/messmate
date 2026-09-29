import Link from "next/link"
import { ShieldAlert, ExternalLink, Terminal, Sparkles } from "lucide-react"

export function Footer() {
  return (
    <footer className="w-full border-t border-white/[0.08] bg-[#07080a]/90 backdrop-blur-md mt-20 py-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col gap-6">
        {/* Transparent Simulated Notice */}
        <div className="flex items-start gap-3.5 p-4 rounded-2xl border border-amber-500/20 bg-amber-500/[0.04] text-neutral-300 text-xs leading-relaxed">
          <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
          <p>
            <strong className="text-amber-300 font-semibold">Important Pricing Disclaimer:</strong> All simulated subscription rates, margin splits, and cluster discounts computed by the Deal Agent are{" "}
            <span className="text-neutral-200 underline decoration-amber-500/50">heuristic decision-support references, not formal commercial offers</span>. Final subscriptions and delivery slots are finalized directly with the independent mess operator via WhatsApp.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-white/[0.05] text-xs text-neutral-500">
          <div className="flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-neutral-400" />
            <span>MessMate Swarm Engine · Bengali & East India University Belts</span>
          </div>

          <div className="flex items-center gap-4 text-neutral-400">
            <Link href="/about" className="hover:text-amber-400 transition-colors">
              Agent Graph Trace
            </Link>
            <span className="text-neutral-700">|</span>
            <Link href="/onboard" className="hover:text-amber-400 transition-colors">
              Mess Onboarding
            </Link>
            <span className="text-neutral-700">|</span>
            <a
              href="https://github.com/bleedZzzz/messmate"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 hover:text-white transition-colors"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
