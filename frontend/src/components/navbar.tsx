import Link from "next/link"
import { Cpu, Sparkles, UserPlus, Info, ExternalLink } from "lucide-react"

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/[0.08] bg-[#08090c]/80 backdrop-blur-xl transition-all">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 via-orange-600 to-amber-700 p-[1px] shadow-lg shadow-amber-500/20 group-hover:shadow-amber-500/35 transition-all">
            <div className="w-full h-full bg-[#0d0f15] rounded-[11px] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-amber-400 group-hover:scale-110 transition-transform" />
            </div>
          </div>

          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base sm:text-lg tracking-tight text-white group-hover:text-amber-400 transition-colors">
                MessMate
              </span>
              <span className="text-[10px] font-mono font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300">
                AI SWARM
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] text-neutral-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-mono text-[10px]">LangGraph 4-Agent Orchestrator</span>
            </div>
          </div>
        </Link>

        {/* Navigation Items */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            href="/"
            className="px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-neutral-300 hover:text-white hover:bg-white/[0.05] transition-all"
          >
            Find Tiffins
          </Link>
          <Link
            href="/onboard"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-neutral-300 hover:text-amber-400 hover:bg-white/[0.05] transition-all"
          >
            <UserPlus className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">Partner Onboarding</span>
          </Link>
          <Link
            href="/about"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-neutral-300 hover:text-neutral-100 hover:bg-white/[0.05] transition-all"
          >
            <Cpu className="w-3.5 h-3.5 text-neutral-400" />
            <span className="hidden sm:inline">Agent Architecture</span>
          </Link>

          <a
            href="https://github.com/bleedZzzz/messmate"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-neutral-900 border border-white/[0.12] text-neutral-200 hover:border-amber-500/40 hover:text-amber-300 hover:bg-neutral-800 transition-all shadow-xs"
          >
            <span>GitHub</span>
            <ExternalLink className="w-3 h-3 text-neutral-400" />
          </a>
        </nav>
      </div>
    </header>
  )
}
