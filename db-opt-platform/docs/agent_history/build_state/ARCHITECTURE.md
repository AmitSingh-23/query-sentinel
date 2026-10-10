# ARCHITECTURE (as built; updated per phase)

## After P0 (unchanged pre-upgrade system)
Streamlit dashboard -> FastAPI (`app/api.py`) -> `Services` (Database pool as qs_app, PostgresInstrumentation,
DataObfuscator vault, OutgoingPayloadGuard, LLMClient, GNNAnalyzer, RLPolicy, EventBus, AuditLogger, WorkloadStore)
-> LangGraph `Pipeline` (security -> privacy -> schema -> EXPLAIN -> plan graph -> GNN -> supervisor -> SQL rewriter /
schema expert / index strategist -> merge -> RL -> validator -> HypoPG sandbox -> blast radius -> final report).
Single PostgreSQL 16 (+HypoPG, pg_stat_statements): schema `public` (demo data), schema `optimizer_meta` (runs,
query_history, audit_events, migrations).

## After the Final Upgrade (P1-P15)
```
Streamlit dashboard (section 0: data-source selector, dataset upload, BYOD flow, Ask Your Database; GATv2 overlay;
DP status)  --HTTP + X-Session-Id-->  FastAPI (existing app + app/api_upgrade.py routers)
   |-- DataSourceResolver (app/datasource.py): (data_source_id, session) -> DataSourceContext
   |      demo    -> existing pool (qs_app, schema public)
   |      dynamic -> pool search_path qs_dynamic (+public for HypoPG functions), tables from qs_meta registry
   |      sandbox -> per-sandbox pool on sandbox-pg (role sbx_<id>_r, HMAC-derived password)
   |-- DatasetIngestionService (preview/commit, additive evolution)      -> main PG schema qs_dynamic (admin path)
   |-- SandboxManager (verify -> provision -> DDL -> synthetic data; TTL reaper; orphan sweep) -> sandbox-pg
   |-- NLQService (schema snapshot + context -> LLM or template generator -> SQLSafetyGate (10 stages) -> execute)
   |      \-- nlq_optimizer.optimize -> Services.for_source(ctx) -> EXISTING LangGraph Pipeline
   |             (security -> privacy -> schema -> EXPLAIN -> GCN or GATv2 -> agents -> RL -> HypoPG -> blast -> report)
   |-- index_portfolio, sandbox_benchmark, dp (accountant), provenance tags on every metric
Main PostgreSQL: public (demo, untouched) | optimizer_meta (+data_source_id) | qs_meta (registry, audit) | qs_dynamic
sandbox-pg: one database + one role per sandbox, internal network only, tmpfs, TTL
```
