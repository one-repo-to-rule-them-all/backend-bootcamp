# Backend Engineering Bootcamp — Curriculum

**Format:** 16 weeks · ~20–25 hrs/week · language-agnostic (concepts first, one implementation language chosen per cohort)
**Audience:** Learners who can already write basic code in *some* language and want to become employable backend engineers.
**Design principle:** One real service, built incrementally across all 16 weeks. Every module adds a layer to the *same* codebase. Students graduate with a production-shaped system in their portfolio — not 30 disconnected toy exercises.

---

## How to teach this

A few decisions baked into the structure. If you adapt it, keep these or you lose the point:

- **Language-agnostic ≠ language-free.** Pick *one* implementation language per cohort (Python, Node/TS, Go, etc.) and teach every concept in it. The curriculum names concepts; the cohort supplies the syntax. Labs are written as capability requirements ("add token-based auth"), not framework tutorials, so the same curriculum runs in any stack.
- **The spine project is non-negotiable.** Resist the urge to let students each build something different early on. A shared, spec'd project means you can give shared assessments, students can help each other, and the difficulty curve is controlled. Let them diverge only at the capstone.
- **Testing and CI are taught early and reinforced every week, not bolted on at the end.** A student who learns to ship without tests will fight that habit forever. From Week 3 onward, *no lab is "done" until it has tests and passes CI.*
- **Assess by defending, not completing.** For each module, the student demos their work and answers "why did you do it this way, and what breaks if load 100x's?" A passing grade requires explaining trade-offs, not just green checkmarks.

---

## Prerequisites (Week 0 pre-work, ~15–20 hrs)

Gate the cohort on these so Week 1 isn't remedial:

- Command line comfort: navigate, pipe, permissions, environment variables
- Git & GitHub: clone, branch, commit, push, pull request, resolve a merge conflict
- Basic programming in the cohort language: variables, control flow, functions, collections, reading a stack trace
- HTTP at a hand-wave level: you type a URL, something comes back

**Pre-work deliverable:** Open a PR to a starter repo that adds a function + a passing test. This confirms Git, the language, and the toolchain all work before Day 1.

---

## The spine project

**"Fieldbook" — a multi-user task/records API.** Deliberately boring domain so cognitive load goes to *engineering*, not business rules. It grows as follows:

| Weeks | What the project becomes |
|---|---|
| 1–2 | A running program with clean modules and tests |
| 3–4 | An HTTP API serving JSON over REST |
| 5–6 | Backed by a real relational database with migrations |
| 7 | Fully tested (unit + integration) and running in CI |
| 8 | Authenticated and authorized (users, roles) |
| 9 | Background jobs + webhooks |
| 10 | Cached, with measured performance wins |
| 11 | Cleanly architected (layered/hexagonal), refactored |
| 12 | Containerized, 12-factor config |
| 13 | Deployed via a CI/CD pipeline |
| 14 | Observable: logs, metrics, health checks, error tracking |
| 15 | Hardened: OWASP pass, rate limiting, secrets management |
| 16 | Capstone extension of the student's own design |

---

## Modules

Each module lists: **Objectives** · **Topics** · **Lab** (adds to the spine) · **Assessment**.

### Week 1 — Backend programming foundations
**Objectives:** Write clean, modular, testable code; reason about data structures and complexity at a working level.
**Topics:** Functions & modules, separation of concerns, core data structures (arrays/lists, maps/dicts, sets), Big-O intuition (not academic — "why this loop is slow"), error handling as control flow, reading/writing files.
**Lab:** Build Fieldbook's core domain logic (create/list/update/delete records) as a pure in-memory library — no HTTP yet. Organized into modules.
**Assessment:** Code review. Is logic separated from I/O? Are errors handled deliberately, not swallowed?

### Week 2 — Testing fundamentals & TDD
**Objectives:** Write meaningful tests; understand the test pyramid; use tests to drive design.
**Topics:** Unit vs integration vs e2e, the test pyramid and why it's shaped that way, arrange-act-assert, fixtures & mocks/stubs (and when *not* to mock), test-driven development loop, coverage as a signal not a target.
**Lab:** Retrofit Week 1's domain library with a full unit test suite via TDD. Introduce one intentional bug and prove the suite catches it.
**Assessment:** Defend the test suite. Which tests are load-bearing? Where would mocking give false confidence?

### Week 3 — HTTP & the web's contract
**Objectives:** Explain precisely what happens between client and server; design URLs and status codes correctly.
**Topics:** Request/response anatomy, methods (GET/POST/PUT/PATCH/DELETE and their semantics), status codes and *choosing the right one*, headers, content negotiation, statelessness, idempotency & safety, REST as a set of constraints (not "any JSON API").
**Lab:** Wrap the domain library in an HTTP layer. Fieldbook is now a REST API serving JSON. Correct methods and status codes required.
**Assessment:** API review against REST semantics. Is `DELETE` idempotent? Does a bad request return 400 vs 500 correctly?

### Week 4 — API design & validation
**Objectives:** Design an API a stranger could consume without asking you questions.
**Topics:** Resource modeling, request validation & sanitization, error response shape (consistent, machine-readable), pagination, filtering, sorting, API versioning strategies, OpenAPI/spec-first thinking, documentation as a deliverable.
**Lab:** Add validation, consistent error envelopes, pagination, and an OpenAPI spec to Fieldbook. Generate docs from the spec.
**Assessment:** Hand the student's API + docs to *another student* and have them integrate against it cold. Friction = grade.

### Week 5 — Relational databases & SQL
**Objectives:** Model data relationally; write non-trivial SQL; reason about integrity.
**Topics:** Tables, keys, relationships, normalization (and when to denormalize), SQL depth (joins, aggregates, subqueries), constraints & referential integrity, transactions & ACID, indexes and what they cost.
**Lab:** Design Fieldbook's schema. Replace in-memory storage with a real relational DB. Hand-write the SQL before introducing any ORM.
**Assessment:** Schema review + a live SQL challenge (write a 3-table join under time). Explain one index you added and its write-time cost.

### Week 6 — Persistence patterns & data access
**Objectives:** Work with databases from application code safely and maintainably.
**Topics:** ORMs vs query builders vs raw SQL (trade-offs, not dogma), migrations & schema evolution, connection pooling, the N+1 problem, transactions in application code, intro to NoSQL (document/key-value) and *when it's actually the right tool*, CAP theorem at a working level.
**Lab:** Introduce a migration system and a data-access layer. Fix a deliberately planted N+1. Add a schema migration without downtime-thinking.
**Assessment:** Explain the migration rollback plan. Justify ORM vs raw SQL for two different queries in the project.

### Week 7 — Integration testing & CI
**Objectives:** Test a system with real dependencies; automate the whole thing.
**Topics:** Integration tests against a real (ephemeral) database, test data management & isolation, contract testing, the flaky-test problem and how to kill it, CI pipelines, running tests on every push, branch protection, test parallelization.
**Lab:** Add an integration test suite hitting a throwaway DB. Stand up CI (e.g. GitHub Actions) that runs unit + integration on every PR. **From here, no PR merges without green CI.**
**Assessment:** Break the build on purpose; show the pipeline catching it. Explain how the suite avoids flakiness.

### Week 8 — Authentication & authorization
**Objectives:** Let users prove who they are and control what they can do — without shooting themselves in the foot.
**Topics:** Passwords done right (hashing, salting, never storing plaintext), sessions vs tokens, JWT (and its footguns), OAuth2/OIDC conceptually, authn vs authz, role-based access control, the principle of least privilege.
**Lab:** Add users, registration, login, and token-based auth to Fieldbook. Add roles so users only see their own records; admins see all.
**Assessment:** Threat-model the auth flow. What happens if a token leaks? How is it revoked?

### Week 9 — Async, queues & background work
**Objectives:** Do work outside the request/response cycle; integrate with other systems.
**Topics:** Why not everything belongs in a request, job queues & workers, message brokers / pub-sub, webhooks (sending and receiving), retries, idempotency, and dead-letter handling, eventual consistency as a design reality.
**Lab:** Move a slow operation (e.g. export/report generation) to a background job. Add an outgoing webhook on record changes with retry + idempotency.
**Assessment:** What happens when a worker dies mid-job? When a webhook receiver is down for an hour? Defend the retry strategy.

### Week 10 — Caching & performance
**Objectives:** Make it fast on purpose, and prove it.
**Topics:** Latency vs throughput, where to cache (in-process, distributed/Redis, HTTP/CDN), cache invalidation strategies & TTLs, measuring before optimizing, load testing, query optimization with EXPLAIN, connection & resource limits.
**Lab:** Load-test Fieldbook to find a bottleneck. Add caching. **Show the before/after numbers** — no measurement, no credit.
**Assessment:** Present the profiling data. Which cache did you choose and why? What's your invalidation strategy and how does it go wrong?

### Week 11 — Architecture & design
**Objectives:** Structure a codebase so it survives growth and new engineers.
**Topics:** Layered vs hexagonal/ports-and-adapters architecture, domain modeling, SOLID *applied* (not recited), dependency inversion for testability, monolith vs microservices (and why "monolith first" is usually right), coupling & cohesion.
**Lab:** Refactor Fieldbook into a clean layered or hexagonal architecture. Swap one adapter (e.g. the DB, or a notification channel) to prove the seams work.
**Assessment:** Draw the architecture. Show that business logic has zero framework/DB imports. Justify monolith vs services for this system.

### Week 12 — Containerization & configuration
**Objectives:** Package the app so it runs identically everywhere.
**Topics:** Docker fundamentals, images vs containers, multi-stage builds, Docker Compose for local multi-service dev, the 12-factor app, config & secrets via environment, image size & security hygiene, intro to orchestration (what Kubernetes solves — conceptual, not deep).
**Lab:** Containerize Fieldbook. Compose it with its database and cache. Move all config to environment variables; no secrets in the repo.
**Assessment:** Fresh-machine test: clone + `compose up` + it runs. Explain the multi-stage build and why the image is the size it is.

### Week 13 — CI/CD & deployment
**Objectives:** Ship to a real environment automatically and safely.
**Topics:** Continuous delivery vs deployment, build → test → deploy pipelines, environments (dev/staging/prod), deployment strategies (rolling, blue-green, canary), rollbacks, database migrations in a pipeline, intro to infrastructure-as-code.
**Lab:** Extend Week 7's CI into full CD: on merge to main, build the image and deploy to a real host/platform. Include an automated migration step and a documented rollback.
**Assessment:** Push a change; watch it reach production untouched. Trigger a rollback. Explain how migrations don't break a rolling deploy.

### Week 14 — Observability & reliability
**Objectives:** Know what your system is doing in production, and find out *before* users do.
**Topics:** Structured logging, metrics (the four golden signals), distributed tracing (concept), health checks & readiness probes, error tracking/alerting, SLIs/SLOs, graceful degradation & timeouts, the incident basics.
**Lab:** Add structured logging, a `/health` endpoint, request metrics, and error tracking to Fieldbook. Create one dashboard and one alert.
**Assessment:** Inject a failure. Show that logs, metrics, and alerting surface it. What's your SLO and how would you know it's breached?

### Week 15 — Security hardening
**Objectives:** Close the common holes before an attacker or auditor finds them.
**Topics:** OWASP Top 10 walkthrough, input validation & injection (SQL, command), authn/authz pitfalls revisited, rate limiting & abuse prevention, secrets management, HTTPS/TLS, dependency & supply-chain scanning, security headers.
**Lab:** Run a security pass on Fieldbook: add rate limiting, fix any injection surface, move secrets to a proper store, add dependency scanning to CI.
**Assessment:** Present an OWASP checklist with evidence for each item. Demonstrate rate limiting under a burst.

### Week 16 — Capstone & career
**Objectives:** Design and defend an original extension; be interview-ready.
**Topics:** System design fundamentals (scaling, load balancing, statelessness, sharding at a conceptual level), reading & drawing architecture diagrams, backend interview patterns, portfolio & README craft.
**Lab:** Each student extends Fieldbook (or forks the design) with a substantial feature *they* scope — search, real-time notifications, a second service, multi-tenancy, etc. Their design, their trade-offs.
**Assessment:** Capstone demo + a live system-design whiteboard ("design a URL shortener / rate limiter / notification service"). Defended, not just described.

---

## Assessment & grading model

- **Per-module gate:** lab merged to main, green CI, and a passing *defense* (the trade-off conversation). No defense, no pass.
- **Midpoint checkpoint (end Week 8):** a running, tested, authenticated API. Students who can't clear this get intervention before the harder second half.
- **Final:** capstone demo + system-design interview + a clean, documented repo.
- **Portfolio artifact:** the graded deliverable *is* the portfolio — one deep, production-shaped service they can walk an interviewer through end to end.

## Optional tracks (if you extend past 16 weeks)

- **Distributed systems deep-dive:** consensus, event sourcing, CQRS, sagas
- **Data engineering lean-in:** streaming, ETL, analytical stores
- **Platform/DevOps lean-in:** real Kubernetes, IaC (Terraform), GitOps
- **Language second-pass:** re-implement two modules in a *different* language to prove the concepts transferred

---

## A note on stack choice per cohort

The curriculum is concept-first so it runs in any language, but the *teaching* is easiest to support when the whole cohort shares one:

- **Python (FastAPI/Django):** gentlest on-ramp, huge ecosystem, great for mixed-experience cohorts.
- **Node/TypeScript:** one language front-to-back if students also touch frontend; types add rigor.
- **Go:** best for teaching concurrency, performance, and "how the machine actually works" — steeper but produces strong systems thinkers.

Pick one, teach every lab in it, and keep the concept vocabulary constant so a graduate can pick up the next language on their own.
