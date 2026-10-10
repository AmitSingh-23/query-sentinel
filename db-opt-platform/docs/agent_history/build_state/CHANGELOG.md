# CHANGELOG (Final Upgrade)

## P0
- Created CODEBASE_AUDIT, UPGRADE_PLAN, STATUS, RESUME, ARCHITECTURE, API_CONTRACTS, DATA_CONTRACTS, TEST_STATUS, KNOWN_ISSUES, CHANGELOG, REQUIREMENT_TRACEABILITY. No source changes.

## P1 Foundation
- app/provenance.py (11 typed tags, `tagged`, `badge`, `has_provenance`), app/feature_flags.py, app/structured_log.py (trace_id + data_source_id)
- app/migrations/001_qs_meta.sql + app/meta_migration.py (idempotent, advisory lock); run by backend lifespan when QS_RUN_META_MIGRATION=true
- app/datasource.py: DataSourceResolver / DataSourceContext; demo needs no registry; distinct codes source_not_found / sandbox_expired / source_forbidden
- app/config.py: Section 10 settings + MAX_* aliases for existing BUDGET_MAX_*; app/errors.py: new machine-readable codes
- app/db.py: optional dsn_kwargs/server_settings/max_size; app/postgres_instrumentation.py: optional schema (default public)
- .env.example: all new variables documented

## P2 Dynamic ingestion
- app/dataset_ingestion.py: streaming CSV (encoding UTF-8/BOM/Latin-1, delimiter, header, ragged rows) and JSON (array, JSON Lines, object-with-array; one-level parent__child flattening, deeper -> jsonb); full-file type inference (boolean..text), identifier normalisation (snake_case, reserved words, 63 bytes, dedupe, originals kept); preview (no writes) / commit (one transaction: CREATE or additive ALTER ADD COLUMN, optional safe widening, COPY of pre-validated values, hidden lineage column _qs_ingest_id, registry rows, ingestion run, audit); conflicts reject the whole load with sample values + row numbers; duplicate SHA-256 needs allow_duplicate
- app/schema_inspector.py: SchemaCache keyed by (data_source_id, schema_version) + invalidate
- app/postgres_instrumentation.py: non-public schemas hide _qs_* columns

## P3 BYOD
- app/schema_verifier.py: pglast-based strict verifier (allowed DDL list, forbidden list with reasons + line numbers, dialect hints, psql meta-commands, type/extension/name/duplicate/dependency checks, reported normalisation of pg_dump preamble)
- app/sandbox_manager.py: sandbox-pg provisioning (db + role per sandbox, HMAC passwords, role limits), verified DDL applied as the sandbox role, quotas, ownership, extend/delete, TTL reaper with FOR UPDATE SKIP LOCKED, startup orphan sweep, workload purge
- app/synthetic_data.py: FK-ordered server-side generation at SMALL/MEDIUM/LARGE with unsatisfied-constraint report
- app/workload_store.py: data_source_id namespace (default demo), scoped views, purge_source
- migration: GRANT DELETE on optimizer_meta.query_history to qs_app (sandbox workload purge)
- examples/byod/shop_schema.sql: pg_dump-style example upload

## P4 SQL safety + NL-to-SQL
- app/sql_safety.py: 10-stage SQLSafetyGate (stages 1-4 reuse SecurityGateway; relation/column binding with suggestions; function allowlist; EXPLAIN as qs_nlq_reader with cost cap; cross-join rejection; row cap; READ ONLY execution with timeouts and pinned search_path; hidden _qs_* columns stripped)
- app/nlq.py: schema snapshot + stats, relevance (lexical + FK neighbours), compact schema context, LLM generator (untrusted-data delimiters, repair loop) and deterministic template generator [ANALYTIC FALLBACK], relative-date warning with anchored re-run, clarification path, template answer with PII masking, qs_meta.query_runs
- app/privacy_release.py: release_aggregate choke point (identity until DP flag)
- app/llm.py: additive complete_json()

## P5 Optimizer integration
- app/nlq_optimizer.py: optimize() runs the EXISTING Pipeline via Services.for_source(ctx); component trace (security, privacy, GNN, RL, HypoPG: used/fallback/skipped + why); HypoPG comparison with provenance; negligible-gain statement; real-name review DDL; workload row under data_source_id namespace (memory + optimizer_meta.query_history); SEARCH_BUDGET_EXHAUSTED audit; apply_index_and_measure() for sandbox/dynamic only [MEASURED SANDBOX]
- app/pipeline.py: Services.for_source(); recommendation_mapper / migration_generator: optional target schema; structural_sim: current_schema(); optimization_budget: sandbox_benchmarks key (backward compatible)

## P6 Semantic-risk screening
- app/sql_semantic_diff.py: structure() adds offset/aggregates/having; new risk_screen() LOW/MEDIUM/HIGH with reasons (outputs, grouping, predicates, joins, aggregation, LIMIT/OFFSET, DISTINCT, ORDER BY) and result_hash_compare() [MEASURED SANDBOX]
- app/agents/sql_rewriter.py: every deterministic and LLM rewrite carries semantic_diff.risk_screening
- app/agents/supervisor.py: HIGH-risk rewrites are blocked (not applied, not simulated) and listed in risks

## P7 Index portfolio
- app/index_portfolio.py: catalog-based IndexInfo (am, opclasses, collations, predicate, expressions, constraint backing, size, idx_scan), exact/prefix redundancy with exclusions, FK-support warnings, workload coverage from parsed pg_stat_statements, pruning only with >=7-day window and >=100 calls, consolidation as suggestion (REPLACE_INDEX_PORTFOLIO), review DROP/CREATE CONCURRENTLY + rollback, A/B/C HypoPG comparison (hypopg_hide_index for removals)
- app/nlq_optimizer.py: attaches index_portfolio when QS_FEATURE_INDEX_PORTFOLIO=true

## P8 GATv2 attention
- app/gnn/gat_model.py: PlanGATv2 (2x GATv2Conv, heads=2, edge_dim=8, add_self_loops=False, residual), structural edge features, attention extraction mapped to real plan edges (source/target/layer/head/weight), edge_attention, node_importance (incoming mass) kept separate from planner cost share, versioned checkpoints (architecture/feature/edge schema/checkpoint version/dataset), train_gat()
- models/gnn_gatv2.pt trained on the labelled synthetic plan generator: held-out same-distribution 1.0 (n=300), unseen template variants 0.8967 (n=300) [SYNTHETIC DATA]
- app/gnn/analyzer.py: QS_FEATURE_GATV2 selects GATv2 (attention in GNNDiagnosis.attention, TRAINED GNN only with a compatible checkpoint, otherwise ANALYTIC FALLBACK with reason); flag off = old GCN path unchanged
- app/contracts.py: optional GNNDiagnosis.attention; app/config.py: GNN_GAT_CHECKPOINT_PATH

## P9 RL curriculum / replay / masking
- app/rl/curriculum.py: levels 1-6 from parsed SQL (pglast), order_by_level, split_by_pattern (held-out by pattern)
- app/rl/replay.py: bounded prioritized replay (|TD|+eps, alpha, uniform mix, annealed IS weights, priority updates)
- app/rl/agent.py: update() returns TD error and takes an IS weight (default 1.0 = old behaviour); load refuses incompatible action schema / state encoding versions
- app/rl/trainer.py: TrainerConfig.curriculum / prioritized_replay (default off); invalid-action masking already existed and is logged as masked_actions

## P10 Differential privacy
- app/dp.py: Laplace mechanism (SystemRandom; seedable in tests only), parameter validation, clipping, post-processing, per-scope sequential-composition accountant, PRIVACY_BUDGET_EXHAUSTED audit hook, protect_schema_payload() for AI-facing schema aggregates (estimated_rows, absolute n_distinct, idx_scan)
- app/privacy_release.py routes to DP when QS_FEATURE_DP=true; app/agents/supervisor.py _llm_data DP-protects the AI payload only; app/nlq.py context omits aggregates after exhaustion; app/pipeline.py wires the audit hook

## P11 Evidence chain + blast radius
- app/contracts.py EvidenceItem: optional evidence_type, provenance, artifact_id
- app/evidence_engine.py: every item classified by code into OBSERVATION / PLAN_EVIDENCE / GAT_EVIDENCE / WORKLOAD_EVIDENCE / SCHEMA_EVIDENCE / RL_DECISION / HYPOPG / SANDBOX / BLAST_RADIUS / FINAL_RECOMMENDATION with provenance + artifact reference; validate_item rejects items without them; GATv2 attention item when present
- blast radius (existing) already maps parsed write statements to tables and labels write impact as heuristic

## P12 Regression / drift
- app/regression_detector.py, app/workload_drift.py: outputs labelled detection_method = 'threshold-based (not a statistical test)'; existing plan-fingerprint regression and JS-divergence drift reused (no second store); drift already feeds the RL recommendation (retraining_recommended)
- workload rows namespaced by data_source_id (P3/P5); pre-upgrade rows default to demo

## P13 API / SSE / frontend
- app/api_upgrade.py: routers /upgrade/status, /sources, /sources/{id}, /sources/{id}/schema, /data/preview (raw body, streamed size cap), /data/commit, /data/datasets, /data/runs, /byod/verify, /sandboxes (create/list/get/extend/delete), /nlq/ask, /nlq/ask/async (+ SSE via existing /stream/{id}, report via existing /report/{id}), /nlq/validate, /nlq/optimize, /nlq/apply-index, /index-portfolio; X-Session-Id ownership header; machine-readable error codes; mounted in app/api.py with lifespan startup (resolver, sandbox manager + reaper + startup sweep, ingestion, NLQ)
- app/events.py: NLQ_* events; app/nlq.py progress callback
- dashboard/upgrade_ui.py + dashboard/app.py: sidebar data-source selector (session id in ?sid=), source panel (tables/rows/schema version/provenance, sandbox countdown with Extend/Delete), dataset upload with preview/commit and conflict tables, BYOD 'Upload Schema Only' flow with verification report before provisioning, Ask Your Database (10 sections, provenance badges, component trace, HypoPG metrics, apply-index for sandbox/dataset only, anchored re-run), GATv2 attention overlay (dashboard/plots.attention_dag) in the GNN tab, DP status in the Privacy tab
- app/synthetic_data.py: enum/char catalog columns cast to text (synthetic enums now varied)

## P14 Docker / runtime hardening
- docker/sandbox/Dockerfile (PG16 + HypoPG, no demo init scripts)
- docker-compose.yml (additive): service sandbox-pg (internal network sandbox_net, no published port, tmpfs storage, mem 1g / 1 cpu, healthcheck); backend joins default + sandbox_net, depends on sandbox-pg healthy, SANDBOX_PG_HOST=sandbox-pg; dashboard --server.maxUploadSize = INGEST_MAX_UPLOAD_MB (one variable for both limits)
- config/sandbox_manager: SANDBOX_PG_ADMIN_PASSWORD falls back to POSTGRES_PASSWORD and SANDBOX_SECRET to PRIVACY_HMAC_KEY/POSTGRES_PASSWORD so the user's existing .env keeps working
- backend lifespan (P1/P13) runs the qs_meta migration after existing init, starts the reaper and the startup sweep

## P15 Benchmark lab
- app/sandbox_benchmark.py: BASELINE / INDEX / FULL variants on BYOD sandboxes only, each in a rolled-back transaction, warm-up discarded, median/min/max over N repetitions, dataset row counts and environment recorded, [MEASURED SANDBOX] (+[SYNTHETIC DATA])
- POST /api/v1/sandboxes/{id}/benchmark (SQL and rewrite pass the safety gate first)

## P16 Final audit
- FINAL_AUDIT.md, FINAL_REPORT.md, ARCHITECTURE.md (after upgrade), README section 28 + Docker notes; traceability complete; local leftovers cleaned (0 sandboxes, 0 qs_dynamic tables, 6 public indexes)
