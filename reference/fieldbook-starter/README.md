# Fieldbook — Reference Starter (Weeks 1–2)

A **complete, runnable reference implementation** of the backend bootcamp's first milestone: the Fieldbook domain library, built and fully tested to house standard. Use it as the exemplar of what a "done" week looks like — the scaffold, the tooling config, the code style, the test discipline. Every later week grows from exactly this structure.

It passes `ruff`, `ruff format`, `mypy --strict`, and `pytest` at 100% coverage out of the box.

> **Why Weeks 1–2 and not Week 7?** A runnable starter has to stand alone. Week 7 (integration testing + CI) only makes sense on top of Weeks 1–6, so a "Week 7 starter" would either drag six weeks of code with it or test code that isn't there. The foundation is the honest home for a self-contained reference — and it's the scaffold every other week inherits. The Week 7 CI pipeline is shown at the bottom of this file as the evolution of the workflow already included here.

---

## Quickstart

With [uv](https://docs.astral.sh/uv/) (the toolchain the course uses):

```bash
uv sync --dev          # create the env + install dev tools
uv run ruff check .    # lint
uv run ruff format --check .
uv run mypy src tests  # strict type check
uv run pytest          # tests + coverage
```

That's the whole local loop — the same four commands run in CI (`.github/workflows/ci.yml`).

---

## Project structure

```
fieldbook-starter/
├── pyproject.toml          # single config: deps, ruff, mypy strict, pytest
├── .python-version         # pins 3.13
├── .gitignore
├── .github/workflows/ci.yml# lint + format + types + tests on every PR
├── src/fieldbook/
│   ├── __init__.py
│   ├── models.py           # Record (frozen dataclass) + Status (StrEnum)
│   ├── errors.py           # FieldbookError hierarchy
│   └── repository.py       # InMemoryRecordRepository (create/get/list/update/delete)
└── tests/
    ├── conftest.py         # the `repo` fixture
    └── test_repository.py  # behaviour suite: happy paths, errors, owner isolation
```

`src/` layout on purpose: it prevents tests from accidentally importing the package from the working directory instead of the installed one — a real source of "passes locally, fails in CI" bugs.

---

## The lab this implements

**Build Fieldbook's core domain logic as a pure, in-memory, fully-typed, fully-tested library — no web, no database.**

- `Record` — a frozen dataclass: `id`, `title`, `status` (`todo`/`doing`/`done`), `owner_id`, `created_at`.
- A custom exception hierarchy so callers can't silently ignore failures.
- `InMemoryRecordRepository` with:
  - `create(title, owner_id)` — generates id + timestamp, defaults to `todo`, rejects empty titles
  - `get(record_id)` — raises `RecordNotFoundError` when missing
  - `list(owner_id)` — returns only that owner's records
  - `update(record_id, *, title=None, status=None)` — returns a new record; raises on missing
  - `delete(record_id)` — raises on missing
- A pytest suite covering every method, both error paths, owner isolation, and validation.

**Two deliberate choices worth noting to learners:**
1. **`Record` is immutable** (`frozen=True`); `update` returns a *new* record via `dataclasses.replace`. Rules out aliasing bugs and models the value-object mindset early.
2. **`update` uses explicit typed keyword args, not `**changes`.** The curriculum sketches `**changes`, but that's effectively untyped and `mypy --strict` can't check it. The reference tightens it — a small but real "production-grade over convenient" call.

---

## Grading rubric (per-week template)

This is the rubric shape to reuse for every week. A week is not "done" on green checkmarks alone — the **defense** is a gate, not a bonus.

| Dimension | Fail | Pass | Strong |
|---|---|---|---|
| **Correctness** | Methods misbehave or error paths unhandled | All specified behaviour works; errors raised deliberately | Edge cases handled cleanly, no dead code |
| **Typing** | `mypy --strict` errors, or types missing | Passes strict with honest annotations | Types express intent (no `Any` escape hatches) |
| **Tests** | Missing methods or error paths untested | Every method + error path + isolation tested | Tests are behaviour-focused and would survive a refactor |
| **Structure** | Logic tangled with I/O; unclear modules | Clean separation; sensible module boundaries | Structure makes the next week's change obvious |
| **Hygiene** | `ruff` fails; junk committed | Lint + format clean; sensible commits | Small, verified commits telling a story |
| **Defense** | Can't explain choices | Explains *what* and *why* | Explains trade-offs and what breaks at 100× load |

**Pass bar:** Pass or better in every row, *including Defense*. A green suite with no defensible reasoning is not a pass — that's the rule that separates this from a checklist bootcamp.

---

## What "done to house standard" demonstrates

Point learners at these as the habits every week must show:
- **Types from line one.** `mypy --strict` is on; there is no "add types later."
- **Every path tested, including failures.** Error paths and owner isolation are tested, not assumed.
- **Logic is pure.** Zero I/O in `src/` — which is *why* the tests need no mocks. That purity is the seed of the Week 11 architecture.
- **One config file.** deps, lint, types, and tests all live in `pyproject.toml`.
- **CI-ready from day one.** The workflow runs the exact local loop, so "works on my machine" and "passes CI" are the same thing.

---

## How the CI evolves in Week 7

The workflow here runs lint + format + types + unit tests — everything Week 1–2 code needs. In **Week 7**, once there's a Postgres-backed repository and integration tests, the pipeline gains a real database and a coverage gate. The `quality` job stays; a second job is added:

```yaml
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: dev
          POSTGRES_DB: fieldbook_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      DATABASE_URL: postgresql://postgres:dev@localhost:5432/fieldbook_test
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          python-version: "3.13"
      - run: uv sync --dev
      - run: uv run alembic upgrade head          # apply migrations to the test DB
      - run: uv run pytest --cov=fieldbook --cov-fail-under=80
```

(The course teaches `testcontainers` as the alternative that runs the *same* ephemeral Postgres locally and in CI — the services block above is the simpler GitHub-native version. Either is fine; testcontainers wins when you want identical behaviour on a laptop.)

That's the whole point of starting CI-ready now: Week 7 is an **addition** to this file, not a rewrite. Same as the code — the foundation is built so the next thing bolts on.
