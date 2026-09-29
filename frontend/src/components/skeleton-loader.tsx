export function SkeletonLoader({ count = 3 }: { count?: number }) {
  return (
    <div className="flex flex-col gap-4 w-full">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="p-6 rounded-3xl cyber-panel border border-white/[0.08] animate-pulse flex flex-col lg:flex-row gap-5 justify-between items-start lg:items-center"
        >
          <div className="flex gap-4 items-start w-full">
            <div className="w-16 h-16 rounded-2xl bg-white/[0.06] shrink-0" />
            <div className="flex flex-col gap-2.5 w-full max-w-lg">
              <div className="h-5 bg-white/[0.08] rounded-lg w-2/3" />
              <div className="h-3.5 bg-white/[0.04] rounded-lg w-1/3" />
              <div className="h-8 bg-white/[0.04] rounded-xl w-5/6" />
            </div>
          </div>
          <div className="flex lg:flex-col justify-between lg:justify-center items-end gap-3 shrink-0 w-full lg:w-auto pt-3 lg:pt-0 border-t lg:border-t-0 border-white/[0.06]">
            <div className="h-6 bg-white/[0.06] rounded-lg w-28" />
            <div className="h-10 bg-amber-500/20 rounded-xl w-36" />
          </div>
        </div>
      ))}
    </div>
  )
}
