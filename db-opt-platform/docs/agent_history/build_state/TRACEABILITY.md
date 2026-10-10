# TRACEABILITY - PS requirement -> implementation -> test -> verification

The authoritative matrix with demo evidence and limitations is
`docs/problem_statement_traceability.md`. This file adds the build-state view of the addendum.

| Requirement | Implementation | Test path | Evidence | Status |
|---|---|---|---|---|
| Secure anonymised ingestion | app/ingestion.py, app/masking_vault.py | tests/test_ingestion.py | VERIFY #16 | INTEGRATED |
| Zero raw-data exposure to AI | app/llm_guard.py, app/llm.py | tests/test_masking.py, tests/test_agents.py::test_mocked_llm_payload_is_anonymised_and_validated | guard blocks + audit | INTEGRATED |
| Composite-index recommendation | app/agents/index_strategist.py | tests/test_agents.py | VERIFY #14 (scenario B) | INTEGRATED |
| Partitioning/sharding | app/partition_advisor.py | tests/test_research_modules.py | advisory label | INTEGRATED |
| Automated SQL rewriting | app/agents/sql_rewriter.py | tests/test_agents.py | scenario C/D | INTEGRATED |
| Execution-tree explainability (GNN) | app/gnn/* | tests/test_gnn.py | VERIFY #8 | INTEGRATED |
| Reinforcement learning | app/rl/* | tests/test_rl.py | VERIFY #9 | INTEGRATED |
| PostgreSQL simulation (HypoPG) | app/sandbox.py | tests/test_sandbox.py, tests/test_integration.py | VERIFY #14, #13 | INTEGRATED |
| Interactive DBA dashboard | dashboard/* | Playwright smoke | VERIFY #21 | INTEGRATED |
| Evidence-backed optimisation | app/evidence_engine.py | tests/test_research_modules.py::test_evidence_chain_kinds | report evidence_chain | INTEGRATED |
| Safe pre-deployment experimentation | app/sandbox.py, app/benchmark.py, app/migration_generator.py | tests/test_sandbox.py | VERIFY #11-13 | INTEGRATED |
| R1 workload intelligence | app/workload_store.py | tests/test_core.py::test_workload_store_context | context_for() in reports | INTEGRATED |
| R2 plan regression | app/regression_detector.py | tests/test_research_modules.py::test_plan_regression_requires_evidence | VERIFY #17 | INTEGRATED |
| R3 predicate intelligence | app/predicate_intelligence.py | tests/test_research_modules.py::test_predicate_intelligence_* | access_pattern in reports | INTEGRATED |
| R4 index hygiene (non-destructive) | app/index_hygiene.py | tests/test_research_modules.py::test_index_hygiene_is_report_only | /api/v1/hygiene | INTEGRATED |
| R5 cardinality (never invents rows) | app/cardinality_analyzer.py | tests/test_research_modules.py::test_cardinality_* | schema_expert.cardinality_analysis | INTEGRATED |
| R6 SQL semantic diff before deployment scripts | app/sql_semantic_diff.py | tests/test_research_modules.py::test_semantic_diff_detects_changes | rewrite.semantic_diff | INTEGRATED |
| R7 hierarchical RL + masking + workload weighting | app/rl/environment.py, app/rl/agent.py | tests/test_rl.py::test_invalid_action_masking, ::test_reward_components_and_workload_weight | masked_actions in reports | INTEGRATED |
| R8 drift measured, not fabricated | app/workload_drift.py | tests/test_research_modules.py::test_workload_drift_measured_not_fabricated | VERIFY #17 | INTEGRATED |
| R9 budgets enforced | app/optimization_budget.py | tests/test_core.py::test_budget_enforced_and_reported | report.budget | INTEGRATED |
| R10 capability firewall | app/capability_firewall.py | tests/test_core.py::test_capability_firewall | CAPABILITY_DENIED audit | INTEGRATED |
| R11 evidence chain | app/evidence_engine.py | tests/test_research_modules.py::test_evidence_chain_kinds | report.evidence_chain | INTEGRATED |
| R12 benchmark + ablation (estimate vs measured) | app/benchmark.py | tests/test_api.py::test_optimize_contract | VERIFY #10-12 | INTEGRATED |
| R13 NL incident retrieval (secondary) | app/agents/nl_intent.py::similar_incidents | API live run | VERIFY #18 | IMPLEMENTED (heuristic) |
| R14 clean-room implementation | all modules | - | no third-party repository code copied | VERIFIED |
