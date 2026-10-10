# CONTRACTS - cross-module interfaces

All structured contracts are Pydantic models in `app/contracts.py` (single source of truth).

| Contract | Producer | Consumers | Key fields |
|---|---|---|---|
| `PrivacyResult` (returned as dict by `DataObfuscator.mask_sql`) | `masking_vault.py` | pipeline, API `/mask`, ingestion | masked_sql, ast_signature, literal_count, mapped_tables, mapped_columns, fallback_used, quarantined, quarantine_reason, privacy_bitmask, privacy_flags, privacy_audit{pii_detected, pii_types, literal_leak_detected, secret_leak_detected, safe_for_llm} |
| `SchemaMetadata` / `TableMeta` / `ColumnMeta` / `IndexMeta` / `ForeignKeyMeta` | `schema_inspector.py` | validator, agents (pseudonymised copy), blast radius, partition advisor | tables{name: TableMeta}, indexes[], foreign_keys[]; ColumnMeta.top_value_freq is a frequency only |
| `PlanAnalysis` / `PlanNode` | `plan_parser.py` | GNN, agents, sandbox, evidence | nodes[node_id, parent_id, depth, node_type, costs, plan_rows, exclusive_cost, estimated_loops, effective_cost, relation_name, filter, index_cond, …], edges[(p,c)], operator_histogram, highest_cost_node, seq_scans, plan_fingerprint, plan_shape, sanitized |
| `GNNDiagnosis` | `gnn/analyzer.py` | supervisor, API, dashboard | primary_bottleneck_type, bottleneck_class_id, confidence (float or "rule:<label>"), class_probabilities, highest_cost_node, natural_language_summary, graph_nodes, graph_edges, model_mode ∈ {trained, analytic_fallback}, evidence, fallback_reason |
| `IndexCandidate` | index strategist / LLM | RL actions, validator, sandbox | table, columns, kind ∈ {single, composite, partial, covering}, include_columns, where_clause, ddl (pseudonymised), reason, evidence, source, signature, roles |
| `RewriteProposal` | `agents/sql_rewriter.py` | merge, RL, validator | rewritten_masked_sql, rules_applied, reasoning, semantic_diff, semantics_verified, requires_human_review, source |
| `PartitionAdvice` / `ShardingAdvice` | `partition_advisor.py` | schema expert, RL, migration notes | strategy_type, table, candidate_key, rationale, evidence, expected_benefit, operational_risks, validation_required, validated=False, label |
| `LLMRecommendation` (Section 28, `extra=forbid`) | `llm.py` | rewriter / strategist | rewritten_sql, proposed_indexes[{ddl, reason, columns}], partitioning_recommendation, sharding_recommendation, technical_reasoning, assumptions, risks, confidence∈[0,1] |
| `AgentRecommendation` | `supervisor_merge` | RL, validator, report | rewritten_sql, rewrite, proposed_indexes, partitioning_recommendation, sharding_recommendation, extended_statistics, technical_reasoning, assumptions, risks, confidence, llm |
| `RLState` (dataclass) | `rl/state_encoder.py` | agent, policy, env | discretised fields; key() 'bc0|cb4|…'; coarse_key() |
| `LowAction` / `StepOutcome` / `EpisodeContext` | `rl/environment.py` | agent, trainer, policy, episode builder | high ∈ {ADD_INDEX, REWRITE_SQL, PARTITION, SHARD_ADVISORY, NO_CHANGE}, signature, payload, redundant, verified |
| `RLRecommendation` | `rl/policy.py` | supervisor, API | policy_mode ∈ {trained_policy, analytic_fallback}, state_key, high_level_action, low_level_action, selected_candidate, q_values, valid_actions, masked_actions, explanation, retraining_recommended |
| `ValidationOutcome` | `recommendation_mapper.py` | sandbox, migration generator | candidate, valid, real_ddl (trusted only), errors, warnings |
| `SandboxResult` (Section 31) | `sandbox.py` | blast radius, report | before_total_cost, after_total_cost, planner_cost_reduction_pct, virtual_indexes_used, estimated_storage_impact_mb, estimated_write_overhead, per_candidate, rewrite_* costs, combination_note, status, cleanup_ok, metric_label |
| `BlastRadiusResult` (Section 33) | `blast_radius.py` | report | target_table, write_queries_analyzed, write_frequency_summary, estimated_write_impact, estimated_storage_impact_mb, risk_level ∈ {low, medium, high}, methodology |
| `DeploymentPlan` | `migration_generator.py` | report, API, dashboard | migration_id, migration_sql, rollback_sql, requires_human_review=True, generated_at, rationale, query_fingerprint, approval_status, advisory_notes |
| `EvidenceItem` | `evidence_engine.py` | report, dashboard | step ∈ {OBSERVATION, EVIDENCE, INTERPRETATION, RECOMMENDATION, SANDBOX_RESULT, BLAST_RADIUS_RESULT, DEPLOYMENT_RISK}, source_type, kind ∈ {observed, inferred, simulated, estimated, benchmark-measured}, statement, data |
| `AuditEvent` | `audit.py` | optimizer_meta.audit_events, API | request_id, event_type, stage, severity, details (sanitised), timestamp |
| `StreamEvent` (Section 38) | `events.py` | SSE, dashboard | event, timestamp, request_id, stage, message, data |
| `FinalOptimizationReport` (Section 67) | `final_report` node | API, dashboard, persistence | request_id, query_fingerprint, privacy_audit, diagnosis, optimization, validation{hypopg_result, planner_cost_reduction_pct, measured_execution_time_reduction_pct}, blast_radius, deployment, evidence_chain, explanation, model_modes, budget, workload_context, limitations |
| `WorkloadRecord` (R1) | `ingestion.py` | workload store, regression, drift, NL incidents | query_fingerprint, plan_fingerprint, plan_shape, timestamp_bucket, call_count, mean_exec_time_ms, estimated_cost, estimated_rows, actual_rows, operator_histogram, access_features, join/sort/index_features, table_size_bucket, write_frequency_bucket, anonymized_sql, source, recommendation_outcome |
| `QSState` (LangGraph TypedDict) | `agents/state.py` | all graph nodes | Section 22 keys + agent_status (reducer), agent_logs (reducer), route, error, llm_calls |

API request/response schemas: `docs/api.md`. Database objects: `scripts/init_db.sql`.
