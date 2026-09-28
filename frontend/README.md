# MessMate — Next.js 16 Frontend

Modern, accessible, mobile-first frontend for the **MessMate** multi-agent student tiffin optimization platform.

Built with **Next.js 16 (App Router)**, **Tailwind CSS v4**, **21st UI** design system tokens, **TanStack React Query v5**, and **Zod** schema validations.

---

## Features

- **Search & Filter (`/`)**: Locality selection, dietary toggle (`veg`, `non_veg`, `egg`), monthly budget ceiling slider, and multi-cuisine selector.
- **Optimization Results (`/results`)**: Ranked list of verified tiffin providers with match score percentage badge, top factor reasons, list price, and embedded **AgentTracePanel**.
- **Provider Detail (`/provider/[id]`)**: 7×2 weekly meal rotation grid (lunches & dinners) with AI/deterministic badges, interactive price negotiation timeline, and direct WhatsApp contact link.
- **Provider Onboarding (`/onboard`)**: Registration form with Zod validation, cuisine and diet selectors, and mandatory terms consent.
- **About Multi-Agent AI (`/about`)**: Complete breakdown of the 4 autonomous LangGraph agents (Demand, Match, Menu, Deal), interactive pipeline diagram, and architecture overview.
- **Agent Trace Observability (`AgentTracePanel`)**: Transparent visibility into agent latency, LLM vs. deterministic fallback paths, and pipeline errors.
- **Mandatory Pricing Disclaimer**: Distinct callouts indicating negotiated rates are algorithmic suggestions, not commercial offers.

---

## Getting Started

### Prerequisites
- Node.js 18+ (tested on Node 22+)
- Running MessMate FastAPI backend at `http://localhost:8000` (or configured via `NEXT_PUBLIC_API_URL`)

### Development Server

```bash
# In /frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Running with Backend

In terminal 1 (Backend):
```bash
# In root directory
uv run uvicorn backend.app.main:app --reload --port 8000
```

In terminal 2 (Frontend):
```bash
# In /frontend directory
npm run dev
```

---

## Testing & Quality

```bash
# Run unit & schema tests (Vitest)
npm test

# Run TypeScript typecheck
npx tsc --noEmit

# Run ESLint
npm run lint

# Run production build verification
npm run build

# Run Playwright E2E smoke tests
npx playwright test
```
