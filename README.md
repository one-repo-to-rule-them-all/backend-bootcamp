# Backend Engineering Bootcamp — Course Reader

Start here. This is the front door to a complete, 16-week, project-based backend engineering course built around **Python**. Six documents make up the full set; this reader tells you what each one is, what order to read them in, and how the pieces fit.

The whole course is organized around building **one service — "Fieldbook"** — from an in-memory Python library in Week 1 to a deployed, observable, hardened production API with a self-designed capstone in Week 16. Same codebase, growing every week. No disconnected toy exercises.

---

## Who this is for

Anyone who can already write basic code in *some* language and wants to become an employable backend engineer. It assumes no prior backend experience but does assume you can navigate a terminal, use Git, and write a simple function. It is deliberately rigorous: the goal is engineers who can *defend* their choices, not learners who can follow a tutorial.

It works two ways:
- **Self-directed learner:** work through the phase workbooks week by week. Each week is self-contained — read, understand, build, check the boxes.
- **Instructor / cohort:** teach it as a 16-week program. The workbooks are the lesson plans; the assessment model (below) is built in.

---

## The six documents & reading order

Read them in this order. The first two set up the *what* and *how*; the four workbooks are the executable course.

1. **`curriculum/01-curriculum-design.md`** — the course design.
   The 16-week structure, the teaching philosophy, the spine-project concept, the assessment model, and optional extension tracks. *Read this first to understand how the course thinks.*

2. **`curriculum/02-python-stack.md`** — the Python implementation layer.
   Pins every concept to a concrete 2026 Python stack (uv, Ruff, mypy, pytest, FastAPI, Pydantic, SQLAlchemy…), with the framework rationale and a curated list of free Python resources. *Read this to know exactly what you'll be using and why.*

3. **`curriculum/03-phase-1-weeks-1-4.md`** — **Phase 1: Foundations to Your First API.**
4. **`curriculum/04-phase-2-weeks-5-7.md`** — **Phase 2: Durable & Trustworthy.**
5. **`curriculum/05-phase-3-weeks-8-11.md`** — **Phase 3: Identity, Scale & Shape.**
6. **`curriculum/06-phase-4-weeks-12-16.md`** — **Phase 4: Production & Proof.**

Each workbook uses the same rhythm every week: **Objectives → Setup → Read → Understand → Build → Done when.** Read before you build. Build by writing code, not by reading about it. A week is finished only when every "Done when" box is checked.

---

## The phase map & milestones

| Phase | Weeks | Theme | Milestone by the end |
|---|---|---|---|
| **1** | 1–4 | Foundations to your first API | A tested, validated, documented REST API running locally |
| **2** | 5–7 | Durable & trustworthy | Backed by PostgreSQL with migrations; integration tests gating every merge in CI |
| **3** | 8–11 | Identity, scale & shape | Real auth + roles, background jobs & webhooks, measured caching, clean hexagonal architecture |
| **4** | 12–16 | Production & proof | Containerized, deployed via CI/CD, observable, hardened, plus a self-designed capstone |

Each phase is a real checkpoint. If you only ever finish Phase 2, you still have a genuinely durable, tested, deployable-adjacent service to show.

---

## How Fieldbook grows, week by week

The project *is* the curriculum. This is the arc:

| Week | Fieldbook becomes… |
|---|---|
| 1 | A clean, typed, modular in-memory Python library |
| 2 | …with a full unit-test suite, built test-first |
| 3 | An HTTP REST API serving JSON (correct methods & status codes) |
| 4 | …validated, paginated, with a consistent error envelope + OpenAPI docs |
| 5 | Backed by PostgreSQL via hand-written, parameterized SQL |
| 6 | …managed with SQLAlchemy + Alembic migrations; N+1 found and fixed |
| 7 | Covered by integration tests against a real DB, gated in CI |
| 8 | Authenticated with real users, JWTs, and role-based ownership |
| 9 | Doing async work: background jobs + signed, retrying webhooks |
| 10 | Faster on measured evidence: cache-aside with before/after numbers |
| 11 | Cleanly re-architected — domain core, ports, swappable adapters |
| 12 | Containerized: multi-stage Docker + Compose, 12-factor config |
| 13 | Deployed to production through an automated CI/CD pipeline |
| 14 | Observable: structured logs, metrics, traces, health checks, alerts |
| 15 | Hardened: OWASP pass, rate limiting, CI security scanning |
| 16 | Extended with a capstone you designed — and can defend end to end |

---

## The spine — rules that run through every week

These recur by design. They're the difference between an engineer who understands backends and one who fills in framework templates:

- **Feel the primitive before the abstraction.** Raw SQL before the ORM (Week 5→6). Raw HTTP before framework sugar (Week 3→4). You can't reason about what you've never seen underneath.
- **Types on from Week 1.** `mypy --strict` on every commit. Retrofitting types onto an untyped codebase is misery; typed-from-the-start makes the checker a teaching assistant.
- **Nothing merges without green CI** (from Week 7). The pipeline is the objective arbiter of "done," not "works on my machine."
- **Never optimize, secure, or 'fix' without evidence.** Measure before/after (Week 10). Prove authz adversarially (Week 15). Test the invalidation (Week 10).
- **Infrastructure depends on the domain, not the reverse** (Week 11). The `RecordRepository` Protocol, introduced in Week 5, is what makes the Week 11 architecture refactor a relocation instead of a rewrite. Decisions compound.
- **Assess by defending, not completing.** Every week ends by explaining *why you did it this way and what breaks at 100x load* — not just showing green checkmarks.

---

## The stack at a glance

Pinned to the 2026 Python consensus (full detail in the stack doc):

- **Tooling:** uv (envs/deps/versions), Ruff (lint+format), mypy strict, pytest
- **Web:** FastAPI + Pydantic v2
- **Data:** PostgreSQL, psycopg 3, SQLAlchemy 2.0, Alembic
- **Async & cache:** Redis, arq, Locust (load testing)
- **Ops:** Docker + Compose, GitHub Actions, a PaaS deploy target (Fly.io / Render / Railway)
- **Observability & security:** structlog, prometheus-client, OpenTelemetry, Sentry, slowapi, bandit, pip-audit

**Framework choice:** FastAPI over Django — deliberately, because this course teaches fundamentals *explicitly* and FastAPI keeps HTTP, validation, and dependency injection in the foreground rather than hiding them. Django swap points are noted per module for anyone who wants batteries-included instead.

---

## Assessment model (for cohorts)

- **Per-week gate:** lab merged, green CI, and a passing *defense* (the trade-off conversation). No defense, no pass.
- **Midpoint checkpoint (end of Week 8):** a running, tested, authenticated API. Anyone who can't clear it gets intervention before the harder second half.
- **Final:** capstone demo + a live system-design round + a clean, documented repo.
- **The graded artifact is the portfolio:** one deep, production-shaped service the learner can walk an interviewer through end to end.

---

## Honest limits of this curriculum

Stated plainly, because teaching engineers to know what they *don't* yet know is part of the job:

- **It's a single-service curriculum.** Distributed systems, inter-service communication, and real Kubernetes are covered conceptually (Week 12) and at the capstone — not built to depth. This is a deliberate scope choice: a monolith done well teaches more than a distributed system done badly. But graduates should know it's the next mountain, not a conquered one.
- **Deployment is platform-as-a-service, not production Kubernetes.** "I deployed to Fly.io" is real and sufficient at this level; it is not "I ran production k8s." Don't let it be mistaken for the latter.
- **Auth reaches production concepts, but JWT revocation is closed only if the capstone tackles it.** A bare stateless JWT is the teaching baseline, not the finish line — the curriculum has learners document that gap explicitly in Week 8.

---

## Where to go deeper (optional tracks)

If you extend past 16 weeks, the natural next mountains are: a **distributed-systems** deep-dive (consensus, event sourcing, CQRS, sagas), a **platform/DevOps** lean-in (real Kubernetes, Terraform, GitOps), a **data-engineering** lean-in (streaming, ETL), or a **second-language pass** — re-implementing two modules in Go to prove the concepts, not the syntax, are what you learned. The curriculum doc has the full list.

---

*Begin with the curriculum doc, then the stack doc, then open Phase 1 and run the Week 1 setup block. Everything after that is one service, one week at a time.*

---

## This repository

```
backend-bootcamp/
├── README.md                     # you are here — the course reader
├── curriculum/                   # the course, in reading order
│   ├── 01-curriculum-design.md
│   ├── 02-python-stack.md
│   ├── 03-phase-1-weeks-1-4.md
│   ├── 04-phase-2-weeks-5-7.md
│   ├── 05-phase-3-weeks-8-11.md
│   └── 06-phase-4-weeks-12-16.md
└── reference/
    └── fieldbook-starter/        # runnable reference impl (Weeks 1–2 end state)
```

**`reference/fieldbook-starter/`** is a complete, runnable exemplar of what a "done" week looks like — it passes `ruff`, `mypy --strict`, and `pytest` at 100% coverage. See its own README for the quickstart, the grading rubric, and how the CI evolves in Week 7.
