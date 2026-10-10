# CODEBASE_AUDIT (Phase P0 of the Final Upgrade Master Prompt)

Audit date: 2026-10-03. Source: snapshot of the user's working copy (C:\Users\bisht\Desktop\codecWe\db-opt-platform),
`.env` excluded. Not a git repository on the PC; git was initialised in the agent workspace for branch/tag discipline.

## Environment (agent workspace)
| Item | Version |
|---|---|
| Python | 3.13.16 (Docker image uses 3.12) |
| PostgreSQL | 16.15 + HypoPG 1.4.0 (apt postgresql-16-hypopg) + pg_stat_statements (preloaded) |
| torch / torch_geometric | 2.14.1 / 2.8.0.post1 (GATv2Conv available) |
| pglast | 8.4 (PostgreSQL 17 parser) |
| fastapi / asyncpg / psycopg2 | 0.142.2 / 0.31.0 / 2.9.13 |
| langgraph / streamlit / plotly / pandas | 1.2.12 / 1.65.0 / 7.1.0 / 3.0.5 |
| LLM client | own httpx client (`app/llm.py`), providers none/gemini/openai/mock, default `none` |
| Docker | NOT AVAILABLE in agent workspace (images run on the user's PC via Docker Desktop) |

Local verification DB: initdb cluster on localhost:5432 initialised with `scripts/create_extensions.sql` +
`scripts/init_db.sql`, `qs_app` password set, `seed_data.py` light mode (100 tenants / 100k orders / 300k items),
`generate_workload.py`.

## Subsystems
| Subsystem | Path | Implementation / interface | Tests | Weakness | Modify? |
|---|---|---|---|---|---|
| Config | app/config.py | pydantic-settings `Settings`, `get_settings()` cached, `reset_settings_cache()` | indirect | no feature flags for new tiers | yes (additive fields) |
| Connection mgmt | app/db.py | `Database` (asyncpg pool as `qs_app`), `connection()`, `read_only()`, `fetch`, `fetchval`, `execute_write`, `explain`, `explain_on` (GENERIC_PLAN via DO block) | test_core, integration | single DSN, no per-source context | yes (optional DSN/search_path) |
| Catalog instrumentation | app/postgres_instrumentation.py | `PostgresInstrumentation(db)`: health, tables, columns, indexes, foreign_keys, primary_keys, statements, explain; SQL hard-codes `nspname='public'` | test_core | schema fixed to public | yes (optional schema) |
| SchemaInspector | app/schema_inspector.py | `SchemaInspector(instr).inspect(tables)` -> `SchemaMetadata`; no cache; `pseudonymize_metadata`, `anonymize` | test_core | no cache / no versioning | yes (cache by source+version, invalidate) |
| Security gateway | app/security.py | `SecurityGateway.validate(sql)` -> `ValidatedQuery`; pglast parse, single stmt, SELECT only, AST visitor (dangerous functions, forbidden catalogs, SELECT INTO, locking, DML CTE) | test_security | no relation-existence / column binding / plan-cost stages | reuse as stage 1-4 of NLQ safety gate (not duplicated) |
| Privacy vault | app/masking_vault.py, app/pii.py, app/llm_guard.py | `DataObfuscator` (literal parameterisation, HMAC pseudonyms, request vault), PII regex, `OutgoingPayloadGuard` | test_masking | no DP | P10 adds DP choke point |
| Workload ingestion (slow-query logs) | app/ingestion.py | `IngestionEngine` (JSON/CSV log records -> `WorkloadRecord`), `PgStatStatementsCollector` | test_ingestion | this is workload-log ingestion, NOT dataset ingestion | no (new dataset ingestion is separate module) |
| Workload store | app/workload_store.py + optimizer_meta.query_history | in-memory `WorkloadStore` + persisted rows | test_research_modules | no data_source_id | yes (additive namespace) |
| Plan parser | app/plan_parser.py | EXPLAIN JSON -> PlanAnalysis | test_plan_parser | - | no |
| GNN | app/gnn/* | `PlanGCN` (PyG GCNConv 32->32->16, global_max_pool, Linear 16->4), checkpoint `models/gnn_bottleneck.pt` (trained on synthetic plans), `GNNAnalyzer` trained/fallback, `fallback_analytics.py`, mapper 32 node features, no edge features | test_gnn | no attention / edge features | P8 adds GATv2 path behind flag |
| RL | app/rl/* | hierarchical tabular Q-learning (`QLearningAgent`), invalid-action masking already present, env against HypoPG, `models/rl_policy.json` | test_rl | no curriculum, no replay | P9 (conditional) applicable |
| LangGraph supervisor | app/agents/supervisor.py | `Pipeline(services).run(request_id, raw_sql)`; nodes security -> privacy -> schema -> explain -> graph -> gnn -> supervisor -> experts -> merge -> rl -> validator -> hypopg -> blast -> final | test_agents, integration | bound to one Services (one DB) | P5: run with a per-source Services |
| SQL rewriter | app/agents/sql_rewriter.py | 4 deterministic operators | test_agents | - | P6 hooks screening |
| Semantic diff | app/sql_semantic_diff.py | structure()/diff()/verify() (relations, joins, sublinks, conjuncts) | test_research_modules | no risk class, no output-column/group/limit checks | P6 extend |
| Index recommender | app/agents/index_strategist.py, app/recommendation_mapper.py | candidates, canonical DDL `public.` | test_agents | public-only | P5 schema param |
| Index hygiene | app/index_hygiene.py | redundancy (prefix) report | test_research_modules | no portfolio actions | P7 extend |
| HypoPG sandbox | app/sandbox.py | `HypoPGSandbox` creates hypothetical indexes + EXPLAIN on one connection | test_sandbox | - | no |
| Structural sim | app/structural_sim.py | TEMP-table write latency + partition sim (rolled back) | test_structural_sim | `schemaname='public'` | minor |
| Blast radius | app/blast_radius.py | pg_stat_statements writes parsed by pglast -> table match | test_research_modules | - | P11 provenance |
| Evidence | app/evidence_engine.py | `EvidenceChain`, `build_chain` | test_research_modules | no provenance validator | P11 extend |
| Regression / drift | app/regression_detector.py, app/workload_drift.py | plan regression, JS divergence drift | test_research_modules | - | P12 (exists; label + flags) |
| Budget | app/optimization_budget.py | `OptimizationBudget` (candidates, hypopg, agent steps, llm retries, workload queries), BUDGET_EXHAUSTED audit | test_research_modules | no sandbox-benchmark key | P5 extend |
| Migration generator | app/migration_generator.py | CREATE/DROP INDEX CONCURRENTLY + rollback, human review | test_agents | public hard-coded | P5/P7 schema param |
| NL intent | app/agents/nl_intent.py | heuristic retrieval over pg_stat_statements -> candidate id -> optimize | test_weekly_sales_dashboard | demo-workload retrieval, not NL-to-SQL | P4 adds NL-to-SQL beside it |
| API | app/api.py | FastAPI; routes listed in API_CONTRACTS.md; errors `{error, message, stage, ...}`; optional X-API-Key | test_api | - | P13 add routers |
| SSE | app/events.py | `EventBus` per request id, `/api/v1/stream/{id}` | test_events | - | reuse |
| Audit | app/audit.py | `AuditLogger.record(rid, type, stage, details)` persisted to optimizer_meta.audit_events | test_core | - | reuse |
| Dashboard | dashboard/app.py, components.py, plots.py, streaming_ui.py | Streamlit dark console, Ask/Result/Details tabs, demo mode toggle, calls backend over HTTP | none (manual) | no data-source selector | P13 |
| Docker | docker-compose.yml, Dockerfile, docker/db | services db (PG16+HypoPG), backend, dashboard; volume pgdata; healthchecks | compose config | no sandbox-pg | P14 additive |
| DB init | scripts/init_db.sql, create_extensions.sql, docker/db/03_app_role.sh, seed_data.py, generate_workload.py | demo schema public + optimizer_meta | integration | - | NEVER modified (forbidden) |

## Every place a database connection is opened (refactor points)
1. `app/db.py:41` `asyncpg.create_pool(**settings.app_dsn_kwargs)` - the only runtime pool; everything (instrumentation, supervisor, sandbox, structural_sim, blast radius, nl_intent, persistence) goes through `Database`.
2. `app/benchmark.py:178` `asyncpg.connect(BENCHMARK_ADMIN_DSN)` - opt-in measured benchmark only.
3. `app/sandbox.py:138` synchronous psycopg2 evaluator - RL training script only.
4. `scripts/train_gnn.py:39`, `scripts/train_rl.py:100`, `scripts/seed_data.py:52` - offline scripts (psycopg2).

Conclusion: the DataSource resolver only needs to produce a `Database` (+ `PostgresInstrumentation`) per source; the
Services/Pipeline layer already takes them by injection.

## Exercised capabilities (P0 smoke, by running, not by filename)
- Baseline suite: 148 passed (incl. 6 live integration tests against the local DB) - see TEST_STATUS.md.
- `/api/v1/health` -> postgresql, hypopg, pg_stat_statements all true.
- `/api/v1/optimize` demo query A: status completed, planner cost 7413.34 -> 2330.21 (-68.57 %, HypoPG), GNN mode `trained`, RL mode `trained_policy`, answer sentence with zero-exposure proof, migration generated.
- Security gateway, privacy vault, schema inspection, EXPLAIN, plan parser, GNN, RL, LangGraph, rewriting, index recommendation, HypoPG, blast radius, SSE, migration generation: covered by the passing baseline tests.
- Docker: NOT RUN here (no Docker in agent workspace); compose file unchanged.
