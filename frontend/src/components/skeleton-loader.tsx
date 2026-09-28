export function SkeletonLoader({ count = 3 }: { count?: number }) {
  return (
    <div className="flex flex-col gap-4 w-full">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="p-5 rounded-2xl border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 animate-pulse flex flex-col sm:flex-row gap-4 justify-between"
        >
          <div className="flex gap-4 items-start w-full">
            <div className="w-14 h-14 rounded-2xl bg-stone-200 dark:bg-stone-800 shrink-0" />
            <div className="flex flex-col gap-2 w-full max-w-md">
              <div className="h-5 bg-stone-200 dark:bg-stone-800 rounded-md w-3/4" />
              <div className="h-3 bg-stone-200 dark:bg-stone-800 rounded-md w-1/2" />
              <div className="h-6 bg-stone-200 dark:bg-stone-800 rounded-md w-5/6" />
            </div>
          </div>
          <div className="flex sm:flex-col justify-between sm:justify-center items-end gap-2 shrink-0">
            <div className="h-6 bg-stone-200 dark:bg-stone-800 rounded-md w-24" />
            <div className="h-9 bg-stone-200 dark:bg-stone-800 rounded-xl w-32" />
          </div>
        </div>
      ))}
    </div>
  )
}
