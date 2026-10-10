# TEST_STATUS

## Commands
- Full suite: `python3 -m pytest -q -rA -p no:cacheprovider` (pytest.ini: testpaths=tests, asyncio auto)
- Env for live DB tests: POSTGRES_HOST=localhost, POSTGRES_PASSWORD, QS_APP_PASSWORD, PRIVACY_HMAC_KEY (values not recorded)
- Integration tests (`-m integration`) auto-skip when no DB is reachable.

## Substitutions
Prompt names `tests/test_existing_core.py` / `tests/test_new_feature.py` do not exist. Existing suite = all files in
tests/ at tag baseline/pre-upgrade. New tests go to `tests/test_upgrade_<area>.py`.

## Baseline (tag baseline/pre-upgrade, 2026-10-04)
Result: **148 passed, 0 failed, 0 skipped** (live PostgreSQL 16.15 + HypoPG 1.4.0 reachable, so 6 integration tests ran).
Docker: NOT RUN (no Docker in agent workspace).

<details><summary>per-test baseline</summary>

```
PASSED tests/test_agents.py::test_full_graph_executes_state_transitions
PASSED tests/test_agents.py::test_routing_skips_rewriter_and_index_for_efficient_query
PASSED tests/test_agents.py::test_unsafe_sql_rejected_before_any_agent
PASSED tests/test_agents.py::test_report_contains_no_raw_literals_outside_internal_fields
PASSED tests/test_agents.py::test_index_strategist_uses_only_known_identifiers
PASSED tests/test_agents.py::test_validator_rejects_invalid_and_redundant
PASSED tests/test_agents.py::test_sql_rewriter_correlated_subquery_semantics_checked
PASSED tests/test_agents.py::test_llm_rewrite_with_invented_identifier_rejected
PASSED tests/test_agents.py::test_mocked_llm_payload_is_anonymised_and_validated
PASSED tests/test_agents.py::test_malformed_llm_json_falls_back
PASSED tests/test_api.py::test_health
PASSED tests/test_api.py::test_status_reports_model_modes
PASSED tests/test_api.py::test_mask
PASSED tests/test_api.py::test_analyze
PASSED tests/test_api.py::test_analyze_rejects_ddl
PASSED tests/test_api.py::test_optimize_contract
PASSED tests/test_api.py::test_optimize_rejects_multi_statement
PASSED tests/test_api.py::test_ingestion_json_and_csv
PASSED tests/test_api.py::test_stream_async_and_report
PASSED tests/test_api.py::test_metrics_endpoint
PASSED tests/test_api.py::test_unknown_report_404
PASSED tests/test_api.py::test_api_key_enforced
PASSED tests/test_core.py::test_settings_redacted_view_hides_secrets
PASSED tests/test_core.py::test_structured_errors
PASSED tests/test_core.py::test_log_redaction
PASSED tests/test_core.py::test_audit_trail_sanitised
PASSED tests/test_core.py::test_budget_enforced_and_reported
PASSED tests/test_core.py::test_capability_firewall
PASSED tests/test_core.py::test_schema_inspector_build_and_anonymize
PASSED tests/test_core.py::test_workload_store_context
PASSED tests/test_core.py::test_metrics_snapshot_and_prometheus
PASSED tests/test_events.py::test_event_creation_and_contract
PASSED tests/test_events.py::test_request_isolation
PASSED tests/test_events.py::test_sse_serialisation_roundtrip
PASSED tests/test_events.py::test_sensitive_payloads_redacted
PASSED tests/test_events.py::test_subscribe_replays_and_terminates
PASSED tests/test_gnn.py::test_operator_mapping_spec
PASSED tests/test_gnn.py::test_graph_nodes_edges_shapes
PASSED tests/test_gnn.py::test_model_forward_pass
PASSED tests/test_gnn.py::test_fallback_mode_when_no_checkpoint
PASSED tests/test_gnn.py::test_corrupted_checkpoint_falls_back
PASSED tests/test_gnn.py::test_fallback_rules_on_real_plans
PASSED tests/test_gnn.py::test_training_save_load_roundtrip
PASSED tests/test_gnn.py::test_synthetic_dataset_balanced
PASSED tests/test_gnn.py::test_shipped_checkpoint_valid
PASSED tests/test_ingestion.py::test_json_ingestion
PASSED tests/test_ingestion.py::test_csv_ingestion
PASSED tests/test_ingestion.py::test_privacy_sanitisation
PASSED tests/test_ingestion.py::test_fingerprint_ignores_literals
PASSED tests/test_ingestion.py::test_no_raw_rows_and_bad_records
PASSED tests/test_ingestion.py::test_vaults_cleared_after_batch
PASSED tests/test_ingestion.py::test_pg_stat_statements_collector
PASSED tests/test_integration.py::test_extensions_operational
PASSED tests/test_integration.py::test_least_privilege_role_cannot_write_or_ddl
PASSED tests/test_integration.py::test_real_hypopg_sandbox_and_cleanup
PASSED tests/test_integration.py::test_live_end_to_end_pipeline
PASSED tests/test_masking.py::test_literals_parameterized
PASSED tests/test_masking.py::test_identifier_pseudonymization_is_deterministic_hmac
PASSED tests/test_masking.py::test_reverse_translation
PASSED tests/test_masking.py::test_unknown_identifier_rejected
PASSED tests/test_masking.py::test_translation_only_allows_create_index
PASSED tests/test_masking.py::test_request_isolation_and_clear
PASSED tests/test_masking.py::test_mask_result_never_contains_reverse_map
PASSED tests/test_masking.py::test_ordinals_kept
PASSED tests/test_masking.py::test_fallback_quarantines_unsafe_constructs
PASSED tests/test_masking.py::test_pii_detection_types
PASSED tests/test_masking.py::test_uuid_and_email_queries_not_rejected
PASSED tests/test_masking.py::test_bitmask_flags
PASSED tests/test_masking.py::test_guard_allows_clean_payload
PASSED tests/test_masking.py::test_guard_blocks_and_audits[payload0-pii:email]
PASSED tests/test_masking.py::test_guard_blocks_and_audits[payload1-raw_literal]
PASSED tests/test_masking.py::test_guard_blocks_and_audits[payload2-reverse_map_identifier]
PASSED tests/test_masking.py::test_guard_blocks_and_audits[payload3-secret:api_key]
PASSED tests/test_masking.py::test_guard_blocks_and_audits[payload4-secret:password_assignment]
PASSED tests/test_masking.py::test_guard_blocks_raw_result_values
PASSED tests/test_plan_parser.py::test_explain_json_parsing
PASSED tests/test_plan_parser.py::test_nested_plan_and_subplan_attribution
PASSED tests/test_plan_parser.py::test_plan_list_form_and_errors
PASSED tests/test_plan_parser.py::test_fingerprint_stable_and_shape
PASSED tests/test_plan_parser.py::test_sanitize_expression
PASSED tests/test_plan_parser.py::test_sanitize_plan_removes_names_and_literals
PASSED tests/test_research_modules.py::test_plan_regression_requires_evidence
PASSED tests/test_research_modules.py::test_predicate_intelligence_roles
PASSED tests/test_research_modules.py::test_predicate_intelligence_correlated_subquery
PASSED tests/test_research_modules.py::test_index_hygiene_is_report_only
PASSED tests/test_research_modules.py::test_cardinality_never_invents_actual_rows
PASSED tests/test_research_modules.py::test_cardinality_with_actuals
PASSED tests/test_research_modules.py::test_semantic_diff_detects_changes
PASSED tests/test_research_modules.py::test_workload_drift_measured_not_fabricated
PASSED tests/test_research_modules.py::test_partition_advice_is_advisory
PASSED tests/test_research_modules.py::test_evidence_chain_kinds
PASSED tests/test_rl.py::test_state_encoding_has_no_identifiers
PASSED tests/test_rl.py::test_invalid_action_masking
PASSED tests/test_rl.py::test_environment_transition_and_reward
PASSED tests/test_rl.py::test_reward_components_and_workload_weight
PASSED tests/test_rl.py::test_training_update_learns_best_action
PASSED tests/test_rl.py::test_save_load_policy
PASSED tests/test_rl.py::test_fallback_mode_is_labelled
PASSED tests/test_rl.py::test_fallback_no_change_for_efficient_plans
PASSED tests/test_rl.py::test_unseen_state_backoff
PASSED tests/test_rl.py::test_corrupt_policy_rejected
PASSED tests/test_sandbox.py::test_cost_reduction_formula_safe
PASSED tests/test_sandbox.py::test_hypothetical_index_creation_cost_comparison_cleanup
PASSED tests/test_sandbox.py::test_unhelpful_candidate_not_kept
PASSED tests/test_sandbox.py::test_cleanup_attempted_even_on_failure
PASSED tests/test_sandbox.py::test_skipped_without_candidates
PASSED tests/test_sandbox.py::test_write_query_discovery_and_table_matching
PASSED tests/test_sandbox.py::test_blast_radius_ranking_and_risk
PASSED tests/test_sandbox.py::test_risk_classification_bands
PASSED tests/test_sandbox.py::test_migration_and_rollback_generation
PASSED tests/test_sandbox.py::test_identifier_quoting_in_migration
PASSED tests/test_security.py::test_simple_select_passes
PASSED tests/test_security.py::test_multiple_statements_rejected
PASSED tests/test_security.py::test_ddl_rejected[DROP TABLE orders]
PASSED tests/test_security.py::test_ddl_rejected[CREATE INDEX ON orders(status)]
PASSED tests/test_security.py::test_ddl_rejected[ALTER TABLE orders ADD COLUMN x int]
PASSED tests/test_security.py::test_ddl_rejected[TRUNCATE orders]
PASSED tests/test_security.py::test_ddl_rejected[CREATE TABLE t (a int)]
PASSED tests/test_security.py::test_dangerous_rejected[COPY orders TO '/tmp/x']
PASSED tests/test_security.py::test_dangerous_rejected[SELECT pg_read_file('/etc/passwd')]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT pg_sleep(10)]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT * FROM pg_authid]
PASSED tests/test_security.py::test_dangerous_rejected[DELETE FROM orders]
PASSED tests/test_security.py::test_dangerous_rejected[UPDATE orders SET status = 'x']
PASSED tests/test_security.py::test_dangerous_rejected[SELECT * INTO new_t FROM orders]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT * FROM orders FOR UPDATE]
PASSED tests/test_security.py::test_dangerous_rejected[WITH d AS (DELETE FROM orders RETURNING *) SELECT * FROM d]
PASSED tests/test_security.py::test_dangerous_rejected[SET statement_timeout = 0]
PASSED tests/test_security.py::test_dangerous_rejected[ALTER SYSTEM SET work_mem = '1GB']
PASSED tests/test_security.py::test_dangerous_rejected[VACUUM orders]
PASSED tests/test_security.py::test_dangerous_rejected[EXPLAIN ANALYZE SELECT 1]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT set_config('x','y',false)]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT nextval('s')]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT dblink('x','y')]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT lo_import('/etc/passwd')]
PASSED tests/test_security.py::test_dangerous_rejected[SELECT pg_terminate_backend(1)]
PASSED tests/test_security.py::test_query_length_limit
PASSED tests/test_security.py::test_invalid_sql_does_not_echo_input
PASSED tests/test_security.py::test_empty_and_nul
PASSED tests/test_security.py::test_parameterised_query_uses_generic_plan
PASSED tests/test_security.py::test_cte_select_allowed
PASSED tests/test_structural_sim.py::test_identifier_quoting_rejects_injection
PASSED tests/test_structural_sim.py::test_headline_contains_ps_elements
PASSED tests/test_structural_sim.py::test_simulator_failure_is_non_fatal
PASSED tests/test_structural_sim.py::test_live_write_latency_and_partitioning_leave_nothing_behind
PASSED tests/test_structural_sim.py::test_live_report_has_answer_and_zero_exposure_proof
PASSED tests/test_weekly_sales_dashboard.py::test_weekly_sales_dashboard_is_safely_obfuscated
PASSED tests/test_weekly_sales_dashboard.py::test_ai_prevented_from_seeing_raw_tenant_id
148 passed, 1 warning in 9.56s
```
</details>

## Per-phase results
| Phase | Command | Old suite | New tests | Notes |
|---|---|---|---|---|
| P0 | full suite | 148 passed | - | baseline |
| P1 | full suite + phase tests | 148 passed | 10 passed | foundation |
| P2 | full suite + phase tests | 148 passed | 16 passed (P1+P2) | dynamic ingestion |
| P3 | full suite + phase tests | 148 passed | 47 passed (P1-P3) | BYOD sandbox |
| P4 | full suite + phase tests | 148 passed | 93 passed (P1-P4) | SQL safety + NL-to-SQL |
| P5 | full suite + phase tests | 148 passed | 95 passed (P1-P5) | optimizer integration |
| P6 | full suite + phase tests | 148 passed | 97 passed (P1-P6) | semantic-risk screening |
| P7 | full suite + phase tests | 148 passed | 99 passed (P1-P7) | index portfolio |
| P8 | full suite + phase tests | 148 passed | 102 passed (P1-P8) | GATv2 attention |
| P9 | full suite + phase tests | 148 passed | 105 passed (P1-P9) | RL curriculum/replay (trainer loop NOT RUN, K3) |
| P10 | full suite + phase tests | 148 passed | 108 passed (P1-P10) | differential privacy |
| P11 | full suite + phase tests | 148 passed | 110 passed (P1-P11) | evidence chain |
| P12 | full suite + phase tests | 148 passed | 111 passed (P1-P12) | regression/drift labels |
| P13 | full suite + phase tests | 148 passed | 114 passed (P1-P13) + UI smoke | API/SSE/frontend |
| P14 | full suite + phase tests | 148 passed | 114 passed | docker compose sandbox-pg (Docker NOT RUN) |
| P15 | full suite + phase tests | 148 passed | 115 passed | benchmark lab |
| P16 | full suite + phase tests | 148 passed | 115 passed | final audit |
