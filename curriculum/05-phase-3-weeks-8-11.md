# Backend Bootcamp — Phase 3: Identity, Scale & Shape
## Weeks 8–11 · Detailed Lesson Plans

Same rhythm: **Objectives → Setup → Read → Understand → Build → Done when.** Read before you build; build by writing code; a week is done only when every box checks.

**Where you left off:** Fieldbook is a durable, migration-managed, CI-gated API — but it still trusts a raw `owner_id` query param, does all its work inside the request, hits the database on every read, and mixes concerns across its modules. This phase fixes all four.

**Stack added this phase:** `argon2-cffi`, `pyjwt`, Redis, `arq`, Locust.
**Weekly load:** ~20–25 hrs. You'll keep Docker running Postgres and add Redis.

---

# Week 8 — Authentication & Authorization

**Goal:** Real users prove who they are and get access scoped to what they own. Retire the `owner_id` query-param placeholder for good.

### Objectives
- Store passwords safely (argon2) and never in plaintext
- Issue and validate JWTs, and gate endpoints behind an authenticated-user dependency
- Enforce ownership and role-based access (regular user vs admin)
- Threat-model the auth flow and name its known gaps

### Setup
```bash
uv add "pyjwt" "argon2-cffi"
```
Add a `JWT_SECRET` to your environment config (via `pydantic-settings` from Week 4's habits) — never hardcode it.

### Read (~5 hrs)
- **FastAPI Security tutorial** (fastapi.tiangolo.com → "Security") — "OAuth2 with Password (and hashing, Bearer with JWT tokens)" and "Get Current User." *Focus on:* `OAuth2PasswordBearer`, the login flow, and using a dependency to inject the current user into routes.
- **OWASP Password Storage Cheat Sheet** (cheatsheetseries.owasp.org). *Focus on:* why argon2/bcrypt with per-password salts, and what a "work factor" is.
- **JWT intro** (jwt.io/introduction). *Focus on:* the header.payload.signature structure, that JWTs are *signed, not encrypted* (don't put secrets in the payload), and the `exp` claim.
- **Sessions vs tokens** — search "session vs JWT authentication." *Focus on:* the core trade-off — server sessions are revocable but stateful; JWTs are stateless but hard to revoke before expiry.

### Understand
- **authn ≠ authz:** authentication proves *who you are* (login); authorization decides *what you may do* (ownership, roles). Two separate concerns, often conflated.
- **Password hashing:** you store an argon2 hash, never the password. Salting defeats rainbow tables; the work factor makes brute force expensive. If your DB leaks, hashes buy your users time.
- **JWT reality:** the signature proves the token wasn't tampered with; anyone can *read* the payload. `exp` limits how long a stolen token is useful — which matters because a plain JWT can't be revoked mid-life. Know this gap; you're choosing it deliberately.
- **RBAC & least privilege:** a `user` sees only their own records; an `admin` can see all. Default to the *least* access that works.

### Build — auth + ownership (~13 hrs)
1. **Migration:** add `password_hash` and a `role` column (enum `user`/`admin`, default `user`) to `users`. Upgrade + downgrade both work.
2. **Register:** `POST /auth/register` — hash the password with argon2, create the user.
3. **Login:** `POST /auth/token` using `OAuth2PasswordRequestForm` — verify the password against the hash, and on success issue a signed JWT with `sub = user_id` and an `exp`.
4. **Current-user dependency:** `get_current_user` reads the `Authorization: Bearer` token, validates the signature and expiry, loads the user, and raises **401** on missing/invalid/expired tokens.
5. **Retire the placeholder:** every `/records` endpoint now derives the owner from `get_current_user`, not a query param. `list` returns the caller's records; `get`/`update`/`delete` on a record the caller doesn't own return **404** (don't leak existence) — decide and document 403-vs-404 and be consistent.
6. **Roles:** a `require_role("admin")` dependency; admins can list all records.
7. **Threat-model (write it in the README):** what's the blast radius if a token leaks? How does `exp` limit it? What would proper revocation (refresh tokens + a denylist) require? You're documenting the gap, not necessarily closing it this week.

### Done when
- [ ] Passwords stored as argon2 hashes via a reversible migration; `role` column added
- [ ] Register + login issue a working JWT; the token carries `sub` and `exp`
- [ ] `get_current_user` protects record routes; missing/invalid/expired → 401
- [ ] Ownership derived from the token; cross-owner access blocked consistently
- [ ] Admin role can list all records; a regular user cannot
- [ ] Tests cover valid/invalid/expired tokens and ownership enforcement
- [ ] Threat-model note written; CI green; committed

---

# Week 9 — Async, Queues & Background Work

**Goal:** Move slow work off the request path, and integrate with other systems via webhooks that survive failure.

### Objectives
- Run work in a background worker instead of blocking the HTTP response
- Use the 202-Accepted + status-polling pattern for async operations
- Send outgoing webhooks with signing, retries, and idempotency
- Reason about what happens when workers or receivers fail

### Setup
```bash
docker run --name fieldbook-redis -p 6379:6379 -d redis:7
uv add arq redis
```
You'll use **arq** (async-native, pairs cleanly with FastAPI) as the queue. Celery is the one you'll meet in industry — you'll take a conceptual tour of it, not build on it.

### Read (~5 hrs)
- **arq docs** (arq-docs.helpmanual.io) — "Getting started" + defining and enqueuing tasks. *Focus on:* writing an async task, enqueuing it from your API, and running the worker process.
- **Why background jobs** — search "background jobs in web applications." *Focus on:* why slow work (report generation, external API calls, email) must not block the request/response cycle.
- **Webhook design** — search "webhooks best practices" and "HMAC webhook signature." *Focus on:* signing payloads so receivers can verify authenticity, retries with backoff, idempotency keys, and handling a receiver that's temporarily down.
- **Skim Celery's intro docs** (docs.celeryq.dev) — *Focus on:* the broker → worker → task mapping so you recognize it in the wild; note how it maps to arq's concepts.

### Understand
- **Keep the request fast:** anything slow or failure-prone that the caller doesn't need synchronously gets enqueued; the endpoint returns immediately.
- **Producer/consumer:** the API enqueues a job; a separate worker process consumes and runs it. They scale independently.
- **Idempotency is mandatory:** queues and webhooks are *at-least-once* — a job or delivery can run twice (retries, redeliveries). Design so double-execution is harmless (dedupe on an event id).
- **Failure has a shape:** transient failures retry with exponential backoff; permanently-failing messages go to a dead-letter queue instead of retrying forever.
- **Eventual consistency:** a webhook or notification lands *after* the write it describes. Consumers must tolerate that lag.

### Build — jobs + webhooks (~13 hrs)
1. **Worker:** wire up an arq worker against Redis.
2. **Async operation:** add an export/report job — `POST /records/export` enqueues the work and returns **202 Accepted** with a job id (not 200 with a blocked wait). Add `GET /records/export/{id}` to poll status/result.
3. **Outgoing webhook:** when a record transitions to `done`, enqueue a webhook delivery to a configured URL, with an **HMAC signature** header the receiver can verify, an event id for idempotency, and **retry-with-backoff** on failure.
4. **Prove the loop:** build a tiny receiver (a second small FastAPI app or script) that verifies the signature and 200s — and one that returns 500 so you can watch retries fire, then dead-letter.
5. **Failure drills:** kill the worker mid-job and observe; point the webhook at the failing receiver and confirm retries → dead-letter rather than infinite loop or lost event.

### Done when
- [ ] A slow operation runs in the background worker, not inline
- [ ] The async endpoint returns 202 + a pollable status handle
- [ ] Outgoing webhook fires on the trigger, HMAC-signed, retried with backoff
- [ ] Delivery is idempotent (event id) and survives a temporarily-down receiver
- [ ] You can explain what happens when a worker dies mid-job
- [ ] Tests cover enqueue, job logic, and webhook signing/retry; CI green; committed

---

# Week 10 — Caching & Performance

**Goal:** Make it fast *on purpose*, and prove the win with numbers. No measurement, no credit.

### Objectives
- Load-test the API and read latency percentiles, not just averages
- Find a real bottleneck with data (and `EXPLAIN ANALYZE`), not a guess
- Add cache-aside caching with a TTL and correct invalidation
- Quantify the before/after improvement

### Setup
```bash
uv add --dev locust
```
(Redis is already running from Week 9 — you'll reuse it as the cache.)

### Read (~4.5 hrs)
- **Caching strategies** — search "cache-aside pattern." *Focus on:* lazy (cache-aside) loading, TTLs, and the two genuinely hard problems — invalidation and key naming.
- **Redis as a cache** (redis.io docs / `redis-py`). *Focus on:* `SET` with an expiry (`EX`), `GET`, and treating Redis as a fast look-aside store.
- **Locust** (docs.locust.io) — quickstart. *Focus on:* writing a `locustfile` with user tasks, running headless, and reading RPS and p50/p95/p99.
- **Postgres `EXPLAIN ANALYZE`** — search "reading EXPLAIN ANALYZE." *Focus on:* spotting a sequential scan vs an index scan and how an index changes the plan (ties back to Week 5).
- **Skim:** latency vs throughput and why tail latency (p95/p99) matters more than the average.

### Understand
- **Measure first:** you profile/load-test to find the *actual* bottleneck before changing anything. Optimizing by intuition is how you speed up code that was never slow.
- **Where to cache:** in-process (`functools.lru_cache`), distributed (Redis), or HTTP/CDN — each with trade-offs in freshness, sharing, and scope.
- **Cache-aside + TTL:** on read, check cache → miss → load from DB → populate cache with a TTL. Simple and robust.
- **Invalidation is the hard part:** a cached read goes stale the moment the underlying record changes. You invalidate the key on writes — and you should be able to name a race where even that goes wrong.
- **Percentiles over averages:** an average hides the slow tail your users actually feel. p95/p99 is the number that matters.

### Build — measured optimization (~13 hrs)
1. **Baseline:** write a `locustfile` exercising your hot read paths (list, get). Run it and **record baseline RPS and p50/p95/p99. This is your BEFORE.**
2. **Diagnose:** identify a bottleneck from the load data; run `EXPLAIN ANALYZE` on the query behind the hottest endpoint and read the plan.
3. **Cache:** add cache-aside caching to a hot read path with Redis and a TTL. **Invalidate the key on update/delete** of that record.
4. **Prove it:** re-run Locust and **record the AFTER numbers.** State the improvement explicitly.
5. **Correctness test:** write a test proving a cached read returns *fresh* data after an update — i.e., invalidation actually fires.
6. **Know the failure modes (write them down):** stale read under a race, thundering herd when a hot key expires, unbounded key growth. Name your mitigation or accept the risk explicitly.

### Done when
- [ ] Baseline load test captured (RPS + p50/p95/p99) *before* any change
- [ ] A bottleneck identified from data and `EXPLAIN ANALYZE`
- [ ] Cache-aside caching added with a TTL and explicit write-invalidation
- [ ] After load test shows a measured improvement — both numbers recorded
- [ ] A test proves the cache returns fresh data after an update
- [ ] You can name one way your invalidation strategy still breaks
- [ ] CI green; committed

---

# Week 11 — Architecture & Design

**Goal:** Refactor into a clean hexagonal (ports-and-adapters) architecture. This is a *refactor, not a rewrite* — the `RecordRepository` Protocol from Week 5 already did the hardest part.

### Objectives
- Separate domain, application service, and adapter layers cleanly
- Get the domain layer to zero framework/DB/cache imports
- Wire adapters via dependency injection against ports (Protocols)
- Prove the seams by swapping an adapter with no change to core code

### Read (~5 hrs)
- **Cosmic Python — *Architecture Patterns with Python*** (cosmicpython.com, free online) — the Repository, Service Layer, and Dependency Inversion chapters. *Focus on:* a domain model with no infrastructure imports, the repository as a port, and a service layer that orchestrates. **This book is the week.**
- **Hexagonal architecture** — search "hexagonal architecture ports and adapters." *Focus on:* domain at the center, adapters (DB, HTTP, cache, webhooks) at the edges, ports (interfaces) between them, and the dependency arrow pointing *inward*.
- **SOLID, applied** — search "SOLID principles Python." *Focus on:* Single Responsibility and Dependency Inversion specifically — the latter is what your Protocol already embodies.
- **Monolith vs microservices** — search "monolith first." *Focus on:* why premature service-splitting usually backfires, and coupling vs cohesion.

### Understand
- **The arrow points inward:** the domain defines the `RecordRepository` port; the SQLAlchemy *adapter* implements it. The domain never imports SQLAlchemy, FastAPI, or Redis — infrastructure depends on the domain, not the reverse.
- **Why you already did the hard part:** dependency inversion is exactly what the Week 5 Protocol gave you. This week is mostly *relocating* code into honest layers so that inversion is visible and enforced.
- **Testability is the dividend:** a domain with no I/O imports is trivially unit-testable — which is why Weeks 1–2 felt so clean. This week makes that structural, not incidental.
- **Monolith first:** one well-layered deployable beats a distributed mess. Services are an answer to organizational and scaling pressure you don't have yet.

### Build — the refactor (~12 hrs)
1. **Reorganize into layers:**
   - `domain/` — models, business rules, and ports (the `RecordRepository` Protocol, a cache port, a webhook-sender port). **No framework/DB/Redis imports.**
   - `adapters/` — concrete implementations: the SQLAlchemy repository, the Redis cache, the webhook sender.
   - `services/` — an application service (e.g. `RecordService`) that orchestrates domain logic through the ports.
   - `api/` — thin FastAPI routes that call the service.
2. **Purge infrastructure from the core:** move code until `grep -r "sqlalchemy\|fastapi\|redis" domain/` returns nothing. That grep is your acceptance test.
3. **Inject adapters:** use FastAPI `Depends` to construct concrete adapters and hand them to the service. The service depends on *ports*, never concretions.
4. **Swap-an-adapter proof:** in a test config, swap the SQLAlchemy repository for the Week 1 in-memory one — and run the service tests unchanged. They pass. That's the seam working. (Do the same by swapping the real webhook sender for a fake in tests.)
5. **Diagram it:** add a simple architecture diagram to the README — core, ports, adapters, and the inward-pointing arrows.

### Done when
- [ ] Code is organized into `domain` / `services` / `adapters` / `api`
- [ ] `grep` confirms the domain layer imports zero infrastructure
- [ ] Adapters are injected, not hard-wired; the service depends on ports
- [ ] Storage adapter swaps (SQLAlchemy ↔ in-memory) with no change to service/domain code, tests still green
- [ ] Architecture diagram in the README
- [ ] Full suite green; mypy + ruff clean; committed and tagged `phase-3-complete`

---

## End of Phase 3 — where you stand

Fieldbook now has **identity** (real auth + role-based authorization), does **async work** (background jobs, resilient webhooks), is **fast on evidence** (measured caching wins), and has a **clean, swappable architecture** where the domain doesn't know or care what database or web framework it runs on. This is the point where the codebase stops looking like a course exercise and starts looking like something a team could own.

**Phase 4 (Weeks 12–16)** is the production/ops phase: containerize it, ship it through a real CI/CD pipeline, make it observable (logs, metrics, traces, alerts), harden it against the OWASP Top 10, and finish with a capstone extension plus system-design and interview prep. That's the phase that makes it *deployable* and makes *you* interviewable.

### Habits reinforced this phase
- Least privilege by default; identity comes from verified tokens, never client-supplied params.
- Slow or failure-prone work goes to a queue; everything that can retry must be idempotent.
- Never optimize without a before-and-after measurement.
- Infrastructure depends on the domain, not the reverse — and the grep proves it.
