# Diff review (presentation-only justification)

dashboard/components.py — new stylesheet and display helpers (brand, group_label, section, page_header,
summary_strip, activity_html, capability_panel, icon); existing helpers keep names/signatures; colours updated for
the light theme; all dynamic strings html-escaped. No backend calls.
dashboard/plots.py — template/colours/fonts/grid only; bottleneck text marker added to labels. Node selection,
edges, costs, sorting, series data and axis types unchanged.
dashboard/app.py — sidebar wrapped in containers (call order unchanged); header + grid + keyed panels; inputs
indented under `with _work:` (lines unchanged except label_visibility, section headings and column ratios);
run_pipeline: tree_box target + render call only; report rendering moved into slots with identical conditions and
values; tabs inside a keyed panel, labels without emoji; deployment code blocks in two columns; badge colours.
dashboard/upgrade_ui.py — group label, source header markup, "rows (estimated)" column label, upload caption
(size limit) + steps line + visible uploader label, Ask-your-database heading + visible label + column ratios,
danger-area container around delete controls. Requests, payloads, state assignments and gates unchanged.
.streamlit/config.toml — [theme] and new [theme.sidebar] only; [server]/[browser] unchanged.
tests/frontend/* — new QA tooling (harness, screenshots, synthetic fixture). Original tests untouched.
