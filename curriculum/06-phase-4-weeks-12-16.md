# Backend Bootcamp — Phase 4: Production & Proof
## Weeks 12–16 · Detailed Lesson Plans

Same rhythm: **Objectives → Setup → Read → Understand → Build → Done when.** This is the final phase — it makes Fieldbook *deployable* and makes *you* interviewable.

**Where you left off:** Fieldbook is a cleanly-architected, authenticated, cached, tested service — that only runs on your laptop, tells you nothing when it breaks, and hasn't been probed for security holes. This phase ships it, watches it, hardens it, and has you extend and defend it.

**Stack added this phase:** Docker Compose (formalized), a deploy platform (Fly.io / Render / Railway), `structlog`, `prometheus-client`, OpenTelemetry, Sentry, `slowapi`, `bandit`, `pip-audit`.
**Weekly load:** ~20–25 hrs.

---

# Week 12 — Containerization & Configuration

**Goal:** Package the app so it runs identically on your laptop, in CI, and in production. One command brings up the whole stack.

### Objectives
- Write a multi-stage Dockerfile that produces a small, non-root runtime image
- Orchestrate app + Postgres + Redis with Docker Compose
- Move all configuration to the environment (12-factor)
- Run migrations automatically as part of startup

### Read (~4.5 hrs)
- **Docker docs** (docs.docker.com) — "Get started" + Dockerfile reference + `.dockerignore`. *Focus on:* image vs container, layers/caching, and **multi-stage builds**.
- **Docker Compose docs** — *Focus on:* defining multiple services, `depends_on`, `environment`, and healthchecks.
- **The Twelve-Factor App** (12factor.net) — Config, Dependencies, Backing Services, Dev/Prod Parity. *Focus on:* config lives in the environment, never in code.
- **uv in Docker** — search "uv docker multi-stage." *Focus on:* installing deps with uv in a build stage and copying only the result into a slim runtime.
- **Skim:** "what does Kubernetes solve" — *conceptual only.* *Focus on:* scheduling, scaling, self-healing — and why you don't need it for a monolith yet.

### Understand
- **Image vs container:** the image is the built artifact; a container is a running instance of it. Immutable image, disposable containers.
- **Multi-stage builds:** compile/install in a fat build stage, copy only the runnable artifact into a slim runtime image. Smaller image, smaller attack surface, no build tools shipped to prod.
- **12-factor config:** the same image runs in every environment; only the injected env vars differ. Secrets never bake into the image.
- **Non-root by default:** run the app as an unprivileged user so a container compromise doesn't hand over root.

### Build — containerize the stack (~13 hrs)
1. **Dockerfile (multi-stage):** build stage installs deps with uv; runtime stage on `python:3.13-slim` copies the venv + app, creates and switches to a non-root user, runs uvicorn. Add a `.dockerignore`.
2. **`docker-compose.yml`:** `app` + `postgres` + `redis`, wired entirely through env vars (`DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`). This formalizes the ad-hoc `docker run` commands from earlier weeks into one declarative file.
3. **Config:** confirm *all* settings load from the environment via `pydantic-settings`. Local dev uses a **gitignored** `.env`; nothing sensitive is committed.
4. **Migrations on startup:** an entrypoint (or a one-shot compose service) runs `alembic upgrade head` before the app serves traffic.
5. **Fresh-machine test — this is the acceptance test:** on a clean checkout, `docker compose up` brings the entire stack to life and the API answers.

### Done when
- [ ] Multi-stage Dockerfile produces a slim image running as non-root
- [ ] `docker compose up` starts app + Postgres + Redis, wired by env
- [ ] All config comes from the environment; zero secrets in the repo (`.env` gitignored)
- [ ] Migrations apply automatically before the app serves
- [ ] A fresh clone + `docker compose up` works with no manual steps
- [ ] You can explain the multi-stage build and the resulting image size
- [ ] Committed

---

# Week 13 — CI/CD & Deployment

**Goal:** Ship to a real, public environment automatically and safely — merge to `main`, and it's live, hands-off.

### Objectives
- Extend the Week 7 CI pipeline into continuous deployment
- Deploy the Week 12 container to a managed platform with attached Postgres/Redis
- Run migrations safely inside the pipeline
- Perform a rollback, and understand zero-downtime migrations

### Setup
Pick one platform with a low-friction tier: **Fly.io** (deploys your Docker image directly — reuses Week 12 with no rework), **Render**, or **Railway**. Create the app and attach a managed Postgres + Redis.

### Read (~4.5 hrs)
- **CD concepts** — search "continuous delivery vs continuous deployment." *Focus on:* the distinction, and the build → test → deploy flow.
- **Your platform's docs** — deploying a Docker app, setting secrets/env, attaching managed Postgres. *Focus on:* the deploy step and secret injection.
- **GitHub Actions deploy** — search "GitHub Actions deploy Docker [your platform]." *Focus on:* a job that builds/pushes the image and deploys on merge to `main`.
- **Deployment strategies** — search "rolling vs blue-green vs canary." *Focus on:* rolling deploys, zero-downtime, and rollback.
- **Zero-downtime migrations** — search "expand contract migration pattern." *Focus on:* why schema changes must stay backward-compatible while old and new code run side by side during a rollout.

### Understand
- **CI vs CD:** CI (Week 7) proves every PR is safe; CD deploys automatically once it's merged. You're extending the same pipeline, not building a new one.
- **Secrets at deploy, not in the image:** the platform injects `JWT_SECRET`, DB URLs, etc. at runtime. The image stays generic and shareable.
- **Rolling deploys need backward-compatible migrations:** during a rollout, old and new pods run at once against the *same* database. A destructive migration (drop/rename a column the old code still uses) breaks the old pods mid-deploy. The **expand/contract** pattern avoids this: expand (add the new nullable column) → deploy code that writes both → backfill → contract (remove the old) in a *later* deploy.
- **Rollback is a first-class operation:** you should be able to get back to the last good version fast, and you should have practiced it before you need it at 2am.

### Build — the deploy pipeline (~13 hrs)
1. **CI → CD:** extend the Week 7 workflow so that on merge to `main`, *after* tests pass, it builds the image, pushes it, and deploys to the platform. The Week 12 Dockerfile is reused unchanged.
2. **Managed backing services:** attach the platform's Postgres + Redis; set all secrets via the platform, not the repo.
3. **Migrations in the pipeline:** `alembic upgrade head` runs as a deploy step before the new version takes traffic.
4. **Environments:** at minimum a production environment; ideally a staging environment that gates prod.
5. **Ship for real:** push a trivial change and watch it flow PR → merge → build → deploy → live, untouched by hand.
6. **Rollback drill:** deploy a deliberately broken change (or use the platform's rollback), roll back, and confirm recovery.
7. **Zero-downtime migration exercise:** rename a column across *two* deploys using expand/contract — never in one destructive step.

### Done when
- [ ] Merge to `main` triggers build → deploy automatically; the Week 12 image is reused
- [ ] Managed Postgres + Redis attached; secrets injected at deploy, never in the repo
- [ ] Migrations run in the pipeline before new code serves traffic
- [ ] You deployed a change end-to-end with zero manual steps and it reached production
- [ ] You performed a rollback and recovered
- [ ] You can explain expand/contract and why a destructive migration breaks a rolling deploy
- [ ] Committed

---

# Week 14 — Observability & Reliability

**Goal:** Know what the system is doing in production — and find out it's broken *before* your users tell you.

### Objectives
- Emit structured logs with a per-request correlation id
- Expose metrics (the golden signals) and distributed traces
- Add health checks and error tracking
- Define an SLI/SLO and an alert; make the system fail fast, not hang

### Setup
```bash
uv add structlog prometheus-client sentry-sdk \
  opentelemetry-sdk opentelemetry-instrumentation-fastapi
```

### Read (~5 hrs)
- **structlog docs** — *Focus on:* JSON output and binding context (a request id) so every log line for a request is correlated.
- **Google SRE Book** (sre.google/books, free) — "Monitoring Distributed Systems" (the **four golden signals**: latency, traffic, errors, saturation) and the **SLO** chapter. *Focus on:* what to measure and what an error budget is.
- **prometheus-client docs** — *Focus on:* counters and histograms, and exposing a `/metrics` endpoint.
- **OpenTelemetry Python** — FastAPI auto-instrumentation. *Focus on:* what a trace/span is and seeing a request's spans including the DB call.
- **Skim:** liveness vs readiness probes; timeouts and graceful degradation.

### Understand
- **Three pillars:** logs (what happened), metrics (how much / how often), traces (where the time went across a request). You want all three; they answer different questions.
- **Correlation id:** bind a request id at the edge and attach it to every log line and span, so you can reconstruct one request's whole journey from a pile of logs.
- **Golden signals:** latency, traffic, errors, saturation — the four numbers that tell you if a service is healthy.
- **SLI/SLO/error budget:** an SLI is a measured indicator (e.g. p99 latency, error rate); an SLO is the target for it; the error budget is how much you're allowed to miss before you stop shipping features and fix reliability.
- **Readiness ≠ liveness:** liveness = "is the process alive"; readiness = "can it actually serve" (DB reachable?). Load balancers route on readiness.
- **Fail fast:** a request should time out on a slow dependency and degrade, not hang forever holding a connection.

### Build — make it observable (~12 hrs)
1. **Structured logging:** structlog emitting JSON; middleware that binds a request id to every log line for the request.
2. **Health endpoint:** `/health` readiness check that verifies Postgres (and Redis) connectivity and returns **503** if a dependency is down.
3. **Metrics:** `/metrics` via prometheus-client; middleware recording request count and a latency histogram (your HTTP golden signals).
4. **Tracing:** OpenTelemetry FastAPI auto-instrumentation; confirm a request produces spans spanning the route and the DB call.
5. **Error tracking:** Sentry SDK capturing unhandled exceptions with the request context.
6. **SLO + alert:** define one SLI/SLO (e.g. "99% of `GET /records` under 200ms" or "error rate < 1%"), and wire one alert (a free-tier alert or, at minimum, a documented alerting rule).
7. **Timeout drill:** add a timeout to an outbound call; inject a slow/failing dependency and show the system fails fast and surfaces the failure in logs/metrics/alerts — instead of hanging.

### Done when
- [ ] Structured JSON logging with a per-request correlation id
- [ ] `/health` reflects real dependency status (503 when the DB is down)
- [ ] `/metrics` exposes request rate + latency; Sentry captures exceptions
- [ ] Traces show spans across a request including the DB call
- [ ] One SLI/SLO defined and one alert configured or documented
- [ ] An injected failure surfaces in observability and the system fails fast (timeout), not hangs
- [ ] Committed

---

# Week 15 — Security Hardening

**Goal:** Close the common holes before an attacker or an auditor finds them — and make security a CI gate, not a one-time pass.

### Objectives
- Work the OWASP Top 10 against your own service
- Add rate limiting and automated security scanning to CI
- Prove object-level authorization and mass-assignment protection adversarially
- Get secrets fully out of the codebase

### Setup
```bash
uv add slowapi
uv add --dev bandit pip-audit
```

### Read (~4.5 hrs)
- **OWASP Top 10** (owasp.org/www-project-top-ten). *Focus on:* broken access control, injection, identification/auth failures, security misconfiguration, vulnerable components.
- **OWASP API Security Top 10** — *Focus on:* **BOLA** (broken object-level authorization) and **mass assignment** especially — you'll test both.
- **slowapi docs** — *Focus on:* per-IP / per-user rate limits and burst protection.
- **bandit + pip-audit** — search each. *Focus on:* SAST for your code (bandit) and CVE scanning for your dependencies (pip-audit), both in CI.
- **Secrets management** — search "secrets management best practices." *Focus on:* env vs a vault, rotation, and secret scanning in the repo.

### Understand
- **The Top 10 is a checklist, not trivia:** each item maps to something concrete in Fieldbook. Walk it with your own code open.
- **BOLA / IDOR:** can user A read user B's record by guessing its id? You *designed* against this in Week 8 — now you **prove** it under adversarial testing rather than assuming it.
- **Mass assignment:** this is exactly why Week 4 used separate input schemas — a client must not be able to set `role: admin` or `owner_id` on itself. Verify the schema actually blocks it.
- **Injection is already mostly handled:** your Week 5 parameterized queries prevent SQL injection. Connect that dot explicitly — you built the defense; now name it.
- **Security is a gate:** bandit + pip-audit run in CI and fail the build on high-severity findings, so a vulnerability can't quietly merge.

### Build — the hardening pass (~13 hrs)
1. **Rate limiting:** slowapi on the login endpoint (stop brute force) and a sane global limit. Prove it with a burst test.
2. **Scanning in CI:** add bandit (SAST) and pip-audit (dependency CVEs) to the pipeline; triage/fix findings; fail the build on high severity.
3. **Adversarial authz tests:** write tests proving user A **cannot** get/update/delete user B's record (404), and that the API **rejects** attempts to set `role`/`owner_id` via the request body.
4. **Secrets:** confirm nothing sensitive is in git history; enable secret scanning (GitHub secret scanning or gitleaks in CI); document a rotation process.
5. **Headers + TLS:** add security headers; confirm the platform terminates/enforces HTTPS.
6. **OWASP checklist (in the repo):** for each relevant Top 10 item, note how Fieldbook addresses it, with the test or config as evidence.

### Done when
- [ ] Rate limiting active (login + global), proven by a burst test
- [ ] bandit + pip-audit run in CI and gate on high-severity findings
- [ ] Adversarial tests prove BOLA and mass-assignment are blocked
- [ ] Secrets confirmed out of git; secret scanning enabled; rotation documented
- [ ] Security headers set; HTTPS enforced
- [ ] An OWASP Top 10 checklist with per-item evidence lives in the repo
- [ ] Committed

---

# Week 16 — Capstone & Career

**Goal:** Design, build, and defend an original extension — and walk out interview-ready with a system you understand end to end.

### Objectives
- Scope and ship a substantial feature of your own design
- Speak the system-design vocabulary for the primitives you've built
- Present the project so a stranger (or interviewer) gets it fast
- Defend your architecture and trade-offs live

### Read (~5 hrs)
- **System Design Primer** (github.com/donnemartin/system-design-primer, free). *Focus on:* horizontal scaling, load balancing, statelessness, caching, replication, sharding, and consistency trade-offs — most of which you've now *implemented* in miniature.
- **Backend interview patterns** — search "backend engineer interview questions." *Focus on:* API design, schema design, concurrency, and the system-design round.
- **README/portfolio craft** — *Focus on:* a README that lets someone run and understand the project in five minutes.

### Understand
- **You've built the primitives; now name them at scale:** your stateless auth is *why the app scales horizontally behind a load balancer*; your cache is a *read-path optimization*; your queue is *how you shed load*; your health check is *what the load balancer routes on*. System design is largely composing things you've already built.
- **Reasoning under scale:** find the bottleneck, the single point of failure, and the consistency trade-off. "Fieldbook at 1M users" is answerable with read replicas, a cache tier, a queue, and statelessness — all things you touched.
- **The interview is the defense:** you'll be asked *why*, not *what*. Every deliberate choice in this course (Protocol, raw-SQL-first, expand/contract, cache-with-measurement) is an answer.

### Build — capstone + career artifacts (~13 hrs)
1. **Capstone (your design):** scope and ship a substantial Fieldbook extension — e.g. full-text search, real-time notifications (SSE/WebSocket), multi-tenancy, a second service with inter-service comms, or **refresh-token auth (closing the Week 8 gap)**. It must be tested, migrated, observable, secured, and deployed through your pipeline — i.e. it meets the bar the rest of the course set.
2. **Design doc:** a short writeup of what you built, the approach, and the trade-offs you chose against. Update the architecture diagram.
3. **Scale writeup:** "How would Fieldbook serve 1M users?" — grounded in the primitives you built (LB, read replicas, cache tier, queue, statelessness).
4. **README polish:** run-in-5-minutes instructions, architecture overview, example requests.
5. **Live system-design reps:** whiteboard a URL shortener, a rate limiter, and a notification service. Time-boxed, out loud.
6. **Final defense:** demo the capstone, walk the repo, and do a system-design mock — answering *why* at every layer.

### Done when
- [ ] Capstone feature designed, built, tested, deployed, and documented with a design doc
- [ ] README lets a stranger run and understand the project quickly
- [ ] A "scale to 1M users" writeup grounded in what you built
- [ ] You completed at least one live system-design mock out loud
- [ ] Final defense passed: capstone demo + repo walkthrough + system-design round
- [ ] Tagged `v1.0` — course complete

---

## End of Phase 4 — course complete

Fieldbook is now a **deployed, observable, hardened, cleanly-architected production service** with a feature you designed yourself — and you can defend every layer of it, because you built each one deliberately and know why it's there. That defensible, end-to-end project is the entire point: it's what you walk an interviewer through, and it's worth more than any completion certificate.

### The habits that made it real
- The same codebase grew for 16 weeks — depth over a folder of disconnected toys.
- Feel the primitive before the abstraction (raw SQL before ORM, raw HTTP before framework sugar).
- Nothing merges without green CI; nothing ships without a rollback plan.
- Never optimize, secure, or "fix" without evidence — measure, prove, test.
- Infrastructure depends on the domain, not the reverse.

### Honest limits of this curriculum (say these out loud to any cohort)
- **It's a single-service curriculum.** Distributed systems, inter-service comms, and real Kubernetes are touched conceptually (Week 12) and at the capstone, not built to depth. That's a deliberate scope choice — a monolith done well teaches more than a distributed system done badly — but graduates should know it's the next mountain, not a covered one.
- **Deploy is platform-as-a-service, not production Kubernetes.** "I deployed to Fly.io" is real and sufficient for this level; it is not "I ran production k8s." Don't let it be mistaken for the latter.
- **Auth reaches production concepts but the capstone is where revocation gets closed** (if the student picks it). A bare JWT is the teaching baseline, not the finish line.

These aren't gaps to paper over — they're the honest edges of a 16-week scope, and naming them is part of teaching engineers to know what they don't yet know.
