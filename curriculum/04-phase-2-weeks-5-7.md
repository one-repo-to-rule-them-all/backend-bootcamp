# Backend Bootcamp — Phase 2: Durable & Trustworthy
## Weeks 5–7 · Detailed Lesson Plans

Same rhythm as Phase 1: **Objectives → Setup → Read → Understand → Build → Done when.** Read before you build; build by writing code; a week isn't done until every box checks.

**Where you left off:** Fieldbook is a tested, validated REST API — but it stores everything in memory and forgets it all on restart. This phase makes it real: a PostgreSQL database, hand-written SQL, versioned migrations, and integration tests that run against a real database in CI.

**The seam that makes this clean:** in Week 5 you'll define a `RecordRepository` *Protocol* (an interface). Your Week 1 in-memory store, this phase's raw-SQL store, and Week 6's ORM store all satisfy it, and the API depends on the interface — not any one implementation. That's why swapping storage barely touches the web layer, and it's the groundwork for the architecture refactor in Phase 3.

**Stack added this phase:** PostgreSQL, `psycopg` 3, SQLAlchemy 2.0, Alembic, testcontainers, GitHub Actions.
**Weekly load:** ~20–25 hrs.

**You'll need Docker** from here on (to run Postgres locally and in tests). Install Docker Desktop / Engine now if you haven't. Week 12 formalizes containerizing *your app*; for now you just need it to run a database.

---

# Week 5 — Relational Databases & SQL

**Goal:** Model Fieldbook's data relationally and write real SQL by hand. Back the repository with Postgres using the raw driver — no ORM yet. Feel the SQL before anything abstracts it away.

### Objectives
- Design a normalized relational schema with keys, constraints, and referential integrity
- Write non-trivial SQL directly: joins, aggregates, `INSERT`/`UPDATE`/`DELETE`
- Query Postgres from Python safely with parameterized queries (and understand the injection you're preventing)
- Reason about indexes: what they speed up and what they cost

### Setup (~1.5 hrs)
Run Postgres in a container and add the driver:
```bash
docker run --name fieldbook-db -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=fieldbook -p 5432:5432 -d postgres:16
uv add "psycopg[binary]"
```
Connect with `psql` (or any client) to poke around:
`docker exec -it fieldbook-db psql -U postgres -d fieldbook`

### Read (~5 hrs)
- **PostgreSQL tutorial** (postgresql.org/docs → "Tutorial," or postgresqltutorial.com). *Focus on:* `CREATE TABLE`, data types, `PRIMARY KEY`/`FOREIGN KEY`/`NOT NULL`/`CHECK`, and the four DML verbs.
- **SQLBolt** (sqlbolt.com) — interactive lessons 1–12. *Focus on:* `SELECT` with `WHERE`, multi-table `JOIN`s, and `GROUP BY` aggregates. Actually type them.
- **"Use The Index, Luke"** (use-the-index-luke.com) — "Preface" + "Anatomy of an Index" + "The Where Clause" (start). *Focus on:* why an index turns a scan into a lookup, and that every index taxes writes.
- **psycopg 3 docs** (psycopg.org) — "Basic usage." *Focus on:* `connect`, `execute` with `%s` placeholders, and `fetchone`/`fetchall`. **The placeholder part is critical — never build SQL with f-strings.**

### Understand
- **Normalization:** owner identity lives in a `users` table; a record *references* an owner by foreign key rather than duplicating the owner's name on every row. Be able to explain why duplication is a bug waiting to happen.
- **Referential integrity:** a `records.owner_id` FK means the database itself refuses to create a record for a non-existent user. Constraints are correctness you get for free.
- **Transactions & ACID:** a transaction is all-or-nothing. If a multi-step write fails halfway, it rolls back. Know what the A, C, I, D each buy you.
- **Indexes:** an index on `records(owner_id)` makes "list this owner's records" fast, at the cost of slower writes and more storage. `EXPLAIN` shows you which path the planner takes.
- **Parameterized queries:** `%s` placeholders send data separately from the SQL text, so a malicious `title` can't become executable SQL. This *is* SQL-injection prevention — understand the attack you're defeating.

### Build — schema + raw-SQL repository (~13 hrs)
1. **Schema** (`db/schema.sql`, hand-written): a `users` table (`id` uuid PK, `name`, `created_at`) and a `records` table (`id` uuid PK, `title`, `status`, `owner_id` uuid FK → users, `created_at`). Add a `CHECK` constraint restricting `status` to the three valid values, and an index on `records(owner_id)`. Apply it with `psql`.
2. **The Protocol** (`repository.py`): define
   ```python
   from typing import Protocol
   class RecordRepository(Protocol):
       def create(self, title: str, owner_id: str) -> Record: ...
       def get(self, record_id: str) -> Record: ...
       def list(self, owner_id: str, limit: int, offset: int) -> list[Record]: ...
       def update(self, record_id: str, **changes: object) -> Record: ...
       def delete(self, record_id: str) -> None: ...
   ```
   Make your existing `InMemoryRecordRepository` conform (it basically already does).
3. **`PostgresRecordRepository`** implementing that Protocol with psycopg and **parameterized** SQL for every method. Raise `RecordNotFoundError` when a row is missing.
4. **Wire it into the API** by swapping which repository the app constructs. The route code should not change — if it does, your Phase 1 separation wasn't clean; fix that, don't work around it.
5. **SQL challenge (do these in `psql`, by hand):**
   - list all records with their owner's *name* (a JOIN)
   - count records per owner (`GROUP BY`)
   - run `EXPLAIN` on the list-by-owner query **before and after** creating the index; read both plans.

**Directions:** write the schema and one query in `psql` first, confirm it returns what you expect, *then* translate it into the repository method. SQL-first, Python-second.

### Done when
- [ ] `schema.sql` creates both tables with FK, `CHECK`, and the owner index
- [ ] `PostgresRecordRepository` satisfies the `RecordRepository` Protocol
- [ ] Every query is parameterized — zero f-string/`.format` SQL anywhere
- [ ] The API works unchanged against Postgres; data survives a restart
- [ ] You can show `EXPLAIN` before/after the index and explain the write-time cost
- [ ] mypy + ruff clean; committed

---

# Week 6 — Persistence Patterns & Data Access

**Goal:** Introduce SQLAlchemy 2.0 and Alembic — *after* you've written raw SQL, so the ORM is a understood convenience, not magic. Reproduce and fix an N+1. Get a real migration workflow.

### Objectives
- Model the schema with SQLAlchemy 2.0 declarative ORM and query with `select()`
- Manage schema evolution with Alembic migrations (upgrade *and* downgrade)
- Diagnose and fix the N+1 query problem
- Articulate when you'd reach past the ORM for raw SQL

### Setup
```bash
uv add sqlalchemy alembic
uv run alembic init db/migrations
```

### Read (~5 hrs)
- **SQLAlchemy 2.0 docs** (docs.sqlalchemy.org) — "ORM Quick Start" and "Relationship Loading Techniques" (at least skim the second). *Focus on:* declarative `Mapped[]` models, the `Session`, `select()`, and lazy vs eager (`selectinload`, `joinedload`) loading.
- **Alembic docs** (alembic.sqlalchemy.org) — the tutorial through "Auto Generating Migrations." *Focus on:* configuring the target metadata, autogenerating a migration, and *reviewing it before applying* — autogenerate is a draft, not gospel.
- **N+1 problem** — search "SQLAlchemy N+1 selectinload." *Focus on:* why iterating a relationship fires one query per parent row, and how eager loading collapses it.
- **Skim:** a document-vs-relational primer and CAP theorem at a working level. *Focus on:* what a document store is good at and the consistency/availability trade-off — no implementation needed.

### Understand
- **ORM vs Core vs raw — trade-offs, not tribes:** the ORM shines for CRUD on domain objects; hand-written SQL (or SQLAlchemy Core) wins for complex analytical or bulk queries. You can now judge because you've done both.
- **Migrations are the only way schema changes:** never hand-edit a database that isn't a scratch toy. Every change is a reviewed, versioned, reversible migration. A migration without a working `downgrade` is half a migration.
- **Connection pooling:** SQLAlchemy hands out connections from a managed pool; opening a fresh connection per request would be needless overhead. Know that the pool exists and why.
- **N+1:** the single most common ORM performance trap — convenient relationship access quietly generating a query per row.

### Build — ORM + migrations (~13 hrs)
1. **Models** (`db/models.py`): `User` and `Record` as SQLAlchemy declarative models mirroring Week 5's schema, with a relationship (`User.records` ↔ `Record.owner`).
2. **Alembic:** point it at your models' metadata, **autogenerate** the initial migration, then **diff it against your hand-written `schema.sql`** — they should describe the same tables. That comparison is the lesson: you now see what the ORM generates. Apply it to a fresh database.
3. **`SQLAlchemyRecordRepository`** conforming to the same Protocol. You now have three implementations; keep them all — they're your trade-off teaching set.
4. **N+1 drill:** build a "list records with their owner's name" feature the naive way (access `record.owner.name` in a loop). Turn on `echo=True` and count the queries. Then fix it with `selectinload`/`joinedload` and count again. **Record both numbers.**
5. **Migration workflow drill:** add a nullable `description` column to `Record` via a *new* autogenerated migration. Apply it (`upgrade`), then roll it back (`downgrade`), then re-apply. Prove the round trip works.

### Done when
- [ ] ORM models match the Week 5 schema; initial Alembic migration applies cleanly
- [ ] You diffed the autogenerated migration against your hand-written DDL and understood the differences
- [ ] A second migration adds a column with a working `upgrade` **and** `downgrade`
- [ ] `SQLAlchemyRecordRepository` satisfies the Protocol and passes existing behavior tests
- [ ] The N+1 is reproduced (query count shown) and fixed (count dropped) — both numbers recorded
- [ ] You can name one query you'd still write as raw SQL, and why
- [ ] mypy + ruff clean; committed

---

# Week 7 — Integration Testing & CI

**Goal:** Test the system against a *real* database, isolated per run, and automate the whole pipeline. This is where "no merge without green CI" turns on — permanently.

### Objectives
- Write integration tests against a real ephemeral Postgres, with per-test isolation
- Stand up a GitHub Actions pipeline running lint, types, and tests on every PR
- Enforce a coverage gate and branch protection
- Understand and prevent flaky tests

### Setup
```bash
uv add --dev testcontainers pytest-randomly
```
(`testcontainers` spins up a throwaway Postgres for tests — same behavior locally and in CI. `pytest-randomly` shuffles test order to expose hidden coupling.)

### Read (~4.5 hrs)
- **pytest docs** (docs.pytest.org) — "How to use fixtures," especially **fixture scope** and yield fixtures. *Focus on:* a session-scoped fixture (start the DB once) plus a function-scoped fixture (wrap each test in a transaction that rolls back).
- **testcontainers-python docs** — the Postgres module. *Focus on:* starting the container and getting a connection URL from it.
- **GitHub Actions docs** (docs.github.com/actions) — "Understanding GitHub Actions" + workflow syntax. *Focus on:* triggering on `pull_request`, defining steps, and caching dependencies.
- **Flaky tests** — search "how to fix flaky tests." *Focus on:* isolation, order-independence, and never sharing mutable state between tests.
- **Skim:** what contract testing is and when you'd want it (relevant once there are multiple services).

### Understand
- **Why integration tests earn their slowness:** they exercise your real SQL, your migrations, and your repository together. They catch a whole class of bugs — bad SQL, migration drift, wrong constraints — that mocked unit tests structurally cannot.
- **Isolation is the whole game:** each test must pass regardless of what ran before it or in what order. The clean pattern: migrate once per session, then run each test inside a transaction that's rolled back at the end. Fast and pristine.
- **Flaky tests are worse than no tests:** a suite that fails randomly gets ignored, and an ignored suite gates nothing. `pytest-randomly` surfaces order-dependence before it rots your trust.
- **CI is the objective arbiter of "done":** not "works on my machine." Branch protection makes the green check *required* to merge, which is what makes the rule real instead of aspirational.

### Build — integration suite + pipeline (~14 hrs)
1. **DB fixtures** (`tests/conftest.py`): a session-scoped fixture that starts a Postgres testcontainer and runs your Alembic migrations against it; a function-scoped fixture that opens a transaction per test and rolls it back after. Every integration test gets a clean database.
2. **Repository integration tests:** run the `SQLAlchemyRecordRepository` behavior suite (create/get/list/update/delete, owner isolation, not-found) against the *real* container database.
3. **API integration tests:** `TestClient` hitting the endpoints backed by the real DB — end to end, HTTP in, rows out.
4. **GitHub Actions** (`.github/workflows/ci.yml`): on `pull_request` and pushes to `main`, run: checkout → install uv → `uv sync` → `uv run ruff check .` → `uv run mypy .` → `uv run pytest --cov=fieldbook`. Fail the build if coverage drops below a threshold you set (start realistic, e.g. 80%).
5. **Prove isolation:** run `uv run pytest` a few times — `pytest-randomly` reshuffles order each run. If a shuffle ever fails, you have hidden coupling; fix it.
6. **Break-the-build drill:** open a PR that breaks a test (or violates a lint rule). Watch CI go red and block the merge. Fix it, watch it go green, merge.
7. **Branch protection:** enable "require status checks to pass before merging" on `main` in the repo settings. Note in your README that CI is a required gate.

### Done when
- [ ] Integration tests run against a real ephemeral Postgres with migrations applied
- [ ] Each test is isolated (transaction rollback); the suite passes under `pytest-randomly` shuffling
- [ ] API-level integration tests pass through the real database
- [ ] GitHub Actions runs ruff + mypy + pytest/coverage on every PR
- [ ] The coverage gate fails the build below threshold (you verified by dropping below it once)
- [ ] Break-the-build drill: CI caught the break and blocked merge, then you fixed it
- [ ] Branch protection is enabled; committed and tagged `phase-2-complete`

---

## End of Phase 2 — where you stand

Fieldbook is now **durable** (PostgreSQL), **evolvable** (Alembic migrations with working rollbacks), and **trustworthy** (real integration tests gating every merge in CI). You've also written the same storage layer three ways — in-memory, raw SQL, ORM — which means you can actually defend a persistence choice instead of reaching for the default.

**Phase 3 (Weeks 8–11)** gives it identity and shape: real authentication and role-based authorization (finally retiring that `owner_id` query-param placeholder), background jobs and webhooks for work that shouldn't block a request, caching with *measured* performance wins, and a clean architectural refactor (hexagonal / ports-and-adapters) — which is exactly where the `RecordRepository` Protocol you built this phase pays off.

### Habits reinforced this phase
- Schema changes only ever happen through reviewed, reversible migrations.
- SQL-first, ORM-second — feel the primitive before the abstraction.
- Integration tests hit the real thing; isolation and order-independence are non-negotiable.
- Green CI is required to merge. No exceptions, starting now.
