# VERIFY - exact verification commands and their last results

Environment: Linux x86_64, Python 3.13.16, PostgreSQL 16.15 (Ubuntu), HypoPG 1.4.0,
pg_stat_statements 1.10 (`shared_preload_libraries = 'pg_stat_statements'`), CPU only.
Dataset: FULL mode - 100 tenants / 1,000,000 orders / 3,000,000 order_items (seed 42).
Date of final run: 2026-10-03.

| # | Command | Result |
|---|---|---|
| 1 | `python -m compileall -q app dashboard scripts tests` | OK (no errors) |
| 2 | `pytest -q` (with live DB reachable) | **146 passed** (140 offline + 6 integration) |
| 3 | `pytest -q -m "not integration"` | 137 passed (fixtures captured from the demo DB) |
| 4 | `docker compose config --quiet` (with a .env derived from .env.example) | OK |
| 5 | `docker pull postgres:16-bookworm` / `python:3.12-slim` | **NOT POSSIBLE in build sandbox**: registry-1.docker.io returned 403 via the egress proxy. Images were not built or started here. |
| 6 | `python scripts/seed_data.py --full` | 1,000,000 orders + 3,000,000 items in 68.1 s, ANALYZE complete |
| 7 | `python scripts/generate_workload.py --export-examples` | 120 reads + 600 writes (rolled back); 48 history records with live plans exported |
| 8 | `python scripts/train_gnn.py --real-plans --epochs 80` | best val 1.0, held-out 1.0, unseen plan-shape variants 0.835, live-plan agreement with rules 4/5 |
| 9 | `python scripts/train_rl.py` | 800 episodes; seen reward 0.599 vs fallback 0.512; unseen reward 0.767 vs fallback 0.511; validity 1.0 |
| 10 | `python scripts/run_benchmark.py` | all 5 scenarios x 12 variants; e.g. C full = 99.96 %, index_only 99.98 %, rewrite_only 99.9 % (planner) |
| 11 | `BENCHMARK_ENABLED=true BENCHMARK_ADMIN_DSN=… python scripts/run_benchmark.py --measure --query 1` | measured median 57.321 → 30.014 ms (−47.64 %); indexes built in rolled-back txn |
| 12 | same, `--query 3` | measured median 44.304 → 0.009 ms (−99.98 %) |
| 13 | post-benchmark `SELECT indexname FROM pg_indexes WHERE schemaname='public'` | only the 6 original indexes (no leftovers) |
| 14 | `uvicorn app.api:app` + `POST /api/v1/optimize` for scenarios A-E | all `completed`; GNN `trained`, RL `trained_policy`; planner −72.78 / −21.32 / −99.98 / −99.91 % / none; 0 ERROR log lines |
| 15 | `POST /api/v1/optimize/async` + `curl -N /api/v1/stream/{id}` | 27 SSE events REQUEST_RECEIVED … FINAL_REPORT_READY |
| 16 | `POST /api/v1/ingest/plans` (sample_history.json) | 48 accepted, 0 quarantined, 36 PII-anonymised, 48 persisted to optimizer_meta.query_history |
| 17 | `GET /api/v1/workload` | regressions detected (PLAN_REGRESSION +36.88 % cost etc.); drift measured (plan_fingerprints JS 0.71) |
| 18 | `POST /api/v1/nl/ask` "weekly sales reporting dashboard timing out" | top candidate = date_trunc weekly report statement, with cited evidence |
| 19 | `optimizer_meta` row counts after runs | optimization_runs, audit_events, migrations, query_history populated; security rejections persisted with severity=security |
| 20 | Least privilege (psql as qs_app) | INSERT into tenants → permission denied; CREATE INDEX on orders → must be owner; hypopg_create_index OK |
| 21 | `streamlit run dashboard/app.py` + Playwright (Chromium headless): load scenario C, run, open 9 tabs | 0 Streamlit exceptions, 0 console errors; screenshots in docs/screenshots/ |
| 22 | Manifest check (82 required paths) + import of every app/dashboard module + `--help` of every script | 0 missing, 0 import failures, all scripts OK |

| 23 | Upgrade run (2026-10-03, full dataset re-seeded): `pytest -q` | **146 passed** |
| 24 | `POST /api/v1/optimize` scenarios A-E after upgrade | all completed; answer sentence + write latency ms + partition simulation + zero-exposure proof present; no `qs_sim%` relations left |
| 25 | Playwright: NL question "weekly sales reporting dashboard timing out" -> analyse -> answer (composite index orders(tenant_id, order_date), planner -98 %); demo mode ON (5 tabs) and OFF (9 tabs), every tab opened | 0 exceptions, 0 console errors |
| 26 | Bug fixed: EXPLAIN (GENERIC_PLAN) for $n workload statements now runs without bound parameters (DO block); before, asyncpg-bound NULLs produced a near-zero custom plan | generic cost now matches psql (10,098) |

Not verified (stated honestly):
- Docker image build / container start (registry blocked in sandbox) - item 5.
- Real external LLM calls (Gemini/OpenAI) - only the mocked provider was exercised; no API key available.
- Redis vault backend - code path present, not exercised (redis not installed).
- Measured benchmark for scenario C (baseline runtime too long for the sandbox).
