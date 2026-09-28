# Architecture & Design Decisions

| ID | Date | Decision | Rationale |
|---|---|---|---|
| DEC-001 | 2026-09-28 | Use `uv` for Python tooling & environment | Faster virtual environment creation, deterministic resolution, and built-in Python management. Python 3.12 pinned. |
| DEC-002 | 2026-09-28 | SQLite default locally, Neon/Supabase Postgres in production | Satisfies zero-configuration local runs while remaining fully compatible with remote Postgres in production. |
| DEC-003 | 2026-09-28 | Root-level `uv` workspace & local doc ignore | Root `pyproject.toml` defines a `uv` workspace member `backend` allowing root-level tool invocation. `PRD.md`, `ARCHITECTURE.md`, `PROMPTS.md` gitignored from remote repo. |

