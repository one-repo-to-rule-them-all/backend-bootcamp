# Backend Bootcamp — Student Progress

**Student:** Rodolfo Baez Jr.
**Stack:** Python 3.13 · uv · Ruff · mypy · pytest · FastAPI · Pydantic v2
**Started:** 2026-08-19
**Working branch:** `student/active` (merge to `main` when deliverables are solid)

---

## Week 0 — Pre-Check (~15–20 hrs)

### Prerequisites validation
- [ ] Command line comfort: navigate, pipe, permissions, environment variables
- [ ] Git & GitHub: clone, branch, commit, push, PR, resolve a merge conflict
- [ ] Basic Python: variables, control flow, functions, collections, reading a stack trace
- [ ] HTTP at a hand-wave level: you type a URL, something comes back

### Deliverable
- [ ] Open a PR to the starter repo that adds a function + a passing test

### Status: Not started

---

## Phase 1 — Foundations to Your First API (Weeks 1–4)

### Week 1 — Backend Programming Foundations
- [ ] Project init with uv (Python 3.13, ruff, mypy, pytest)
- [ ] `models.py` — `Record` dataclass, `Status` enum, fully typed
- [ ] `errors.py` — `FieldbookError`, `RecordNotFoundError`, `ValidationError`
- [ ] `repository.py` — `InMemoryRecordRepository` with create/get/list/update/delete
- [ ] `mypy --strict` passes, `ruff check` clean
- [ ] All five methods work; error paths raise correctly
- [ ] No I/O anywhere in `src/` — logic is pure
- [ ] Committed with sensible messages

### Week 2 — Testing & TDD
- [ ] `conftest.py` with `repo` fixture
- [ ] Test-first for at least 3 behaviors
- [ ] All repository methods tested; error paths covered
- [ ] Owner-isolation proven by test with two owners
- [ ] Plant-a-bug drill completed (broke a method, test caught it, reverted)
- [ ] Coverage report reviewed; uncovered lines explained
- [ ] mypy + ruff clean; committed

### Week 3 — HTTP & Your First API
- [ ] FastAPI app with 5 endpoints (POST/GET/GET-one/PATCH/DELETE)
- [ ] Correct status codes (201 create, 204 delete, 404 missing)
- [ ] `RecordNotFoundError` handled centrally (exception handler)
- [ ] Owner isolation works through the API
- [ ] `TestClient` tests assert status + body
- [ ] Verified in `/docs` and with `curl`
- [ ] mypy + ruff clean; committed

### Week 4 — API Design & Validation
- [ ] Separate Create/Update/Out Pydantic schemas
- [ ] Input validation (empty title, over-length, unknown status) → 422
- [ ] Consistent error envelope across all error responses
- [ ] Pagination on `list` with defaults and hard cap
- [ ] `/openapi.json` complete; README with example requests
- [ ] Full test suite green; tagged `phase-1-complete`

---

## Phase 2 — Durable & Trustworthy (Weeks 5–7)

### Week 5 — Relational Databases & SQL
- [ ] `schema.sql` with `users` + `records` tables, FK, CHECK, index
- [ ] `RecordRepository` Protocol defined
- [ ] `PostgresRecordRepository` with parameterized SQL (zero f-strings)
- [ ] API works unchanged against Postgres; data survives restart
- [ ] EXPLAIN before/after index; write-time cost explained
- [ ] SQL challenge completed (JOIN, GROUP BY, EXPLAIN)
- [ ] mypy + ruff clean; committed

### Week 6 — Persistence Patterns & Data Access
- [ ] SQLAlchemy 2.0 ORM models matching Week 5 schema
- [ ] Alembic initial migration; diffed against hand-written DDL
- [ ] Second migration (add column) with working upgrade + downgrade
- [ ] `SQLAlchemyRecordRepository` satisfies Protocol
- [ ] N+1 reproduced (query count) and fixed (count dropped)
- [ ] Can name one query kept as raw SQL, and why
- [ ] mypy + ruff clean; committed

### Week 7 — Integration Testing & CI
- [ ] Integration tests against real ephemeral Postgres (testcontainers)
- [ ] Per-test isolation via transaction rollback
- [ ] `pytest-randomly` passes on multiple shuffles
- [ ] API integration tests through real DB
- [ ] GitHub Actions: ruff + mypy + pytest/coverage on every PR
- [ ] Coverage gate verified (dropped below threshold, build failed)
- [ ] Break-the-build drill completed
- [ ] Branch protection enabled; tagged `phase-2-complete`

---

## Phase 3 — Identity, Scale & Shape (Weeks 8–11)

### Week 8 — Authentication & Authorization
- [ ] Migration: `password_hash` + `role` column on users
- [ ] Register + login issue JWT with `sub` and `exp`
- [ ] `get_current_user` dependency protects routes; invalid/expired → 401
- [ ] Ownership derived from token; cross-owner access blocked
- [ ] Admin role can list all; regular user cannot
- [ ] Threat-model written
- [ ] Tests cover auth paths; CI green; committed

### Week 9 — Async, Queues & Background Work
- [ ] arq worker wired to Redis
- [ ] Async export: 202 Accepted + pollable status
- [ ] Outgoing webhook with HMAC signature, retries, idempotency
- [ ] Failure drills: worker death, receiver down → dead-letter
- [ ] Tests cover enqueue, job logic, webhook; CI green; committed

### Week 10 — Caching & Performance
- [ ] Baseline load test (Locust): RPS + p50/p95/p99 recorded
- [ ] Bottleneck identified from data + EXPLAIN ANALYZE
- [ ] Cache-aside with Redis, TTL, write-invalidation
- [ ] After load test: measured improvement recorded
- [ ] Test proves cache returns fresh data after update
- [ ] Failure modes documented; CI green; committed

### Week 11 — Architecture & Design
- [ ] Code reorganized: `domain/` / `services/` / `adapters/` / `api/`
- [ ] `grep` confirms domain has zero infrastructure imports
- [ ] Adapters injected via DI; service depends on ports
- [ ] Adapter swap proof (SQLAlchemy ↔ in-memory), tests pass
- [ ] Architecture diagram in README
- [ ] Full suite green; tagged `phase-3-complete`

---

## Phase 4 — Production & Proof (Weeks 12–16)

### Week 12 — Containerization & Configuration
- [ ] Multi-stage Dockerfile, slim image, non-root
- [ ] `docker compose up` starts app + Postgres + Redis
- [ ] All config from environment; `.env` gitignored
- [ ] Migrations auto-apply on startup
- [ ] Fresh-machine test: clone + compose up works
- [ ] Committed

### Week 13 — CI/CD & Deployment
- [ ] Merge to `main` triggers build → deploy automatically
- [ ] Managed Postgres + Redis; secrets injected at deploy
- [ ] Migrations in pipeline before new code serves traffic
- [ ] End-to-end deploy with zero manual steps
- [ ] Rollback drill completed
- [ ] Expand/contract migration exercise completed
- [ ] Committed

### Week 14 — Observability & Reliability
- [ ] Structured JSON logging with per-request correlation id
- [ ] `/health` reflects real dependency status
- [ ] `/metrics` exposes request rate + latency
- [ ] Traces show spans across request + DB call
- [ ] SLI/SLO defined; alert configured
- [ ] Injected failure surfaces in observability; system fails fast
- [ ] Committed

### Week 15 — Security Hardening
- [ ] Rate limiting on login + global; proven by burst test
- [ ] bandit + pip-audit in CI, gating on high severity
- [ ] Adversarial tests prove BOLA and mass-assignment blocked
- [ ] Secrets out of git; secret scanning enabled
- [ ] Security headers; HTTPS enforced
- [ ] OWASP Top 10 checklist with evidence in repo
- [ ] Committed

### Week 16 — Capstone & Career
- [ ] Capstone feature designed, built, tested, deployed
- [ ] Design doc with trade-offs
- [ ] README polished for a stranger
- [ ] "Scale to 1M users" writeup
- [ ] At least one live system-design mock
- [ ] Final defense passed
- [ ] Tagged `v1.0` — course complete

---

## Content Improvement Notes

> As you work through the bootcamp, log anything confusing, missing, or worth improving here. These feed back into the curriculum.

_No notes yet — start logging as you hit Week 0._
