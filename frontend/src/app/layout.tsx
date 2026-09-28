import type { Metadata } from "next"
import { ReactNode } from "react"
import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Providers } from "@/components/providers"
import "./globals.css"

export const metadata: Metadata = {
  title: "MessMate — AI Tiffin & Mess Optimizer for Students",
  description:
    "Multi-agent AI platform matching student clusters with local tiffin providers, balancing weekly rotating menus and simulating subscription negotiations.",
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#fdfbf7] dark:bg-[#0c0a09] text-stone-900 dark:text-stone-100 font-sans selection:bg-orange-500/20 selection:text-orange-900 dark:selection:text-orange-200">
        <Providers>
          <Navbar />
          <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  )
}
