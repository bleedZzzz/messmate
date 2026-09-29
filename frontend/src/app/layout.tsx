import type { Metadata } from "next"
import { ReactNode } from "react"
import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Providers } from "@/components/providers"
import "./globals.css"

export const metadata: Metadata = {
  title: "MessMate — Autonomous Multi-Agent Tiffin Intelligence",
  description:
    "Next-generation 4-Agent LangGraph swarm matching student clusters with local messes, constraint-validated 7-day rotating menus, and simulated volume negotiations.",
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#08090c] text-neutral-100 font-sans selection:bg-amber-500/25 selection:text-amber-200 relative overflow-x-hidden">
        {/* Background Ambient Glows */}
        <div className="fixed inset-0 pointer-events-none z-0">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[450px] bg-gradient-to-b from-amber-500/10 via-orange-600/5 to-transparent blur-[120px] opacity-75" />
          <div className="absolute top-1/3 -left-48 w-[600px] h-[400px] bg-violet-600/5 blur-[100px]" />
          <div className="absolute bottom-10 -right-48 w-[600px] h-[400px] bg-emerald-600/5 blur-[100px]" />
        </div>

        <Providers>
          <div className="relative z-10 flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8">{children}</main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  )
}
