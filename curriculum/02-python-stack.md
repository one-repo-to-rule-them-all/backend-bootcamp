# Backend Bootcamp — Python Implementation Layer

Companion to the 16-week curriculum. This pins the concepts to a concrete, modern (2026) Python stack so every lab is runnable. Concepts stay portable; the syntax and tooling are fixed cohort-wide here.

**Framework spine:** FastAPI + Pydantic v2.
**Why FastAPI over Django:** this curriculum teaches fundamentals *explicitly*. FastAPI keeps HTTP semantics, validation, and API design in the foreground; Django's batteries-included magic hides exactly the machinery Weeks 3–6 exist to reveal. Django swap points are noted per module if you prefer batteries over transparency.

---

## Core toolchain — pin this on Day 1, cohort-wide

The 2026 Python stack has consolidated into a small, fast, coherent set. Teach it once in Week 0 and use it in every lab:

| Tool | Replaces | Role |
|---|---|---|
| **uv** | pip, venv, virtualenv, pyenv, poetry | Python versions, environments, dependencies, lockfile, running commands |
| **Ruff** | black, flake8, isort, pyupgrade | Linting + formatting in one binary |
| **mypy** (`--strict`) | — | Static type checking; the production baseline |
| **pytest** | unittest | Test runner for everything |

Everything configures in a single `pyproject.toml`. Add **pre-commit** hooks running Ruff + mypy so issues die before CI.

Standard project kickoff students should internalize:

```bash
uv init fieldbook && cd fieldbook
uv add fastapi "uvicorn[standard]" "pydantic>=2"
uv add --dev pytest ruff mypy
uv run uvicorn app.main:app --reload
```

No `pip install`, no manual venv activation. `uv run` executes inside the project env automatically. This one habit removes a whole class of "works on my machine" onboarding pain from the cohort.

---

## Per-module Python stack

### Week 1 — Foundations
**Stack:** Python 3.13, type hints, `dataclasses`, exceptions, `pathlib`. Ruff + mypy enforced from the first commit.
**Note:** Require type hints from day one. In a typed-from-the-start cohort, mypy becomes a teaching assistant that catches conceptual errors, not just syntax.

### Week 2 — Testing & TDD
**Stack:** `pytest`, fixtures, `unittest.mock` (or `pytest-mock`), `pytest-cov`. Bonus: `hypothesis` for property-based testing once they're comfortable.
**Note:** Teach pytest fixtures deliberately — they're the mechanism the whole rest of the course leans on for integration tests.

### Week 3 — HTTP & the web's contract
**Stack:** FastAPI + `uvicorn`. `httpx` as the client for hitting your own API. FastAPI's `TestClient` for endpoint tests.
**Django swap:** Django + Django REST Framework — but you'll spend Week 3 explaining DRF's serializer/viewset abstractions instead of raw HTTP, which is the wrong trade here.

### Week 4 — API design & validation
**Stack:** Pydantic v2 models for request/response schemas, FastAPI's automatic OpenAPI generation (validation and docs come *for free* and visibly — a major FastAPI teaching win), pagination via query params.
**Note:** Pydantic v2 makes validation a first-class, readable thing. Students see the schema *as* the contract.

### Week 5 — Relational databases & SQL
**Stack:** PostgreSQL. Hand-write SQL first via the raw driver (`psycopg` 3). No ORM yet — students must feel raw SQL before it's abstracted away.
**Resource pairing:** SQLBolt + "Use The Index, Luke" for the indexing lab.

### Week 6 — Persistence patterns
**Stack:** SQLAlchemy 2.0 (ORM + Core), Alembic for migrations. Introduce the ORM *after* raw SQL so they understand what it's doing. NoSQL taste: `redis-py` or MongoDB via `pymongo`.
**Note:** The planted N+1 lab is easy to stage with SQLAlchemy's lazy loading — a perfect, realistic teaching bug.

### Week 7 — Integration testing & CI
**Stack:** `pytest` against a real ephemeral Postgres via **testcontainers-python** (or a Postgres service container in CI). **GitHub Actions** running `uv sync`, Ruff, mypy, and the full test suite on every PR. Coverage gate.
**Note:** testcontainers is the cleanest way to teach "integration tests against the real thing, isolated per run." This is where the no-merge-without-green-CI rule turns on.

### Week 8 — Authentication & authorization
**Stack:** `argon2-cffi` (or `passlib[bcrypt]`) for password hashing, `pyjwt` for tokens, FastAPI's `Security`/`Depends` for the OAuth2 password flow and role dependencies.
**Note:** FastAPI's dependency-injection security utilities make authz *composable and visible* — students wire `require_role("admin")` as a dependency and see exactly where the check happens.

### Week 9 — Async, queues & background work
**Stack:** **Celery** + Redis (industry-standard, résumé-relevant) or **arq** (async-native, simpler, pairs naturally with FastAPI). Outgoing webhooks via `httpx` with retry/idempotency.
**Recommendation:** Start with arq for conceptual clarity, mention Celery as the one they'll meet in the wild.

### Week 10 — Caching & performance
**Stack:** Redis via `redis-py`, `functools.lru_cache` for in-process caching, **Locust** for load testing, `EXPLAIN ANALYZE` in Postgres, `py-spy` for profiling.
**Note:** Locust is Python-native and lets students *write* their load tests as code — reinforces the "measure before optimizing" rule with real numbers.

### Week 11 — Architecture & design
**Stack:** Hexagonal architecture in Python using `typing.Protocol` for ports, FastAPI `Depends` (or the `dependency-injector` lib) for wiring adapters.
**Resource:** **Cosmic Python — *Architecture Patterns with Python*** (free online). This book *is* the Week 11 reading. It teaches exactly this — ports/adapters, repository pattern, service layer — in Python. Assign it directly.

### Week 12 — Containerization & configuration
**Stack:** Docker multi-stage builds on a `python:3.13-slim` base (use uv in the build stage for fast, reproducible installs), Docker Compose for app + Postgres + Redis, `pydantic-settings` for env-based config.
**Note:** `pydantic-settings` ties config validation back to Week 4's Pydantic work — nice reinforcement.

### Week 13 — CI/CD & deployment
**Stack:** GitHub Actions builds and pushes the image; deploy to **Fly.io**, **Render**, or **Railway** (all have low-friction free-ish tiers good for a cohort). Alembic migration step in the pipeline.
**Note:** Fly.io deploys containers directly, so it reuses Week 12's Dockerfile with no rework — clean continuity.

### Week 14 — Observability & reliability
**Stack:** `structlog` for structured logging, `prometheus-client` for metrics, **OpenTelemetry Python** for tracing, **Sentry** SDK for error tracking. FastAPI middleware for request metrics; a `/health` endpoint.
**Note:** OTel has a first-class FastAPI auto-instrumentation package — students see traces with minimal wiring.

### Week 15 — Security hardening
**Stack:** **bandit** (SAST) and **pip-audit** (dependency/CVE scanning) added to CI, **slowapi** for rate limiting on FastAPI, secrets via environment (graduate to a vault conceptually).
**Note:** bandit + pip-audit in the pipeline makes "security is a CI gate, not a vibe" concrete.

### Week 16 — Capstone & career
**Stack:** No new tooling — students extend the existing stack. Focus shifts to system-design fundamentals and interview prep.

---

## Free, Python-specific resources (curated — not a link dump)

Pair these with the modules; don't assign all at once.

- **FastAPI official docs** — genuinely excellent and free; effectively a mini-course on Weeks 3–4 and 8. Tutorial + Advanced User Guide.
- **Cosmic Python — *Architecture Patterns with Python*** (cosmicpython.com) — free online book; the Week 11 spine.
- **The official Python Tutorial + Real Python (free articles)** — Week 0–1 reference.
- **SQLBolt** and **"Use The Index, Luke"** (use-the-index-luke.com) — Weeks 5–6, SQL and indexing.
- **pytest docs** and **"Effective Python Testing With pytest"** (Real Python) — Week 2.
- **The Twelve-Factor App** (12factor.net) — Week 12 config/deploy principles.
- **OWASP Top 10** (owasp.org) — Week 15.
- **SQLAlchemy 2.0 + Alembic docs** — Week 6.
- **OpenTelemetry Python docs** — Week 14.

### For self-study, not the cohort
If someone wants a paid, backend-Python-specific structured path *alongside* this, **boot.dev** is the closest match (Python/Go backend, project-driven) — but this curriculum plus the free resources above already covers more ground, in Python, with a deeper portfolio artifact at the end.

---

## Two things to hold the line on in a Python cohort

1. **Type hints and mypy strict from Week 1, not "later."** Python lets you skip types, so students will want to. Don't let them. Typed-from-the-start is the single highest-leverage habit for producing maintainable backend Python, and retrofitting types onto an untyped codebase is miserable — they'll learn that lesson the hard way if you let the habit slip.
2. **Raw SQL before the ORM (Week 5 before 6), raw HTTP before the framework sugar (Week 3 before 4's Pydantic).** The ordering is deliberate. An engineer who reaches for SQLAlchemy without ever having written a join, or who thinks "the framework handles HTTP," has a ceiling. Feel the primitive first, then abstract it.
