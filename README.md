# Tiffin Optimizer (MessMate)

> Tell us where you live and what you eat. Four AI agents find the best mess for your area, plan your weekly menu, and work out a fair monthly price.

Tiffin Optimizer is a multi-agent AI system designed to match students and bachelors in Indian towns with nearby tiffin/mess providers, plan rotating weekly menus, and simulate subscription price negotiation between providers and demand clusters.

## Milestones Progress

- [x] **M0: Repo, tooling, CI skeleton**
- [x] **M1: Domain models, database, synthetic data**
- [x] **M2: Demand and Match agents**
- [x] **M3: LLM layer and Menu agent**
- [x] **M4: Deal agent**
- [ ] **M5: LangGraph orchestrator**
- [ ] **M6: FastAPI layer**
- [ ] **M7: Next.js frontend**
- [ ] **M8: Observability and evaluation**
- [ ] **M9: Docker, CI/CD, deployment**
- [ ] **M10: Polish and portfolio material**

## Quick Start (with `uv`)

The entire project is managed with `uv` as a unified workspace. Run directly from the repo root:

```bash
# Sync all dependencies
uv sync

# Run tests with coverage
uv run pytest

# Check code formatting & linting
uv run ruff check .
uv run ruff format --check .

# Type check
uv run mypy backend/app

# Start FastAPI server
uv run uvicorn app.main:app --reload --port 8000
```

