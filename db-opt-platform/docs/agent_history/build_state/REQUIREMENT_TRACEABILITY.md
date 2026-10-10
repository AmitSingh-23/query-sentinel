# REQUIREMENT_TRACEABILITY (Final Upgrade)

| Req | Phase | Implementation | Test | API | Dashboard | State |
|---|---|---|---|---|---|---|
| Audit + baseline | P0 | .build_state/CODEBASE_AUDIT.md, TEST_STATUS.md | baseline run | - | - | VERIFIED |
| Context resolver | P1 | app/datasource.py | test_upgrade_foundation | (P13) | (P13) | VERIFIED |
| qs_meta migration | P1 | app/migrations/001_qs_meta.sql, app/meta_migration.py, api lifespan | test_migration_runs_twice... | - | - | VERIFIED |
| Feature flags | P1 | app/feature_flags.py, app/config.py | test_feature_flags_snapshot_defaults | /api/v1/upgrade/status | Privacy tab | VERIFIED |
| Provenance tags | P1/P13 | app/provenance.py + every new output | test_provenance_serializes_tags, API tests | provenance fields | badges (upgrade_ui.prov) | VERIFIED |
| Dynamic ingestion CSV/JSON | P2 | app/dataset_ingestion.py | test_upgrade_ingestion (6), test_upgrade_api | /api/v1/data/* | Upload Dataset flow | VERIFIED |
| Additive schema evolution | P2 | dataset_ingestion.evolution_plan/commit | test_create_append_evolve_conflict_cycle | (P13) | (P13) | VERIFIED |
| BYOD verifier | P3 | app/schema_verifier.py | test_upgrade_byod (verifier tests) | (P13) | (P13) | VERIFIED |
| BYOD sandbox-pg isolation + TTL | P3 | app/sandbox_manager.py | test_provision_hypopg_isolation..., test_ttl_reaper_and_startup_sweep, test_failed_verification_never_provisions | (P13) | (P13) | VERIFIED (local cluster; Docker NOT RUN) |
| Synthetic data | P3 | app/synthetic_data.py | test_synthetic_scales_row_counts | (P13) | (P13) | VERIFIED (small/medium run; large NOT RUN for time) |
| SQL safety layer (10 stages) | P4 | app/sql_safety.py | test_upgrade_nlq (adversarial corpus 32 cases, valid analytics live) | (P13) | (P13) | VERIFIED |
| Schema-aware NL-to-SQL | P4 | app/nlq.py | test_nl_on_ingested_table..., test_repair_loop_exhaustion... | (P13) | (P13) | VERIFIED |
| Optimizer integration + search budget + component trace | P5 | app/nlq_optimizer.py, app/pipeline.py for_source | test_upgrade_integration (2) | (P13) | (P13) | VERIFIED demo+dynamic (sandbox in P13) |
| Semantic-risk screening | P6 | app/sql_semantic_diff.py risk_screen, sql_rewriter, supervisor n_merge | test_upgrade_semantic (2) | report.agent_recommendation.rewrite.semantic_diff | (P13) | VERIFIED |
| Index portfolio | P7 | app/index_portfolio.py | test_upgrade_portfolio (2) | (P13 /index-portfolio) | (P13) | VERIFIED (flag default off) |
| GATv2 attention | P8 | app/gnn/gat_model.py, app/gnn/analyzer.py | test_upgrade_gat (3) | gnn_analysis.attention | (P13 overlay) | VERIFIED (flag default off) |
| RL curriculum / PER / masking | P9 | app/rl/curriculum.py, replay.py, agent.py, trainer.py | test_upgrade_rl (3) | rl_recommendation.masked_actions | (P13) | PARTIAL: components VERIFIED; full trainer loop NOT RUN (K3); no retraining |
| Differential privacy + budget | P10 | app/dp.py, privacy_release.py, supervisor._llm_data | test_upgrade_dp (3) | (P13 /upgrade/status) | (P13 Privacy tab) | VERIFIED (flag default off) |
| Evidence chain + blast radius | P11 | app/evidence_engine.py, app/blast_radius.py | test_upgrade_evidence (2) | final_report.evidence_chain | (P13 chain view) | VERIFIED |
| Regression / drift | P12 | app/regression_detector.py, app/workload_drift.py, app/workload_store.py | test_upgrade_drift (1) + existing test_research_modules | /api/v1/workload | Workload tab | VERIFIED |
| API/SSE/UI | P13 | app/api_upgrade.py, dashboard/upgrade_ui.py, dashboard/app.py | test_upgrade_api (3: demo, dynamic, sandbox) + Streamlit AppTest smoke (demo ask, sandbox select/countdown/ask) | see API_CONTRACTS | section 0 + GNN/Privacy tabs | VERIFIED (file-upload widgets verified via API; AppTest cannot drive uploads) |
| Docker sandbox-pg | P14 | docker-compose.yml, docker/sandbox/Dockerfile | YAML parse; sandbox lifecycle verified against a local PG16+HypoPG cluster | - | - | NOT RUN in Docker (K4) |
| Benchmark lab | P15 | app/sandbox_benchmark.py, api_upgrade | test_upgrade_benchmark (1) | /sandboxes/{id}/benchmark | (API) | VERIFIED |
