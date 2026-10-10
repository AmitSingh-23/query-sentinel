# Frontend redesign — STATE

Objective: V3 "Light Peach Glass" presentation-only redesign of the Streamlit dashboard
(QuerySentinel_Light_Glass_V3_Claude_Master_Prompt.pdf). Backend, models, API contracts unchanged.
Selected reference: references/selected-interface.png (extracted from the V3 PDF page 1, 1279x818).
Superseded: V2 Midnight Glass, V1 charcoal — not used.

## Milestones
- [x] A — inventory, git checkpoint d1d2317, PROTECTED_HASHES.json (699 files), contract baseline
      (contract_baseline.json, 8 scenarios), before screenshots (screenshots/before_*)
- [x] B — material system (CSS, theme, components) + main composition
- [x] C — datasets / Ask Your Database / nine detail views
- [x] D — syntax, tests (232 passed), contracts identical, hashes ok
- [x] E — final screenshots at 5 viewports, QA notes

## Editable files
dashboard/components.py, dashboard/plots.py (styling only), dashboard/app.py + dashboard/upgrade_ui.py (rendering
only), .streamlit/config.toml [theme] only, tests/frontend/**, .frontend_redesign/**.

## Commands
- stack: /home/claude/start_stack.sh (local postgres + backend :8000, QA only)
- dashboard: BACKEND_URL=http://localhost:8000 streamlit run dashboard/app.py --server.port 8501
- contracts: BACKEND_URL=http://localhost:8000 python3 tests/frontend/contract_harness.py <out.json>
- screenshots: python3 tests/frontend/screens.py <tag> initial report upload

## Next
Done. Handoff delivered; user rebuilds with docker compose up --build.

## Progress log
- B done: CSS material system (components.py), light theme (config.toml [theme] only), page header, summary
  strip, dark activity card (live via run_pipeline tree_box), capability facts, keyed glass panels, Plotly light.
- C in progress: all nine views captured (screenshots/c1_view_*); deployment side-by-side; emoji headings removed.
