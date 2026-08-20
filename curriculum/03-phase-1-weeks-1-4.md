# Backend Bootcamp — Phase 1: Foundations to Your First API
## Weeks 1–4 · Detailed Lesson Plans

This is the executable workbook. Each week follows the same rhythm:
**Objectives → Setup → Read → Understand → Build → Done when.**

Read the "Read" section *before* you build. Do the "Build" section by writing code, not by reading about code. A week isn't finished until every box in "Done when" is checked.

**The project:** you're building **Fieldbook**, a multi-user task/records service. It starts this phase as a plain Python library and ends as a real HTTP API. Same repo grows all 16 weeks.

**Stack pinned this phase:** Python 3.13, uv, Ruff, mypy, pytest, FastAPI, Pydantic v2.
**Weekly load:** ~20–25 hrs. Rough splits are given per week.

---

# Week 1 — Backend Programming Foundations

**Goal:** Write clean, modular, typed, testable Python. Build Fieldbook's core logic as a pure in-memory library — no web, no database yet.

### Objectives
- Structure a Python project into modules with clear separation of concerns
- Use type hints everywhere and pass `mypy --strict`
- Handle errors deliberately with exceptions instead of return codes or silent failures
- Choose the right core data structure (dict vs list vs set) and know why

### Setup (do this once, ~2 hrs)
Install uv (the one tool that manages Python versions, envs, and deps), then:

```bash
uv python install 3.13
uv init fieldbook && cd fieldbook
uv add --dev pytest ruff mypy pytest-cov
git init && git add -A && git commit -m "chore: project init"
```

Create `pyproject.toml` config so the toolchain is strict from line one:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]   # errors, pyflakes, import-sort, pyupgrade, bugbear

[tool.mypy]
strict = true

[tool.pytest.ini_options]
addopts = "-q"
```

Verify the loop works: `uv run ruff check .` · `uv run mypy .` · `uv run pytest`.

### Read (~5 hrs)
- **Python official tutorial** (docs.python.org) — Modules, Packages, and Errors and Exceptions sections. *Focus on:* how a package is laid out, and `raise`/`try`/`except`/custom exception classes.
- **mypy docs** (mypy.readthedocs.io) — "Getting started" + "Type hints cheat sheet." *Focus on:* annotating functions, `Optional`, `list[X]`/`dict[K, V]`, and what `--strict` actually enforces.
- **Real Python** (free articles) — search "Python dataclasses" and "Python type checking." *Focus on:* when a `@dataclass` beats a bare dict, and why typing catches bugs early.
- **Reference, skim now:** Python `dataclasses` and `enum` stdlib docs.

### Understand (concepts to be able to explain, not just use)
- **Separation of concerns:** business logic must not know about I/O. Your Fieldbook logic this week has zero `print`, zero file access, zero network — it just manipulates data.
- **Data structure choice:** you'll store records keyed by ID. That's a `dict[str, Record]` lookup (O(1)), not a list you scan (O(n)). Be able to say why.
- **Exceptions as control flow:** a "record not found" is an exceptional case → raise a custom `RecordNotFoundError`, don't return `None` and hope the caller checks.

### Build — Fieldbook core library (~12 hrs)
Create this structure:

```
fieldbook/
  src/fieldbook/
    __init__.py
    models.py        # the Record dataclass + any enums
    errors.py        # custom exceptions
    repository.py    # in-memory store: create/get/list/update/delete
  tests/             # (you'll fill this next week)
```

Requirements:
1. **`models.py`** — a `Record` dataclass with: `id: str`, `title: str`, `status` (an `Enum`: `todo`/`doing`/`done`), `owner_id: str`, `created_at: datetime`. Fully typed.
2. **`errors.py`** — `RecordNotFoundError` and `ValidationError`, both subclassing a base `FieldbookError`.
3. **`repository.py`** — an `InMemoryRecordRepository` class holding a `dict[str, Record]`, with methods:
   - `create(title, owner_id) -> Record` (generates a `uuid4` id and `created_at`, defaults status to `todo`)
   - `get(record_id) -> Record` (raises `RecordNotFoundError` if missing)
   - `list(owner_id) -> list[Record]` (only that owner's records)
   - `update(record_id, **changes) -> Record`
   - `delete(record_id) -> None`
4. Everything passes `uv run mypy .` in strict mode and `uv run ruff check .`.

**Directions:** write the smallest method first (`create`), run mypy after each method, commit after each passing method. Don't write all five then debug — build the muscle of small, verified increments now.

### Done when
- [ ] `uv run mypy .` passes strict, `uv run ruff check .` is clean
- [ ] All five repository methods work when driven from a throwaway `scratch.py`
- [ ] `get`/`update`/`delete` on a missing id raise `RecordNotFoundError`
- [ ] No I/O anywhere in `src/` — logic is pure
- [ ] Committed to git with sensible messages

---

# Week 2 — Testing & TDD

**Goal:** Put a real test suite around Week 1's library, driven test-first. From now on, untested code is unfinished code.

### Objectives
- Write unit tests with pytest and organize them with fixtures
- Practice the TDD loop: red → green → refactor
- Understand the test pyramid and where today's tests sit in it
- Read a coverage report as a signal (not a target to game)

### Read (~4 hrs)
- **pytest docs** (docs.pytest.org) — "Get Started" + "How to use fixtures." *Focus on:* the `assert` style, `@pytest.fixture`, and fixture scope.
- **Real Python** — "Effective Python Testing With pytest." *Focus on:* structuring a test file, parametrizing, and fixtures for setup.
- **Short read on TDD** — search "TDD red green refactor." *Focus on:* the loop and *why* writing the test first shapes better interfaces.
- **Skim:** the "test pyramid" concept (Martin Fowler's article). *Focus on:* why there are many unit tests and few end-to-end ones.

### Understand
- **The pyramid:** lots of fast unit tests at the base, fewer integration tests, very few slow e2e tests at the top. This week is all base.
- **Arrange–Act–Assert:** every test sets up state, does one thing, asserts one outcome. Be strict about it.
- **When NOT to mock:** you have no external dependencies yet (pure in-memory logic), so you should be writing *zero* mocks this week. If you reach for a mock, ask why. (Mocking comes later, when there's a database or network to isolate.)

### Build — TDD the library (~13 hrs)
1. Set up `tests/` with a `conftest.py` exposing a `repo` fixture that returns a fresh `InMemoryRecordRepository`.
2. **Rewrite this week test-first.** For each behavior, write the failing test, then make it pass:
   - creating a record returns one with a generated id, `todo` status, and a `created_at`
   - `get` returns the created record
   - `get` on unknown id raises `RecordNotFoundError`
   - `list` returns only the requesting owner's records (create records for two owners to prove isolation)
   - `update` changes fields and returns the updated record
   - `update`/`delete` on unknown id raise `RecordNotFoundError`
3. Add coverage: `uv run pytest --cov=fieldbook`. Aim to understand any line that *isn't* covered — don't just chase a number.
4. **Plant-a-bug drill:** deliberately break one method (e.g. make `list` ignore `owner_id`). Confirm a test goes red. Revert. This proves your suite has teeth.

**Directions:** genuinely write the test before the implementation for at least three of these. It'll feel slow and backwards. Do it anyway — the point is to feel how test-first pressure produces cleaner method signatures.

### Done when
- [ ] Every repository method has at least one test; error paths are tested
- [ ] Owner-isolation is proven by a test with two owners
- [ ] The plant-a-bug drill made a test fail, then you reverted
- [ ] `uv run pytest` is green; you can explain any uncovered line
- [ ] mypy + ruff still clean; committed

---

# Week 3 — HTTP & Your First API

**Goal:** Wrap the library in an HTTP layer. Fieldbook becomes a real REST API serving JSON — with correct methods and status codes.

### Objectives
- Explain precisely what happens in an HTTP request/response
- Map CRUD operations to the correct HTTP methods and status codes
- Serve JSON from FastAPI and test endpoints with `TestClient`
- Keep the web layer thin — it calls the library, it doesn't contain logic

### Setup
```bash
uv add fastapi "uvicorn[standard]" httpx
```
(`httpx` powers FastAPI's `TestClient`.)

### Read (~5 hrs)
- **MDN HTTP** (developer.mozilla.org) — "An overview of HTTP," "HTTP request methods," "HTTP response status codes." *Focus on:* GET/POST/PUT/PATCH/DELETE semantics, and the 2xx/4xx/5xx families — especially 200 vs 201 vs 204, and 400 vs 404 vs 422 vs 500.
- **FastAPI docs** (fastapi.tiangolo.com) — Tutorial: "First Steps," "Path Parameters," "Query Parameters," "Request Body." *Focus on:* defining routes, reading path/query/body, and returning data.
- **Short read on REST** — search "REST constraints" (statelessness, uniform interface). *Focus on:* why REST is a set of constraints, not just "an API that returns JSON."

### Understand
- **Method semantics:** GET is safe and idempotent (no side effects). PUT/DELETE are idempotent (calling twice = calling once). POST is neither. Your routes must respect this.
- **Status codes are a contract:** create → 201, successful delete → 204 (no body), not-found → 404, malformed input → 422/400. Returning 200 for everything is a code smell.
- **Statelessness:** the server keeps no per-client session in memory between requests; everything needed is in the request. (This is *why* backends scale horizontally later.)
- **Thin controllers:** the endpoint function should translate HTTP ↔ library call. Business logic stays in `repository.py`.

### Build — the HTTP layer (~12 hrs)
Add:
```
src/fieldbook/
  api.py           # FastAPI app + routes
  main.py          # uvicorn entrypoint: `app` lives here or is imported
```

Expose these endpoints, wired to the repository:

| Method | Path | Success code | Behavior |
|---|---|---|---|
| POST | `/records` | 201 | create a record |
| GET | `/records` | 200 | list caller's records |
| GET | `/records/{id}` | 200 | fetch one |
| PATCH | `/records/{id}` | 200 | update fields |
| DELETE | `/records/{id}` | 204 | delete, empty body |

Requirements:
1. Map `RecordNotFoundError` → HTTP 404 (use a FastAPI exception handler, not a try/except in every route).
2. For now, take `owner_id` as a query param or header — real auth is Week 8. Keep it explicit so owner-isolation still works.
3. Run it: `uv run uvicorn fieldbook.main:app --reload`, hit it from the interactive `/docs` page FastAPI generates, and with `curl`.
4. **Tests:** use FastAPI's `TestClient` to test each endpoint — assert both the JSON body *and* the status code. Wrong-method and not-found cases included.

**Directions:** build one endpoint end-to-end (route → test → curl) before moving to the next. Notice that your routes are nearly empty — that's correct. If logic is creeping into `api.py`, push it back down into the library.

### Done when
- [ ] All five endpoints work, verified in `/docs` and by tests
- [ ] Status codes are correct (201 create, 204 delete, 404 missing)
- [ ] `RecordNotFoundError` is handled centrally, not per-route
- [ ] Owner isolation still holds through the API
- [ ] `TestClient` tests assert status + body; mypy + ruff clean; committed

---

# Week 4 — API Design & Validation

**Goal:** Turn a working API into a *well-designed* one — validated input, consistent errors, pagination, and generated docs a stranger could consume cold.

### Objectives
- Model requests and responses with Pydantic v2 schemas
- Validate and reject bad input with clear, machine-readable errors
- Add pagination, and a consistent error envelope across all endpoints
- Produce an OpenAPI spec and treat docs as a deliverable

### Read (~5 hrs)
- **Pydantic v2 docs** (docs.pydantic.dev) — "Models," "Fields," "Validators." *Focus on:* declaring schemas, field constraints (`min_length`, etc.), and how validation errors are raised.
- **FastAPI docs** — "Request Body," "Response Model," "Handling Errors," "Query Parameters" (for pagination). *Focus on:* separate input vs output models, `response_model`, and customizing error responses.
- **Skim:** the OpenAPI concept and API versioning strategies (URL vs header). *Focus on:* why a spec matters and how you'd introduce `/v2` without breaking `/v1`.

### Understand
- **Input ≠ output models:** the shape a client *sends* (no id, no timestamps) differs from what you *return* (full record). Model them separately — `RecordCreate` vs `RecordOut`. Never accept fields you don't trust (e.g. a client shouldn't set `id` or `owner_id` on itself).
- **Validation at the edge:** bad data is rejected at the boundary with a 422 and a clear message, before it ever reaches your logic.
- **Consistent error envelope:** every error response has the same JSON shape (`{"error": {"code": ..., "message": ...}}`), so a consumer can handle failures uniformly.
- **Pagination is not optional:** an unbounded `list` endpoint is a production incident waiting to happen. Add `limit`/`offset` with sane defaults and a cap.

### Build — design pass (~12 hrs)
1. **Schemas** (`schemas.py`): `RecordCreate` (title, with `min_length=1`), `RecordUpdate` (all fields optional), `RecordOut` (full record). Wire endpoints to use them via `response_model`.
2. **Validation:** reject empty titles, over-length titles, and unknown status values with 422s. Confirm the auto-generated messages are useful.
3. **Error envelope:** add an exception handler that renders *all* errors (404, 422, 500) in one consistent JSON shape. Update the 404 handler from Week 3 to match.
4. **Pagination:** `GET /records?limit=&offset=` with defaults (e.g. limit 20, max 100) and return enough for a client to page (at minimum the items; ideally a small envelope with `total`).
5. **Docs:** confirm `/docs` and the raw OpenAPI JSON (`/openapi.json`) reflect all of this. Write a short `README` section: base URL, auth note, and one example request/response per endpoint.
6. **Integration proof:** hand your running API + README to another person (or your future self after a day away) and integrate against it cold, using only the docs. Every point of confusion is a design bug — fix it.

### Done when
- [ ] Separate Create/Update/Out schemas; clients can't set `id`/`owner_id`
- [ ] Invalid input returns 422 with a clear message
- [ ] All errors share one JSON envelope shape
- [ ] `list` is paginated with a default and a hard cap
- [ ] `/openapi.json` is complete; README lets someone integrate cold
- [ ] Full test suite green; mypy + ruff clean; committed and tagged `phase-1-complete`

---

## End of Phase 1 — where you stand

You now have a tested, typed, validated, documented REST API running locally, built on clean separation between web and logic. That's a real backend service — it just lives in memory and trusts the caller's identity. **Phase 2 (Weeks 5–7)** makes it durable and trustworthy: PostgreSQL, SQL, migrations, then integration tests against a real database running in CI.

### Habits to carry forward (non-negotiable)
- Type hints + `mypy --strict` on every commit — never "I'll add types later."
- No code merges without a passing test.
- Small verified increments: build one thing, test it, commit, repeat.
- Logic stays out of the web layer.

### If you get stuck
Use an AI tutor or docs to get *unstuck on a concept*, not to write the implementation for you. The portfolio value — and the actual learning — is in code you can explain and defend. A solution you can't explain is worse than a blank file.
