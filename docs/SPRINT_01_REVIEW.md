# Sprint 01 Review — Stabilization Pass

**Date:** 2026-07-26
**Scope:** `apps/api` (FastAPI backend), `apps/web` (Next.js frontend), `infrastructure/supabase` (schema), shared `packages/*`
**Type:** Analysis + remediation. The initial pass (2026-07-25) was analysis-only; all 6 High-priority findings from that pass were then implemented and verified in a follow-up stabilization pass (2026-07-26). No new product features were added.

---

## 1. What Was Implemented

### 1.1 Sprint 01 vertical slice (2026-07-25)

- **Create Project** — `POST /api/v1/projects`. Validates and persists a project (Clean Architecture: domain entity, repository interface, Postgres implementation, use case, FastAPI route).
- **Start Research Session** — `POST /api/v1/projects/{project_id}/research-sessions`. Validates the parent project exists, creates a session for a given `Marketplace` (`amazon` / `ebay` / `tiktok`) with status `pending`.
- **View Research Result** — `GET /api/v1/research-sessions/{id}/research-result`. Returns a research result for a session, generating one on first access (currently backed by hardcoded placeholder data standing in for the future Analytics/AI pipeline described in `docs/ARCHITECTURE.md`).
- **Frontend** — a single `/projects` page (Next.js App Router) exercising the full flow: create project → select marketplace → start research → view result.
- **Database** — three Supabase/Postgres migrations (`projects`, `research_sessions`, `research_results`) with FK relationships, `updated_at` triggers, and basic check constraints.
- **Local dev environment** — Supabase CLI-managed local stack (Postgres, Studio, etc.) via Docker.

### 1.2 Stabilization pass (2026-07-26)

Following the review, all 6 High-priority findings were implemented:

- **Structured logging** — added `app/core/logging.py`, a request-logging middleware, and a global `Exception` handler in `main.py` that logs unhandled errors and returns a generic 500 instead of leaking internals.
- **Research-session status lifecycle** — added `ResearchSessionRepository.update_status`; `CreateResearchResultUseCase` now transitions a session from `pending` to `completed` once its result exists. Verified live: the UI badge now reads `completed` instead of being stuck at `pending`.
- **Race-condition fix** — `PostgresResearchResultRepository.create` now uses `INSERT ... ON CONFLICT (research_session_id) DO NOTHING` with a fallback `SELECT`, so two concurrent first-time requests for the same session converge on one row instead of one of them raising an unhandled unique-violation 500.
- **List/read endpoints** — added `GET /projects`, `GET /projects/{id}`, and `GET /projects/{id}/research-sessions`, each with a dedicated use case (`ListProjectsUseCase`, `GetProjectUseCase`, `ListResearchSessionsForProjectUseCase`). The frontend now fetches projects on mount and a project's sessions on selection, so a browser refresh no longer loses visible data (the previous behavior only ever showed in-memory state from the current page load).
- **Basic API-key auth** — added `app/core/security.py` (`verify_api_key`, an `X-API-Key` header check) applied as a router-level dependency to `projects`, `research_sessions`, and `research_results` (the `/health` route stays open). The frontend sends the key via a new shared `apiFetch` client (`apps/web/src/lib/api/client.ts`), which also removed the per-file `API_URL`/error-class duplication called out in the original review.
- **Integration tests against real Postgres** — new `apps/api/tests/integration/` suite (15 tests) runs against the live local Supabase Postgres, each test wrapped in a rolled-back transaction via a single-connection pool test double, plus a dedicated two-connection concurrency test that reproduces and confirms the fix for the race condition above. Tests skip gracefully if Postgres is unreachable.

A bug was also found and fixed during manual verification of the above: the frontend never refreshed session state after fetching a result, so the status badge still showed `pending` even after the backend-side fix in the previous bullet was working correctly. `handleViewResult` now re-fetches the project's sessions after a result loads.

Both automated suites and a full manual browser walkthrough (create → list → select → research → result → status-completed → page-reload-persists) were used to verify the fixes; see Section 5.

---

## 2. Architecture Review (Post-Stabilization Status)

### 2.1 Layering — Still good, unchanged

Each backend feature continues to follow the intended Clean Architecture layering (`domain` → `application` → `infrastructure`/`presentation`), and the new query-side use cases (`ListProjectsUseCase`, `GetProjectUseCase`, `ListResearchSessionsForProjectUseCase`) were added following the same conventions as the existing `CreateXUseCase` classes. No layering regressions were introduced.

### 2.2 Cross-feature coupling — Unchanged, not addressed

`research_sessions` and `research_results` still import repository interfaces directly from other features' domain packages, and the new `ListResearchSessionsForProjectUseCase` adds one more such dependency (on `ProjectRepository`, to 404 on an unknown project). This was flagged as a Low-priority item ("address before the next engine lands," not before this stabilization pass) and was deliberately left as-is — fixing it now would have meant introducing a port/contract pattern with no second consumer yet to validate the design against. It remains the top architectural item to resolve before the Supply Engine (or any other new feature slice) is added.

### 2.3 Duplicated logic — Partially resolved

- **Frontend API client boilerplate — resolved.** All three client files now go through a shared `apiFetch` helper (`apps/web/src/lib/api/client.ts`) that owns the base URL, `Content-Type`/`X-API-Key` headers, and error handling (`ApiError`). The three bespoke per-file `Error` subclasses were removed.
- **DTO → response-model mapping boilerplate — reduced, not eliminated.** Each route module now has one `_to_response()` helper reused by its own create/list/get handlers (previously each handler repeated the mapping inline), but the three feature modules still each define their own near-identical helper. Not deduplicated across features.
- **Validation constants duplicated across languages — still open.** `MIN_NAME_LENGTH`/`MAX_NAME_LENGTH` remain independently defined in the Python use case and the Next.js page.

### 2.4 Unnecessary complexity / dead scaffolding — Unchanged, not addressed

`app/api/`, `app/shared/`, `packages/ui/`, `packages/utils/` are still empty scaffolding, untouched by this pass (out of scope for the 6 High-priority items). The dead `ResearchSessionStatus.RUNNING`/`FAILED` states are now joined by a reachable `COMPLETED`, but `RUNNING` and `FAILED` are still never set by any code path (there's still no real async pipeline to be "running" or to "fail").

---

## 3. Code Quality Review (Post-Stabilization Status)

| Area | Status |
|---|---|
| **Type safety** | Unchanged and still clean: `mypy --strict` passes across 75 source files (up from 70), `tsc --noEmit` and `eslint` clean. `demand_level`/`competition_level`/`profit_level` are still plain `str`, not enums — not addressed this pass (was Medium priority). |
| **Error handling** | **Improved.** A global `Exception` handler now catches anything not already translated to an `HTTPException`, logs it, and returns a generic `{"detail": "Internal server error"}` 500. Domain-exception → `HTTPException` translation per route is unchanged. |
| **Logging** | **Resolved.** Request/response logging middleware plus error logging via the global exception handler. Log level is configurable via `Settings.log_level` (`LOG_LEVEL` env var, defaults to `INFO`). |
| **Validation** | Unchanged. Business validation still lives correctly in the use-case layer; DB-level `CHECK` constraints for `demand_level`/`competition_level`/`profit_level` were not added (still Medium priority, still open). |
| **Naming consistency** | `CreateResearchResultUseCase` is still invoked from a `GET` route and still performs a write on first call — not renamed or restructured this pass (the fix targeted was the race condition in that write, not the verb/name mismatch itself). DTOs were renamed from `CreateXResponseDTO` to generic `XDTO` (e.g. `ProjectDTO`, `ResearchSessionDTO`) since they're now shared across create/get/list use cases — this incidentally improved naming consistency as a side effect of adding the list/read endpoints. |
| **Auth** | **New.** A single shared `X-API-Key` header, checked via a FastAPI dependency, is required on all `projects`/`research_sessions`/`research_results` routes. This is explicitly a stopgap: it's one static credential shared by every client (not per-user), and on the frontend it ships in the client bundle via `NEXT_PUBLIC_API_KEY` (documented in-code as such). It stops casual/automated access to a local or staging deployment; it is not a substitute for real authentication before any public launch. |
| **TODOs / tech debt markers** | Still none. The placeholder-pipeline comment in `create_research_result.py` is unchanged and still accurate. |

---

## 4. Current Test Status

| Suite | Before stabilization | After stabilization |
|---|---|---|
| Backend (`pytest`) | 31 passed | **61 passed** |
| — of which: real-Postgres integration tests | 0 | **15** (new `tests/integration/`, includes the race-condition regression test) |
| Backend `mypy --strict` | clean (70 files) | clean (75 files) |
| Backend `ruff check` | clean | clean |
| Frontend (`vitest`) | 8 passed | **12 passed** |
| Frontend `tsc --noEmit` | clean | clean |
| Frontend `eslint` | clean | clean |

The integration suite connects to the same local Supabase Postgres used for manual verification, wraps each test in a transaction that's rolled back afterward (via a single-connection pool test double), and skips gracefully (`pytest.skip`) if Postgres isn't reachable — so the suite doesn't hard-fail in an environment without Docker/Supabase running.

Manual verification this pass (headless browser against the live local stack, both servers running): created a project, confirmed it and prior test data appear in the list, started research, viewed the result, confirmed the status badge reads `completed`, reloaded the page and confirmed the project list and status persisted. Requests without a valid `X-API-Key` were confirmed to return 401; the health check was confirmed to remain open without a key.

---

## 5. Remaining Technical Debt

Carried over from the original review, still open (renumbered; items resolved this pass have been removed from this list):

1. Cross-feature domain coupling (`research_results` → `research_sessions` → `projects`) has no explicit port/contract boundary. Highest-priority remaining architectural item — see Section 6.
2. `demand_level`/`competition_level`/`profit_level` are free-text `str` end-to-end (domain, DTO, DB) instead of enums with matching `CHECK` constraints, inconsistent with `Marketplace`/`ResearchSessionStatus`.
3. `MIN_NAME_LENGTH`/`MAX_NAME_LENGTH` are duplicated between the Python use case and the Next.js page with no single source of truth.
4. CORS allowed origins are still hardcoded (`DEV_ALLOWED_ORIGINS` in `main.py`), not environment-driven.
5. `asyncpg` connection pool is still created lazily on first request with no lock (a cold-start race that could create/leak more than one pool); should move into the `lifespan` startup.
6. Empty scaffold packages (`app/api/`, `app/shared/`, `packages/ui/`, `packages/utils/`) are untouched — either populate or delete.
7. `README.md` is still stale (still describes the database as "not yet connected" and infra dirs as "empty scaffold").
8. Frontend root `/` route is still the unmodified `create-next-app` boilerplate page, with no link into `/projects`.
9. No pagination on the new `GET /projects` / `GET /projects/{id}/research-sessions` list endpoints. Not a problem at current data volumes, but was a known gap even before these endpoints existed and is now live rather than hypothetical.
10. `ResearchSessionStatus.RUNNING` and `.FAILED` are still unreachable — no code path sets them, since there's still no real async pipeline that could be "running" or could "fail." Only `PENDING`→`COMPLETED` is wired up.
11. Frontend API responses are still consumed via blind type assertions (`apiFetch<T>`) with no runtime schema validation (e.g. zod) — a backend contract change would fail confusingly at render time rather than at the fetch boundary.
12. `apps/web/src/app/projects/page.tsx` has grown substantially with this pass's rehydration work (project list + selection + sessions + results all in one component with ~10 pieces of `useState`); worth extracting into smaller hooks/components before more UI is added on top of it.

New, introduced by this pass:

13. The API key is a single shared credential for all clients, embedded client-side via `NEXT_PUBLIC_API_KEY`. This was an explicit, documented tradeoff (see Section 3) to close the "no auth at all" gap quickly — it must be replaced with real per-user authentication before any public deployment, not extended or relied on longer-term.

---

## 6. Recommended Priorities for Sprint 02

| # | Recommendation | Priority |
|---|---|---|
| 1 | Replace the shared static API key with real per-user/per-tenant authentication before any environment beyond local/staging is stood up | **High** |
| 2 | Define an explicit contract/port pattern for cross-feature domain dependencies before adding the next engine (Supply Engine, per `ARCHITECTURE.md`) — the coupling only gets more expensive to unwind the longer it's deferred | **High** |
| 3 | Add pagination to `GET /projects` and `GET /projects/{id}/research-sessions` before real usage grows | Medium |
| 4 | Make CORS allowed origins environment-driven via `Settings` | Medium |
| 5 | Promote `demand_level`/`competition_level`/`profit_level` to enums with matching DB check constraints | Medium |
| 6 | Single-source the name-length validation constants between backend and frontend | Medium |
| 7 | Initialize the asyncpg pool once in the FastAPI `lifespan` startup instead of lazily per-request | Medium |
| 8 | Add runtime response validation (e.g. zod) on the frontend instead of blind type assertions | Medium |
| 9 | Extract `apps/web/src/app/projects/page.tsx` into smaller hooks/components before adding more UI to it | Medium |
| 10 | Resolve or remove the empty `app/api/`, `app/shared/`, `packages/ui/`, `packages/utils/` scaffolding | Low |
| 11 | Update `README.md` to reflect the current state of the database/infra setup | Low |
| 12 | Replace the default Next.js starter homepage with a real landing page or redirect to `/projects` | Low |
| 13 | Decide whether `ResearchSessionStatus.RUNNING`/`.FAILED` are needed before the real pipeline exists, or drop them until they are | Low |

---

## 7. Summary

All 6 High-priority findings from the initial review are resolved and verified: structured logging, the research-session status bug, the research-result race condition, the missing list/read endpoints (with frontend rehydration), basic API-key auth, and a real-Postgres integration test suite. Test coverage grew from 39 to 73 passing tests across both apps, with no regressions in type checking or linting. One additional bug (stale status badge on the frontend) was found and fixed during verification of this work.

The architecture itself is unchanged and remains sound — this pass was deliberately scoped to stabilization, not refactoring, so the known cross-feature coupling and scaffold debt were left in place rather than opportunistically reworked. Sprint 02 should treat replacing the shared API key and resolving the cross-feature coupling as the two highest-priority items, since both get more expensive the longer new features are built on top of them.
