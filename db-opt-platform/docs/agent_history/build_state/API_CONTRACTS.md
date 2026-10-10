# API_CONTRACTS

Error envelope (existing): `{"error": <category>, "message": str, "stage": str|null, "request_id"?: str, "details"?: {}}`.
Auth (existing): optional `X-API-Key` when QS_API_KEY is set.

## Existing endpoints (must not change)
| Method | Path | Request | Response (top-level keys) |
|---|---|---|---|
| GET | /api/v1/health | - | status, postgresql, hypopg, pg_stat_statements (503 when degraded) |
| GET | /api/v1/metrics, /metrics/prometheus | - | metrics snapshot / text |
| GET | /api/v1/status | - | component status dict |
| POST | /api/v1/mask | {sql, request_id?} | request_id, masked output, note |
| POST | /api/v1/analyze | {sql, request_id?} | request_id, privacy_audit, schema_analysis, plan_analysis, graph, gnn_analysis, access_pattern, workload_context, regression |
| POST | /api/v1/optimize | {sql, request_id?} | full report (request_id, status, privacy_audit, ..., answer, zero_exposure_proof, ...) 200/400/500 |
| POST | /api/v1/optimize/async | {sql} | request_id, stream_url, report_url |
| GET | /api/v1/report/{id} | - | report or 202 running |
| GET | /api/v1/stream/{id} | - | SSE |
| GET | /api/v1/audit/{id} | - | request_id, events |
| POST | /api/v1/ingest/logs, /ingest/plans | {format, content?, records?} | ingestion report |
| POST | /api/v1/ingest/pg_stat_statements | {limit, min_mean_ms} | ingestion report |
| GET | /api/v1/workload | - | summary, top_fingerprints, regressions, drift |
| GET | /api/v1/hygiene | - | hygiene report |
| POST | /api/v1/benchmark | {sql?, demo_query_index?, variants?, measure} | request_id, results |
| GET | /api/v1/examples | - | examples |
| POST | /api/v1/nl/ask | {question} | NL intent candidates |
| POST | /api/v1/nl/analyze | {candidate_id} | as optimize/async |

## New endpoints
(added per phase below)

## New endpoints (Final Upgrade P13)
Headers: `X-Session-Id` (8-64 [A-Za-z0-9-]) = ownership, not authentication. Uploads: raw request body + `filename` query param.
| Method | Path | Request | Response / errors |
|---|---|---|---|
| GET | /api/v1/upgrade/status | - | feature_flags, model_modes, search_budget_limits, differential_privacy, sandbox_server, provenance_tags, raw_data_exposed_to_ai |
| GET | /api/v1/sources | session | sources[] (demo + own dynamic/sandbox) |
| GET | /api/v1/sources/{id} | session | public view / source_not_found, source_forbidden, sandbox_expired |
| GET | /api/v1/sources/{id}/schema | session | tables with columns, stats, keys, provenance |
| POST | /api/v1/data/preview?filename&dataset_name&entity_name | body=file, session required | preview_id, detected_format, columns, plan, warnings / upload_rejected |
| POST | /api/v1/data/commit | {preview_id, allow_duplicate, allow_widening} | run_id, data_source_id, table, schema_version, rows_* / schema_conflict(409), upload_rejected |
| GET | /api/v1/data/datasets, /api/v1/data/runs?data_source_id | session | lists |
| POST | /api/v1/byod/verify | body=schema | verification report (verified, schema_objects, rejected_statements, unsupported_features, normalized_statements, warnings, how_to_fix) |
| POST | /api/v1/sandboxes?scale&name | body=schema, session | sandbox + verification + synthetic_data / upload_rejected, quota_exceeded(429), sandbox_unavailable(503) |
| GET/POST/DELETE | /api/v1/sandboxes, /{id}, /{id}/extend, /{id} | session | sandbox views / sandbox_expired(410), quota_exceeded |
| POST | /api/v1/nlq/ask | {question, data_source_id?, optimize, execute, anchor_date?} | 10 sections / sql_rejected(422, details.stage), llm errors |
| POST | /api/v1/nlq/ask/async | same | run_id, stream_url, report_url; SSE NLQ_STARTED..NLQ_COMPLETE |
| POST | /api/v1/nlq/validate | {sql, data_source_id?} | stages_passed, final_sql, plan cost |
| POST | /api/v1/nlq/optimize | {sql, data_source_id?} | optimizer summary with component_trace |
| POST | /api/v1/nlq/apply-index | {sql, ddl, data_source_id} (sandbox/dynamic only) | MEASURED SANDBOX timings / source_forbidden on demo, search_budget_exhausted |
| GET | /api/v1/index-portfolio?data_source_id | session, flag | actions / feature_disabled(404) |
