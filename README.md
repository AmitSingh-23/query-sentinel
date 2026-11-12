# QuerySentinel

**A privacy-aware optimizer for PostgreSQL queries.** It tells a DBA why a query is slow and how to fix it, without sending customer data or real schema names to an AI model.

Finalist, Code Utsava X.0 (NIT Raipur) · Built by [Amit Singh Bisht](https://github.com/AmitSingh-23)

[![Tests](https://github.com/AmitSingh-23/query-sentinel/actions/workflows/tests.yml/badge.svg)](https://github.com/AmitSingh-23/query-sentinel/actions/workflows/tests.yml)

![QuerySentinel pipeline run](db-opt-platform/docs/screenshots/pipeline_run.png)

## Quick start

```bash
git clone https://github.com/AmitSingh-23/query-sentinel.git
cd query-sentinel/db-opt-platform
cp .env.example .env          # set the passwords
docker compose up --build
```

- API health check: `http://localhost:8000/api/v1/health`
- Dashboard: `http://localhost:8501`

The application lives in [`db-opt-platform/`](db-opt-platform/); every command in the documentation is run from there.

## The problem

Slow queries are usually diagnosed by pasting SQL and `EXPLAIN` output into a chat assistant. For a company database that means sending table names, column names and literal values (emails, tenant IDs, amounts) to a third party. QuerySentinel keeps the diagnosis and removes the leak.

## How it works

| Step | What happens | Where |
| --- | --- | --- |
| 1. Mask | Literals become `$1, $2, …` from the SQL parse tree, and table and column names become HMAC-SHA256 pseudonyms. A guard blocks any outgoing AI payload that still contains a raw value. | `app/masking_vault.py`, `app/llm_guard.py` |
| 2. Diagnose | `EXPLAIN (FORMAT JSON)` runs in a read-only transaction. The plan tree is scored by a small graph neural network, with deterministic rules as the fallback. | `app/plan_parser.py`, `app/gnn/` |
| 3. Propose | LangGraph agents suggest indexes, SQL rewrites and partitioning. A tabular Q-learning policy ranks the candidates. | `app/agents/`, `app/rl/` |
| 4. Test | Each index is simulated with HypoPG hypothetical indexes, and its write and storage cost is estimated, before it is recommended. | `app/sandbox.py`, `app/blast_radius.py` |
| 5. Hand over | The output is a migration script with a rollback. Nothing is applied automatically. | `app/migration_generator.py` |

| Privacy masking | Plan analysis | HypoPG simulation |
| --- | --- | --- |
| ![Privacy view](db-opt-platform/docs/screenshots/privacy.png) | ![Plan and GNN view](db-opt-platform/docs/screenshots/plan_gnn.png) | ![HypoPG view](db-opt-platform/docs/screenshots/hypopg.png) |

## Results

Measured on PostgreSQL 16 with HypoPG, on a 1M-order, 3M-item demo dataset. These are **planner cost estimates** unless marked measured.

| Scenario | Fix proposed | Planner cost | Measured runtime |
| --- | --- | --- | --- |
| Join with sequential scan | Two indexes | −72.8 % | not measured |
| Weekly report | Composite index | −21.3 % | 57.3 ms → 30.0 ms |
| Correlated subquery | FK index + join rewrite | −99.98 % | not run (baseline too slow) |
| Cast on an indexed column | Index + range rewrite | −99.9 % | 44.3 ms → 0.009 ms |

Full table and method: [section 24 of the detailed README](db-opt-platform/README.md#24-verified-results-in-the-build-environment).

## Tests

```bash
cd db-opt-platform
pip install -r requirements.txt
pytest -q -m "not integration"     # 211 pass, 15 skip without a database
```

The offline suite runs in GitHub Actions on every push. Tests that need a live PostgreSQL 16 + HypoPG database run when one is reachable, for example under `docker compose`.

## Limitations

This is a hackathon prototype for decision support, not a production tool.

- **Planner estimates are not runtime.** Only the rows marked measured were timed.
- **The GNN is trained on synthetic plans.** It scores 100 % on held-out synthetic plans and 70.8 % on plan shapes it has not seen. It has not been evaluated on a labelled set of real plans.
- **The RL workload is small:** 15 query templates on one demo schema.
- **The LLM integration is tested with a mocked provider only.** No real LLM call is part of the test suite.
- **Docker images were not built in the original build environment** (the registry was blocked); `docker compose config` validates.
- **PII detection is pattern-based.** Literal masking does not depend on it, since every literal is removed.

The complete list is in [section 25](db-opt-platform/README.md#25-limitations).

## Documentation

- [Detailed README](db-opt-platform/README.md): architecture, privacy and security design, API, benchmarks
- [Architecture](db-opt-platform/docs/architecture.md)
- [Security model](db-opt-platform/docs/security.md)
- [API reference](db-opt-platform/docs/api.md)

## Stack

Python · FastAPI · PostgreSQL 16 · HypoPG · pglast · LangGraph · PyTorch Geometric · Streamlit · Docker
