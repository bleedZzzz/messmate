import Link from "next/link"
import { UtensilsCrossed, Info, UserPlus } from "lucide-react"

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-stone-200 dark:border-stone-800 glass-panel">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-orange-600 text-white flex items-center justify-center shadow-md shadow-orange-500/20 group-hover:scale-105 transition-transform">
            <UtensilsCrossed className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg leading-tight tracking-tight text-stone-900 dark:text-stone-100 flex items-center gap-1.5">
              MessMate
              <span className="text-[10px] font-semibold tracking-wider uppercase px-1.5 py-0.5 rounded-full bg-orange-100 dark:bg-orange-950/60 text-orange-700 dark:text-orange-300">
                AI Match
              </span>
            </span>
            <span className="text-xs text-stone-500 dark:text-stone-400">
              Smart Student Tiffin Optimizer
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            href="/"
            className="px-3 py-1.5 rounded-lg text-sm font-medium text-stone-700 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
          >
            Find Tiffins
          </Link>
          <Link
            href="/onboard"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-stone-700 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
          >
            <UserPlus className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            <span className="hidden sm:inline">Register Mess</span>
          </Link>
          <Link
            href="/about"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-stone-700 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
          >
            <Info className="w-4 h-4 text-stone-500" />
            <span className="hidden sm:inline">How It Works</span>
          </Link>
          <a
            href="https://github.com/bleedZzzz/messmate"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-stone-900 dark:bg-stone-100 text-white dark:text-stone-900 hover:opacity-90 transition-opacity"
          >
            GitHub
          </a>
        </nav>
      </div>
    </header>
  )
}
