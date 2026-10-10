# Contracts

Recorded with tests/frontend/contract_harness.py (AppTest + httpx recording) before any edit
(contract_baseline.json) and after (contract_after.json); compared with tests/frontend/compare_contracts.py.

| scenario | calls before | calls after | identical |
|---|---|---|---|
| initial | 7 | 7 | yes |
| find_workload (/nl/ask) | 22 | 22 | yes |
| all_tabs (demo mode off) | 14 | 14 | yes |
| upload_mode | 14 | 14 | yes |
| dataset_source | 14 | 14 | yes |
| demo_run (/optimize/async + /stream + /report) | 397 | 397 | yes (request id normalised) |
| ask_db (/nlq/ask) | 29 | 29 | yes |
| run_sql (/nlq/run) | 29 | 29 | yes |

Not clicked (write actions): /data/commit, DELETE /data/datasets/{id}, /nlq/apply-index. For these, every request,
payload and session-state assignment line in app.py and upgrade_ui.py was diffed against commit d1d2317: identical.
UpgradeClient, session_id, source_for_sql, _delete_sources, EVENT_TO_AGENT, SKIP_HINTS, AGENTS and session-state
initialisation are byte-identical. /data/preview was exercised in the browser with a synthetic CSV (no writes).
Pre-existing (unchanged): pasting SQL while the demo source is active makes source_for_sql fetch every uploaded
source's schema (374 GETs with many test datasets) — noted, not changed (frontend-only task).
