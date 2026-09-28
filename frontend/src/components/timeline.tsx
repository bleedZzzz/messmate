import * as React from "react"
import { cn } from "@/lib/utils"

export type TimelineProps = React.HTMLAttributes<HTMLOListElement>

export const Timeline = React.forwardRef<HTMLOListElement, TimelineProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <ol
        ref={ref}
        className={cn("relative border-l border-stone-200 dark:border-stone-800 ml-3.5 space-y-6", className)}
        {...props}
      >
        {children}
      </ol>
    )
  }
)
Timeline.displayName = "Timeline"

export type TimelineItemProps = React.LiHTMLAttributes<HTMLLIElement>

export const TimelineItem = React.forwardRef<HTMLLIElement, TimelineItemProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <li ref={ref} className={cn("relative pl-6 group", className)} {...props}>
        {children}
      </li>
    )
  }
)
TimelineItem.displayName = "TimelineItem"

export interface TimelinePointProps extends React.HTMLAttributes<HTMLDivElement> {
  active?: boolean
}

export const TimelinePoint = React.forwardRef<HTMLDivElement, TimelinePointProps>(
  ({ active = false, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "absolute -left-[1.3125rem] top-1.5 flex h-6 w-6 items-center justify-center rounded-full border-2 bg-white dark:bg-stone-900 transition-colors",
          active
            ? "border-orange-600 dark:border-orange-500 text-orange-600"
            : "border-stone-300 dark:border-stone-700 text-stone-500",
          className
        )}
        {...props}
      />
    )
  }
)
TimelinePoint.displayName = "TimelinePoint"

export type TimelineContentProps = React.HTMLAttributes<HTMLDivElement>

export const TimelineContent = React.forwardRef<HTMLDivElement, TimelineContentProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("flex flex-col gap-1", className)} {...props}>
        {children}
      </div>
    )
  }
)
TimelineContent.displayName = "TimelineContent"
