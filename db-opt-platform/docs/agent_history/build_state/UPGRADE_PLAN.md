# UPGRADE_PLAN (Final Upgrade Master Prompt, P0 output)

Principle: additive. Existing endpoints, tests, init scripts and demo flows stay unchanged.
All new DB access goes through the DataSource resolver (`app/datasource.py`), which hands out a `Database`
+ `PostgresInstrumentation` pair per source. The existing `Services`/`Pipeline` already accept those by
injection, so the optimizer is reused, never duplicated.

## New files
| File | Phase | Purpose |
|---|---|---|
| app/provenance.py | P1 | typed provenance tags (Section 7) + `tagged()` helper |
| app/feature_flags.py | P1 | read QS_FEATURE_* flags, report for /upgrade/status |
| app/migrations/qs_meta.sql + app/meta_migration.py | P1 | idempotent additive migration (schemas qs_meta, qs_dynamic, role qs_nlq_reader) run as admin after existing init |
| app/datasource.py | P1 | `DataSourceResolver`, `DataSourceContext`, error codes |
| app/structured_log.py | P1 | trace-id + data_source_id logging helper |
| app/dataset_ingestion.py | P2 | CSV/JSON dataset profiling, type inference, identifier normalisation, preview/commit, additive evolution |
| app/schema_verifier.py | P3 | strict BYOD DDL verifier (pglast) |
| app/sandbox_manager.py | P3 | sandbox-pg provisioning, quotas, TTL reaper, orphan sweep, ownership |
| app/synthetic_data.py | P3 | FK-ordered synthetic rows at SMALL/MEDIUM/LARGE |
| app/sql_safety.py | P4 | 10-stage SQL safety gate (reuses SecurityGateway for stages 1-4) |
| app/nlq.py | P4/P5 | schema context builder, privacy choke point `release_aggregate`, LLM + deterministic fallback generator, repair loop, executor, answer |
| app/index_portfolio.py | P7 | portfolio actions, redundancy, consolidation, pruning evidence, review DDL |
| app/gnn/gat_model.py | P8 | GATv2 (PyG GATv2Conv, edge_dim) + attention extraction, versioned checkpoints |
| app/rl/curriculum.py, app/rl/replay.py | P9 | curriculum levels from parsed SQL, bounded PER buffer |
| app/dp.py | P10 | Laplace mechanism, budget accountant |
| app/api_upgrade.py | P13 | new routers (sources, data, sandboxes, byod, nlq, upgrade/status) |
| dashboard/upgrade_ui.py | P13 | data-source selector, upload flows, Ask Your Database |
| docker/sandbox/Dockerfile | P14 | PG16 + HypoPG, no init scripts |
| tests/test_upgrade_*.py | all | new tests per phase |

## Files changed (additively)
| File | Change | Risk |
|---|---|---|
| app/config.py | new settings with defaults | low |
| app/db.py | `Database(settings, dsn_kwargs=None, server_settings=None)` optional | low |
| app/postgres_instrumentation.py | optional `schema` (default 'public') | low (SQL constants keep behaviour for public) |
| app/schema_inspector.py | optional cache + invalidate | low |
| app/recommendation_mapper.py, app/migration_generator.py | optional schema (default public) | low |
| app/sql_semantic_diff.py | add `risk_screen()` | low |
| app/evidence_engine.py | provenance validator | low |
| app/optimization_budget.py | sandbox benchmark key + SEARCH_BUDGET_EXHAUSTED code | low |
| app/workload_store.py | optional data_source_id field | low |
| app/api.py | include new router + lifespan hook (migration, reaper) | medium (guarded) |
| app/gnn/analyzer.py, app/rl/* | flag-gated new paths | medium |
| dashboard/app.py | add source selector + new section | medium |
| docker-compose.yml, .env.example, README | additive service/vars/docs | low |

## Dependencies
None new expected (pglast, torch_geometric GATv2Conv, asyncpg, psycopg2 already installed). Any addition recorded in DECISIONS.

## Tier 2/3 applicability
| Phase | Applicable | Reason |
|---|---|---|
| P6 semantic screening | yes (extend) | rewriter + sql_semantic_diff exist |
| P7 index portfolio | yes (extend) | index strategist + index_hygiene exist |
| P8 GATv2 | yes | PyG GNN + plan-graph mapper exist |
| P9 RL upgrades | yes (minimal) | tabular Q-learning exists; masking exists; replay added as bounded buffer |
| P10 DP | yes | choke point created in P4 |
| P11 evidence + blast radius | yes (extend) | both exist |
| P12 regression/drift | yes (extend) | both exist |
| P15 benchmark lab | conditional | only sandbox measurements |

## Test plan
After every phase: full suite (`python3 -m pytest -q`) compared with baseline (148 passed) + phase tests against the
local PostgreSQL 16 + HypoPG (main on :5432, sandbox-pg simulated by a second local cluster on :5433).
