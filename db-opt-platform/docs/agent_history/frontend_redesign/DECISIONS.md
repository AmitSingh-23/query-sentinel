# Decisions (V3 light peach glass)

1. Reference: references/selected-interface.png (from the V3 PDF). V1/V2 directions not used.
2. Glass on native Streamlit only: keyed containers (`st.container(key="qs_glass_*")` -> app-owned class
   `st-key-qs_glass_*`), the main block container (outer shell) and the sidebar content (narrow glass column).
   No generated emotion classes are targeted. No new framework, server, proxy or dependency.
3. Composition: header (title + truthful source context, top right) -> grid 62/38: left = summary strip + work panel
   (answer / workload search / slow SQL); right = dark "Pipeline activity" card + "Capabilities" facts.
   Full-width data panel (source/schema, upload, dataset management, Ask Your Database) and the Details panel below.
   The data panel is full width (not inside the 62% column) so Ask Your Database results stay readable.
4. Live run: run_pipeline's `tree_box` now points at the dark activity card (`activity_slot`) and renders
   `ui.activity_html(...)` instead of `ui.agent_tree(...)`. Event mapping, callbacks, polling, ordering unchanged.
   After the run the card shows the report's authoritative `agent_status` (falls back to session agent_status).
5. Containers keep the original call order (sidebar connection inputs are created first but displayed last;
   strip/answer slots are filled after the report is known) so no request or state assignment moved.
6. Summary strip: same four values and formatting as the previous st.metric row (HTML tiles, help text kept as
   tooltip). Before a report: a neutral description, no numbers.
7. Capabilities = the old status chips (same /api/v1/status response, same ok/warn/bad rules) as labelled facts.
8. Plotly: plotly_white, light ivory plot area, warm orange / muted mauve data, red + "BOTTLENECK"/"(bottleneck)"
   text marker for the bottleneck. Data, sorting and existing log scales unchanged.
9. Helper text darkened to #4F535A (screenshot grey fails AA on the peach edge: 3.8:1 -> 5.3:1).
10. Labels of the two main inputs and Ask-your-database are visible (were collapsed); same label text/keys.
11. Emoji removed from tab labels and two headings (presentation). Deployment migration/rollback side by side.
