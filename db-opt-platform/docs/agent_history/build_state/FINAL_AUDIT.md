# FINAL_AUDIT (P16 checklist) - 2026-10-04

| Item | State | Evidence |
|---|---|---|
| Existing code audited and baseline recorded | VERIFIED | CODEBASE_AUDIT.md, TEST_STATUS.md (148 passed at tag baseline/pre-upgrade) |
| No unnecessary refactor; diff reviewed | VERIFIED | `git diff --name-status baseline/pre-upgrade HEAD`: 30 modified files, all additive edits named in CHANGELOG; 51 added files |
| No existing test edited, skipped or loosened | VERIFIED | no file of the baseline tests/ set appears as modified in the diff |
| Existing demo database and flows behave as baseline | VERIFIED | old suite alone: 148 passed (incl. 6 live integration); init_db.sql / seed_data.py unchanged; 6 public indexes, no leftovers |
| Dynamic ingestion creates, validates and evolves tables safely | VERIFIED | test_upgrade_ingestion, test_upgrade_api::test_dynamic_upload_flow |
| Schema evolution is additive only | VERIFIED | no DROP/RENAME/narrowing code path; conflict test leaves zero partial writes |
| BYOD verification before provisioning; rejects data-bearing and dangerous SQL | VERIFIED | test_upgrade_byod (22 forbidden constructs, provision_calls == 0) |
| BYOD isolation without Docker-in-Docker or socket | VERIFIED | separate server/db/role; role A cannot reach B or the main DB |
| Sandbox cleanup by TTL; orphan sweep | VERIFIED | test_ttl_reaper_and_startup_sweep |
| Schema-aware NL-to-SQL with no hard-coded names | VERIFIED | test_nl_on_ingested_table... (fake LLM asserts real columns in the prompt) |
| SQL safety layer rejects the adversarial corpus | VERIFIED | 32-case corpus at expected stages; restricted role refuses optimizer_meta |
| Generated SQL flows through the existing optimizer | VERIFIED | test_upgrade_integration (demo, dynamic), test_upgrade_api (sandbox) |
| GATv2 with edge features + attention, fallback preserved | VERIFIED (flag off by default) | test_upgrade_gat |
| Model mode and versions visible in API and UI | VERIFIED | /upgrade/status model_modes.gnn.gatv2; GNN tab attention caption |
| RL curriculum, TD-error PER, held-out, masking | PARTIAL | components verified; trainer loop NOT RUN in tests (K3); policy not retrained |
| Index portfolio reasoning; pruning workload-based | VERIFIED (flag off by default) | test_upgrade_portfolio |
| DP bounded and budgeted; exhaustion fallback | VERIFIED (flag off by default) | test_upgrade_dp |
| Semantic-risk screening | VERIFIED | test_upgrade_semantic |
| Evidence chain with provenance on every item | VERIFIED | test_upgrade_evidence |
| Metric provenance badges in the UI | VERIFIED | AppTest smoke: badges rendered in Ask Your Database |
| Search budget enforced and recorded | VERIFIED | SEARCH_BUDGET_EXHAUSTED in report + qs_meta.audit_log |
| Plan regression and drift (threshold-based) | VERIFIED | test_upgrade_drift + existing tests |
| HypoPG works in both PostgreSQL services | VERIFIED (local clusters) | main: existing tests; sandbox: hypopg_create_index as sandbox role |
| Blast radius with honest labelling | VERIFIED | parser mapping test; HEURISTIC ESTIMATE provenance |
| FastAPI works; SSE works | VERIFIED | test_upgrade_api SSE order NLQ_STARTED ... NLQ_COMPLETE |
| Frontend non-generic and fits existing design | VERIFIED (manual/AppTest) | same dark console, chips, dense tables |
| No fake metrics / model results / benchmarks | VERIFIED | all numbers from runs; GATv2 1.0 same-distribution accuracy flagged as synthetic-label |
| Migration and rollback generation works | VERIFIED | existing tests + schema-aware migration for qs_dynamic |
| No automatic production deployment path | VERIFIED | apply-index refused on demo; review artifacts only |
| Existing tests pass vs baseline; new tests pass | VERIFIED | 148/148 old + 115/115 new = 263 passed |
| Docker clean start | NOT RUN | no Docker in agent workspace (K4); commands in README section 16 |
| REQUIREMENT_TRACEABILITY.md complete | VERIFIED | all rows filled |
| Documentation and .env.example updated | VERIFIED | README section 28, .env.example Final Upgrade block |

Status wording: because Docker clean-start verification is NOT RUN and RL is PARTIAL, the system is NOT declared a
"verified hackathon-ready production-oriented prototype". It is an upgraded prototype verified by tests in the agent
workspace, pending the user's Docker verification.
