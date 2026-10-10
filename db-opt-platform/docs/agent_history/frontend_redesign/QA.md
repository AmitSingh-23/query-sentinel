# QA

Checks run
- python syntax/import (ast) + ruff F on dashboard: pass
- existing test suite: 232 passed (live local PostgreSQL + HypoPG)
- contract harness: 8 scenarios identical (CONTRACTS.md)
- protected hashes: only .streamlit/config.toml changed (theme tables); added tests/frontend/* only
- screenshots (Playwright, Chromium): final_* initial/report/askdb at 1280x820, 1440x900, 1024x768, 768x1024,
  390x844 (viewport + full height); c1_view_1..9 all nine views after a demo run; state_upload_preview_1280,
  state_rejected_1280 (synthetic fixture / invalid table)
- contrast (computed on the peachiest composite): body text 11.2:1; secondary 5.3:1; helper 5.3:1; orange 5.6:1;
  activity secondary 9.9:1; status labels >= 5.7:1

Not run / limitations
- write actions (commit, delete, apply-index) not executed in QA; code paths diffed instead
- Docker image not rebuilt here; the user rebuilds with `docker compose up --build`
- 200% zoom, forced-colors and reduced-transparency checked by CSS review only, not on a real device
- native limits: Streamlit's sidebar is fixed outside the main block, so the sidebar is a separate glass column
  next to the shell rather than inside it; the toolbar ("Deploy", menu) floats above the shell; dataframes are
  canvas-rendered (theme colours only); captions inherit theme fonts
- pre-existing: privacy metric "Outgoing LLM check" truncates to "BLOCK..." in 5 narrow columns
