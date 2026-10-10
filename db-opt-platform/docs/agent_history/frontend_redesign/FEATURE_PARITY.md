# Feature parity checklist (all reachable after the redesign)

- [x] Connection settings (backend URL, API key) — sidebar, bottom
- [x] Data source selector, Demo / Upload mode, session id caption
- [x] Demo scenarios + Load scenario; Demo mode toggle (5 core / all 9 views)
- [x] Find workload (/nl/ask), candidate cards, Analyze this candidate (/nl/analyze)
- [x] Slow SQL input, source-routing notice, Run optimisation pipeline (demo + uploaded-source paths)
- [x] Live SSE progress (status box + log + activity card), report polling, rejection/error + suggestions + 42P01 hint
- [x] Auto-correction notes + corrected SQL
- [x] Answer card, metric note, four summary metrics
- [x] Source panel (name, kind, status, schema v, id, provenance, tables, example SQL)
- [x] Delete active dataset (confirmation gate); upload (preview, warnings, conflicts, duplicate/widening, commit)
- [x] Uploaded-dataset table + multi-select delete with confirmation (danger area)
- [x] Ask Your Database: question, Optimize toggle, Ask, run own SQL (+Optimize), clarification, warnings, anchored
      rerun, 10 sections, apply-index (uploaded only), 200-row result slice, truncation label
- [x] Nine views: Privacy Audit, Execution Plan / GNN (+GATv2), AI Agents, Optimization, Simulation (HypoPG),
      Deployment Review (+3 downloads), Evidence Chain, Workload History (ingest, pg_stat_statements, hygiene),
      Benchmark Lab
