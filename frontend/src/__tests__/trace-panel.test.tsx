import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { AgentTracePanel } from "@/components/trace-panel"
import { TraceStep } from "@/lib/schemas"

describe("AgentTracePanel Component", () => {
  const sampleTrace: TraceStep[] = [
    {
      agent: "demand",
      started_ms: 1000,
      duration_ms: 45,
      used_llm: false,
      fallback_used: false,
    },
    {
      agent: "match",
      started_ms: 1045,
      duration_ms: 60,
      used_llm: false,
      fallback_used: false,
    },
    {
      agent: "menu",
      started_ms: 1105,
      duration_ms: 850,
      used_llm: true,
      fallback_used: false,
    },
    {
      agent: "deal",
      started_ms: 1955,
      duration_ms: 120,
      used_llm: false,
      fallback_used: true,
    },
  ]

  it("renders nothing when trace is empty", () => {
    const { container } = render(<AgentTracePanel trace={[]} />)
    expect(container.firstChild).toBeNull()
  })

  it("renders trace summary with total duration and step count", () => {
    render(<AgentTracePanel trace={sampleTrace} />)

    expect(screen.getByText(/LangGraph Agent Observability Trace/i)).toBeInTheDocument()
    // Total duration: 45 + 60 + 850 + 120 = 1075ms
    expect(screen.getByText(/4 steps · 1075ms total/i)).toBeInTheDocument()
  })

  it("renders agent cards with proper agent names", () => {
    render(<AgentTracePanel trace={sampleTrace} />)

    expect(screen.getByText(/1\. Demand Agent/i)).toBeInTheDocument()
    expect(screen.getByText(/2\. Match Agent/i)).toBeInTheDocument()
    expect(screen.getByText(/3\. Menu Agent/i)).toBeInTheDocument()
    expect(screen.getByText(/4\. Deal Agent/i)).toBeInTheDocument()
  })

  it("displays LLM, Fallback, and Deterministic badges correctly", () => {
    render(<AgentTracePanel trace={sampleTrace} />)

    // Should have 1 LLM badge (menu)
    const llmBadges = screen.getAllByTestId("badge-llm")
    expect(llmBadges.length).toBe(1)
    expect(llmBadges[0]).toHaveTextContent(/LLM/i)

    // Should have 1 Fallback badge (deal)
    const fallbackBadges = screen.getAllByTestId("badge-fallback")
    expect(fallbackBadges.length).toBe(1)
    expect(fallbackBadges[0]).toHaveTextContent(/Fallback/i)

    // Should have 2 Deterministic badges (demand, match)
    const deterministicBadges = screen.getAllByTestId("badge-deterministic")
    expect(deterministicBadges.length).toBe(2)
  })

  it("renders step-level errors and pipeline error alerts", () => {
    const errorTrace: TraceStep[] = [
      {
        agent: "menu",
        started_ms: 1000,
        duration_ms: 500,
        used_llm: false,
        fallback_used: true,
        error: "LLM timeout after 3 retries",
      },
    ]

    render(
      <AgentTracePanel
        trace={errorTrace}
        errors={["Menu fallback used due to provider downtime"]}
      />
    )

    expect(screen.getByText(/LLM timeout after 3 retries/i)).toBeInTheDocument()
    expect(
      screen.getByText(/Pipeline Partial Failure Warning:/i)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Menu fallback used due to provider downtime/i)
    ).toBeInTheDocument()
  })

  it("allows toggling expand and collapse of the trace panel", () => {
    render(<AgentTracePanel trace={sampleTrace} />)

    // Initially expanded
    expect(screen.getByText(/1\. Demand Agent/i)).toBeInTheDocument()

    // Click header to collapse
    const toggleButton = screen.getByRole("button", { name: /LangGraph Agent Observability Trace/i })
    fireEvent.click(toggleButton)

    // Details should now be hidden
    expect(screen.queryByText(/1\. Demand Agent/i)).not.toBeInTheDocument()

    // Click again to expand
    fireEvent.click(toggleButton)
    expect(screen.getByText(/1\. Demand Agent/i)).toBeInTheDocument()
  })
})
