"""Reusable Streamlit components: status bar, badges, agent tree, evidence chain, tables.

V3 "light peach glass" presentation layer: one app-owned stylesheet (CSS), plus small HTML display helpers
(page header, summary strip, dark activity panel, capability list). Helpers only render data they are given;
they never call the backend. Every dynamic string is html-escaped.
"""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

# status colours (text label always shown next to the colour)
STATUS_COLORS = {"QUEUED": "#6B6F76", "RUNNING": "#18243A", "COMPLETED": "#1D654D", "SKIPPED": "#6B6F76",
                 "REJECTED": "#805308", "ERROR": "#AC2F3E"}
KIND_COLORS = {"observed": "#1D654D", "inferred": "#6E4F7A", "simulated": "#18243A", "estimated": "#805308",
               "benchmark-measured": "#A64F20"}

CSS = """
<style>
:root{
 --qs-navy:#18243A; --qs-text:#162238; --qs-sec:#5C626B; --qs-help:#4F535A; --qs-accent:#D78F5D;
 --qs-orange:#A64F20; --qs-mauve:#AF939F; --qs-sep:#D8D5D0; --qs-read:#FAFAF8; --qs-pop:#FCFBF9;
 --qs-green:#1D654D; --qs-amber:#805308; --qs-red:#AC2F3E; --qs-fallback:#F1EEEA;
 --qs-shadow:0 10px 30px rgba(55,42,31,.06);
}
/* ---------- layer 1: static warm canvas (no images, no animation) ---------- */
.stApp{
 background:
  radial-gradient(900px 520px at 0% 100%, rgba(244,214,158,.38), rgba(244,214,158,0) 62%),
  linear-gradient(100deg,#E6B899 0%,#EBCDB6 18%,#E8E1D8 46%,#D3D1CF 72%,#BEBFC0 100%);
 background-attachment:fixed; color:var(--qs-text);
}
[data-testid="stHeader"]{background:transparent}
[data-testid="stDecoration"]{display:none}
/* ---------- layer 2: frosted outer shell ---------- */
[data-testid="stMainBlockContainer"]{
 max-width:1440px; width:min(90%,1440px); margin:24px auto 32px auto; padding:26px 32px 40px 32px;
 background:rgba(247,247,245,.44); border:1.5px solid rgba(255,255,255,.70); border-radius:20px;
 -webkit-backdrop-filter:blur(22px) saturate(110%); backdrop-filter:blur(22px) saturate(110%);
 box-shadow:var(--qs-shadow), inset 0 1px 0 rgba(255,255,255,.65);
}
/* sidebar: narrow translucent column (a native, collapsible Streamlit sidebar) */
[data-testid="stSidebar"]{background:transparent; border-right:none}
[data-testid="stSidebarContent"]{
 margin:24px 0 24px 18px; border-radius:20px; background:rgba(247,247,245,.40);
 border:1.5px solid rgba(255,255,255,.70);
 -webkit-backdrop-filter:blur(16px) saturate(110%); backdrop-filter:blur(16px) saturate(110%);
 box-shadow:var(--qs-shadow); height:calc(100% - 48px);
}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding-top:4px}
/* main panels (keyed native containers) */
[class*="st-key-qs_glass"]{
 background:rgba(255,255,255,.58)!important; border:1px solid rgba(255,255,255,.88)!important;
 border-radius:14px!important; box-shadow:var(--qs-shadow), inset 0 1px 0 rgba(255,255,255,.65);
 -webkit-backdrop-filter:blur(16px) saturate(110%); backdrop-filter:blur(16px) saturate(110%);
 padding:18px 20px!important; transition:border-color .16s ease;
}
[class*="st-key-qs_glass"]:focus-within{border-color:#765337!important}
/* nested panels inside a glass panel are solid reading surfaces (no stacked blur) */
[class*="st-key-qs_glass"] [data-testid="stVerticalBlockBorderWrapper"],
[class*="st-key-qs_glass"] [data-testid="stExpander"] details{
 background:var(--qs-read); border-color:var(--qs-sep)!important; border-radius:10px;
 -webkit-backdrop-filter:none; backdrop-filter:none;
}
/* ---------- layer 3: reading interiors ---------- */
[data-testid="stCode"], .stCode, [data-testid="stCodeBlock"]{border:1px solid var(--qs-sep); border-radius:10px}
[data-testid="stDataFrame"]{border:1px solid var(--qs-sep); border-radius:10px; background:var(--qs-read)}
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"]>div{
 background:var(--qs-read)!important; border-color:var(--qs-sep)!important;
}
.stApp textarea, .stApp input, [data-testid="stTextAreaRootElement"]{background:var(--qs-read)!important;
 color:var(--qs-text)}
[data-baseweb="popover"] ul, [data-baseweb="menu"]{background:var(--qs-pop)!important}
[data-testid="stFileUploaderDropzone"]{background:var(--qs-read); border:1.5px dashed #C9B7A6; border-radius:12px}
/* visible keyboard focus on native controls */
.stApp button:focus-visible, .stApp input:focus-visible, .stApp textarea:focus-visible,
.stApp [role="tab"]:focus-visible, .stApp [role="switch"]:focus-visible, .stApp summary:focus-visible,
.stApp [role="radio"]:focus-visible, .stApp [role="checkbox"]:focus-visible{
 outline:2px solid var(--qs-navy)!important; outline-offset:2px;
}
.stApp button{min-height:38px; transition:background-color .16s ease, border-color .16s ease}
/* tabs as a quiet segmented strip */
[data-testid="stTabs"] [role="tablist"]{gap:4px; background:rgba(255,255,255,.55); border:1px solid rgba(255,255,255,.9);
 border-radius:12px; padding:4px; flex-wrap:wrap; height:auto; overflow:visible}
[data-testid="stTab"]{border-radius:9px; padding:6px 14px!important; height:auto!important; border-bottom:none!important;
 color:var(--qs-sec); transition:background-color .16s ease}
[data-testid="stTab"]:hover{background:rgba(255,255,255,.7); color:var(--qs-text)}
[data-testid="stTab"][aria-selected="true"]{background:#FFFFFF; color:var(--qs-text); box-shadow:0 1px 4px rgba(55,42,31,.10)}
[data-testid="stTab"]::after{display:none!important}
[data-testid="stCaptionContainer"]{opacity:1!important}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p{color:var(--qs-help)!important}
[data-testid="stMetricValue"]{font-variant-numeric:tabular-nums; color:var(--qs-text)}
[data-testid="stMetricLabel"] p{color:var(--qs-sec)}
/* ---------- helpers ---------- */
.qs-brand{display:flex; align-items:center; gap:10px; margin:6px 0 2px 0}
.qs-brand .mark{width:34px; height:34px; border-radius:10px; display:grid; place-items:center;
 background:linear-gradient(140deg,#D78F5D,#A64F20); color:#fff; font-weight:700; font-size:13px;
 box-shadow:0 4px 12px rgba(166,79,32,.25)}
.qs-brand .name{font-weight:700; font-size:16px; color:var(--qs-text)}
.qs-brand-sub{font-size:12.5px; color:var(--qs-help); margin:6px 0 4px 0; line-height:1.45}
.qs-group{font-size:12px; color:var(--qs-help); margin:14px 0 4px 2px; letter-spacing:.02em}
.qs-head{display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap;
 margin:0 0 14px 0}
.qs-head h1{font-size:34px; font-weight:600; color:var(--qs-text); margin:0; padding:0; line-height:1.15;
 letter-spacing:-.01em}
.qs-head .ctx{font-size:12.5px; color:var(--qs-sec); margin-top:2px}
.qs-head .lede{font-size:14px; color:var(--qs-sec); margin-top:6px}
.qs-source{display:flex; align-items:center; gap:10px; background:rgba(255,255,255,.66);
 border:1px solid rgba(255,255,255,.92); border-radius:14px; padding:8px 14px 8px 8px;
 box-shadow:var(--qs-shadow); max-width:100%}
.qs-source .ic{width:32px; height:32px; border-radius:50%; background:#fff; display:grid; place-items:center;
 box-shadow:0 1px 4px rgba(55,42,31,.12)}
.qs-source .t{font-size:13.5px; font-weight:600; color:var(--qs-text); overflow-wrap:anywhere}
.qs-source .s{font-size:12px; color:var(--qs-sec)}
.qs-strip{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; padding:16px 18px;
 background:rgba(255,255,255,.58); border:1px solid rgba(255,255,255,.88); border-radius:14px;
 box-shadow:var(--qs-shadow), inset 0 1px 0 rgba(255,255,255,.65);
 -webkit-backdrop-filter:blur(16px) saturate(110%); backdrop-filter:blur(16px) saturate(110%); margin-bottom:16px}
.qs-tile{display:flex; gap:10px; align-items:flex-start; min-width:0}
.qs-ico{flex:0 0 36px; width:36px; height:36px; border-radius:50%; background:#fff; display:grid; place-items:center;
 box-shadow:0 1px 4px rgba(55,42,31,.12)}
.qs-tl{font-size:12.5px; color:var(--qs-sec); line-height:1.3}
.qs-tv{font-size:19px; font-weight:650; color:var(--qs-text); font-variant-numeric:tabular-nums; line-height:1.35;
 overflow-wrap:anywhere}
.qs-tn{font-size:11.5px; color:var(--qs-help)}
.qs-strip-empty{grid-column:1/-1; font-size:13.5px; color:var(--qs-sec)}
.qs-section{font-size:20px; font-weight:600; color:var(--qs-text); margin:0 0 2px 0}
.qs-section-sub{font-size:13px; color:var(--qs-sec); margin:0 0 10px 0}
/* dark activity panel (the single intentionally dark surface) */
.qs-activity{background:#1B1B1C; color:#FAFAF9; border-radius:14px; padding:20px 22px 18px 22px;
 box-shadow:0 18px 40px rgba(30,20,12,.28); position:relative; overflow:hidden; margin-bottom:16px}
.qs-activity::before{content:""; position:absolute; left:0; right:0; top:0; height:1px;
 background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.35),rgba(255,255,255,0))}
.qs-activity h3{font-size:20px; font-weight:600; color:#FAFAF9; margin:0 0 4px 0; padding:0}
.qs-activity .rid{font-size:12px; color:#C6C4C1; margin-bottom:12px; overflow-wrap:anywhere}
.qs-activity ol{list-style:none; margin:0; padding:0 0 0 2px; border-left:1px solid #3A3A3C}
.qs-activity li{position:relative; padding:4px 0 6px 18px; font-size:13.5px; display:flex;
 justify-content:space-between; gap:10px}
.qs-activity li::before{content:""; position:absolute; left:-4px; top:11px; width:7px; height:7px; border-radius:50%;
 background:#C6C4C1}
.qs-activity li.st-COMPLETED::before{background:#7FD1AE} .qs-activity li.st-RUNNING::before{background:#F2B48A}
.qs-activity li.st-ERROR::before{background:#F08A97} .qs-activity li.st-REJECTED::before{background:#E9C46A}
.qs-activity .lab{font-size:11.5px; font-weight:600; letter-spacing:.03em; color:#C6C4C1; white-space:nowrap}
.qs-activity li.st-COMPLETED .lab{color:#9FE0C3} .qs-activity li.st-RUNNING .lab{color:#F6C7A6}
.qs-activity li.st-ERROR .lab{color:#F6A9B3} .qs-activity li.st-REJECTED .lab{color:#EFD38E}
.qs-activity .ev{margin-top:12px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px;
 color:#C6C4C1; line-height:1.55; max-height:160px; overflow:auto}
.qs-activity .empty{font-size:13.5px; color:#C6C4C1; margin:2px 0 12px 0}
/* capability / provenance facts (Working-format area) */
.qs-facts h3{font-size:20px; font-weight:600; color:var(--qs-text); margin:2px 0 10px 0; padding:0}
.qs-factgrid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px}
.qs-fact{display:flex; flex-direction:column; gap:1px; padding:9px 12px; border-radius:12px;
 border:1px solid rgba(255,255,255,.9);
 background:linear-gradient(90deg,rgba(255,255,255,.62),rgba(255,255,255,.30))}
.qs-fact .k{font-size:12.5px; color:var(--qs-sec)} .qs-fact .v{font-size:14px; font-weight:600; color:var(--qs-text);
 overflow-wrap:anywhere}
.qs-fact .st{font-size:12.5px; font-weight:650; white-space:nowrap}
.qs-fact.ok .st{color:var(--qs-green)} .qs-fact.warn .st{color:var(--qs-amber)} .qs-fact.bad .st{color:var(--qs-red)}
.qs-fact.ok{background:linear-gradient(90deg,rgba(255,255,255,.62),rgba(29,101,77,.07))}
.qs-fact.warn{background:linear-gradient(90deg,rgba(255,255,255,.62),rgba(215,143,93,.16))}
.qs-fact.bad{background:linear-gradient(90deg,rgba(255,255,255,.62),rgba(172,47,62,.12))}
/* existing helper classes, light versions */
.qs-chip{display:inline-block; padding:4px 10px; margin:2px 4px 2px 0; border-radius:12px; font-size:12px;
 font-weight:600; border:1px solid rgba(255,255,255,.9)}
.qs-ok{background:rgba(29,101,77,.10); color:var(--qs-green)} .qs-bad{background:rgba(172,47,62,.10); color:var(--qs-red)}
.qs-warn{background:rgba(128,83,8,.10); color:var(--qs-amber)}
.qs-badge{display:inline-block; padding:2px 8px; border-radius:8px; font-size:11px; font-weight:700; color:#FFFFFF}
.qs-label{font-size:12px; letter-spacing:.05em; text-transform:uppercase; color:var(--qs-sec); margin:6px 0 4px 0;
 font-weight:600}
.qs-sensitive{border-left:4px solid var(--qs-red); padding-left:8px} .qs-safe{border-left:4px solid var(--qs-green); padding-left:8px}
.qs-tree{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; line-height:1.9; color:var(--qs-text);
 background:var(--qs-read); border:1px solid var(--qs-sep); border-radius:10px; padding:10px 14px}
.qs-advisory{background:#FBF1E6; border:1px solid #E8C9AC; color:#5A3A1E; padding:8px 12px; border-radius:10px}
.qs-log{font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12.5px; line-height:1.6; color:var(--qs-text)}
.qs-sub{color:var(--qs-sec); font-size:14px; margin:-4px 0 10px 0}
.qs-answer{background:#FFFFFF; border:1px solid rgba(255,255,255,.95); border-left:4px solid var(--qs-accent);
 border-radius:12px; padding:16px 18px; margin:4px 0 8px 0; font-size:16px; line-height:1.6; color:var(--qs-text);
 box-shadow:var(--qs-shadow)}
.qs-answer .t{font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--qs-orange); font-weight:700;
 margin-bottom:6px}
.qs-explain{background:rgba(255,255,255,.62); border:1px solid rgba(255,255,255,.9); border-left:3px solid var(--qs-accent);
 border-radius:10px; padding:9px 13px; margin:2px 0 12px 0; font-size:13.5px; color:var(--qs-sec)}
.qs-shield{display:inline-block; margin-top:8px; padding:3px 10px; border-radius:12px; background:rgba(29,101,77,.10);
 color:var(--qs-green); font-size:12px; font-weight:700}
.qs-srcname{font-size:18px; font-weight:600; color:var(--qs-text); margin-top:4px}
.qs-srcmeta{font-size:13px; color:var(--qs-sec); margin:2px 0 10px 0; line-height:1.9}
.qs-srcmeta code{font-size:12px; color:var(--qs-text); background:var(--qs-read); border:1px solid var(--qs-sep);
 border-radius:6px; padding:1px 6px}
.qs-steps-line{font-size:13px; color:var(--qs-sec); margin:4px 0 8px 0}
.qs-steps-line b{display:inline-grid; place-items:center; width:20px; height:20px; border-radius:50%; background:#fff;
 color:var(--qs-navy); font-size:11.5px; box-shadow:0 1px 3px rgba(55,42,31,.15); margin-right:4px}
.qs-steps-line span{margin:0 6px; color:#9A948C}
.st-key-qs_danger{border-color:rgba(172,47,62,.35)!important; background:#FFF7F6!important}
.qs-danger-t{font-weight:650; color:var(--qs-red); font-size:14px}
@media (max-width:1560px){ .qs-strip{grid-template-columns:repeat(2,minmax(0,1fr)); row-gap:16px} }
/* responsive: tablet stacks the right column after the work area; phone uses one column */
@media (max-width:1100px){ [data-testid="stMainBlockContainer"]{width:94%; padding:22px 22px 32px 22px} }
@media (max-width:900px){
 [class*="st-key-qs_grid"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap}
 [class*="st-key-qs_grid"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{flex:1 1 100%!important; width:100%!important; min-width:100%!important}
 .qs-strip{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:640px){
 [data-testid="stMainBlockContainer"]{width:calc(100% - 24px); margin:12px auto; padding:48px 14px 28px 14px; border-radius:16px}
 .qs-head h1{font-size:28px}
 .qs-strip{grid-template-columns:1fr}
 [class*="st-key-qs_glass"]{padding:14px 12px!important; -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px)}
 [data-testid="stSidebarContent"]{margin:12px; height:calc(100% - 24px)}
}
/* fallbacks */
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
 [data-testid="stMainBlockContainer"], [data-testid="stSidebarContent"], [class*="st-key-qs_glass"], .qs-strip{background:var(--qs-fallback)!important}
}
@media (prefers-reduced-transparency:reduce){
 [data-testid="stMainBlockContainer"], [data-testid="stSidebarContent"], [class*="st-key-qs_glass"], .qs-strip{
  background:var(--qs-fallback)!important; -webkit-backdrop-filter:none!important; backdrop-filter:none!important}
}
@media (prefers-reduced-motion:reduce){ [class*="st-key-qs_glass"], .stApp button{transition:none!important} }
@media (forced-colors:active){
 [data-testid="stMainBlockContainer"], [data-testid="stSidebarContent"], [class*="st-key-qs_glass"], .qs-strip,
 .qs-activity, .qs-fact, .qs-answer, .qs-source{background:Canvas!important; color:CanvasText!important;
  border:1px solid CanvasText!important; box-shadow:none!important; -webkit-backdrop-filter:none!important;
  backdrop-filter:none!important}
}
</style>
"""

# small inline SVG glyphs for the white icon holders (local, no network, decorative -> aria-hidden)
_ICON = {
    "cost": '<path d="M4 15a8 8 0 1 1 16 0" fill="none" stroke="#A64F20" stroke-width="2" stroke-linecap="round"/>'
            '<path d="M12 15l4-5" stroke="#18243A" stroke-width="2" stroke-linecap="round"/>',
    "write": '<circle cx="12" cy="12" r="8" fill="none" stroke="#A64F20" stroke-width="2"/>'
             '<path d="M12 7v5l3 2" fill="none" stroke="#18243A" stroke-width="2" stroke-linecap="round"/>',
    "storage": '<ellipse cx="12" cy="6.5" rx="7" ry="2.8" fill="none" stroke="#A64F20" stroke-width="2"/>'
               '<path d="M5 6.5v11c0 1.6 3.1 2.8 7 2.8s7-1.2 7-2.8v-11" fill="none" stroke="#18243A" stroke-width="2"/>',
    "shield": '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z" fill="none" stroke="#A64F20" stroke-width="2"/>'
              '<path d="M9 12l2 2 4-4" fill="none" stroke="#18243A" stroke-width="2" stroke-linecap="round"/>',
    "db": '<ellipse cx="12" cy="6.5" rx="7" ry="2.8" fill="none" stroke="#18243A" stroke-width="2"/>'
          '<path d="M5 6.5v11c0 1.6 3.1 2.8 7 2.8s7-1.2 7-2.8v-11M5 12c0 1.6 3.1 2.8 7 2.8s7-1.2 7-2.8" fill="none" '
          'stroke="#A64F20" stroke-width="2"/>',
}

AGENT_LABELS = {"supervisor": "Supervisor", "sql_rewriter": "SQL rewriter", "schema_expert": "Schema expert",
                "index_strategist": "Index strategist", "rl_optimizer": "RL optimizer",
                "recommendation_validator": "Recommendation validator", "hypopg_sandbox": "HypoPG simulation",
                "blast_radius": "Blast radius", "final_report": "Final report"}


def icon(name: str, size: int = 18) -> str:
    return (f'<svg aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 24 24">{_ICON.get(name, "")}'
            "</svg>")


def fmt_sql(sql: str | None) -> str | None:
    """Display-only line breaks before major clauses (does not change the SQL)."""
    if not sql:
        return sql
    import re
    out = re.sub(r"\s+(FROM|WHERE|LEFT JOIN|INNER JOIN|JOIN|GROUP BY|ORDER BY|LIMIT|HAVING)\s+", r"\n\1 ", sql)
    return re.sub(r"\s+(AND|OR)\s+", r"\n  \1 ", out)


def compact(v: float | None) -> str:
    if v is None:
        return "n/a"
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(v) >= div:
            return f"{v / div:.2f}{suf}"
    return f"{v:.2f}"


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ V3 layout helpers (display only)
def brand() -> None:
    st.markdown('<div class="qs-brand"><div class="mark" aria-hidden="true">QS</div>'
                '<div class="name">QuerySentinel</div></div>'
                '<div class="qs-brand-sub">PostgreSQL query analysis. Suggests fixes; nothing changes until a '
                'person approves.</div>', unsafe_allow_html=True)


def group_label(text: str) -> None:
    st.markdown(f'<div class="qs-group">{html.escape(text)}</div>', unsafe_allow_html=True)


def section(title: str, sub: str = "") -> None:
    st.markdown(f'<div class="qs-section">{html.escape(title)}</div>'
                + (f'<div class="qs-section-sub">{html.escape(sub)}</div>' if sub else ""), unsafe_allow_html=True)


def page_header(source: dict | None) -> None:
    """Dashboard title + truthful current-source context (no user account, no avatar)."""
    src = source or {}
    kind = {"demo": "Demo database", "dynamic": "Uploaded dataset"}.get(src.get("kind", "demo"), src.get("kind", ""))
    st.markdown(
        '<div class="qs-head"><div><div class="ctx">QuerySentinel · PostgreSQL query analysis</div>'
        '<h1>Dashboard</h1><div class="lede">Inspect query plans, compare recommendations, and review the '
        'evidence.</div></div>'
        f'<div class="qs-source" title="active data source id: {html.escape(str(src.get("id", "demo")))}">'
        f'<div class="ic">{icon("db", 18)}</div><div><div class="t">{html.escape(str(src.get("name", "Demo Database")))}'
        f'</div><div class="s">{html.escape(kind)} · {html.escape(str(src.get("id", "demo")))}</div></div></div></div>',
        unsafe_allow_html=True)


def summary_strip(tiles: list[dict] | None) -> None:
    """Shared metric strip. tiles=None -> neutral pre-run description (no invented numbers)."""
    if not tiles:
        st.markdown('<div class="qs-strip" role="group" aria-label="Report summary"><div class="qs-strip-empty">'
                    'No report yet. Run the optimisation pipeline to see the planner cost change, extra write time, '
                    'index storage and raw-data exposure for your query.</div></div>', unsafe_allow_html=True)
        return
    cells = "".join(
        f'<div class="qs-tile" title="{html.escape(t.get("help") or "")}"><div class="qs-ico">{icon(t["icon"])}</div>'
        f'<div><div class="qs-tl">{html.escape(t["label"])}</div><div class="qs-tv">{html.escape(str(t["value"]))}</div>'
        f'<div class="qs-tn">{html.escape(t.get("note", ""))}</div></div></div>' for t in tiles)
    st.markdown(f'<div class="qs-strip" role="group" aria-label="Report summary">{cells}</div>',
                unsafe_allow_html=True)


def activity_html(statuses: dict[str, str], events: list[dict], request_id: str | None = None,
                  started: bool = True) -> str:
    """Dark pipeline-activity card from existing agent statuses and SSE events (escaped)."""
    rows = "".join(
        f'<li class="st-{html.escape(statuses.get(a, "QUEUED"))}"><span>{html.escape(lab)}</span>'
        f'<span class="lab">{html.escape(statuses.get(a, "QUEUED").title())}</span></li>'
        for a, lab in AGENT_LABELS.items())
    head = ('<h3>Pipeline activity</h3>'
            + (f'<div class="rid">run {html.escape(request_id)}</div>' if request_id else ""))
    if not started:
        return (f'<div class="qs-activity" role="region" aria-label="Pipeline activity">{head}'
                '<div class="empty">No run started. Stages appear here when you run the optimisation '
                f'pipeline.</div><ol>{rows}</ol></div>')
    ev = "".join(f'<div>[{html.escape((e.get("timestamp") or "")[11:19])}] {html.escape(str(e.get("message") or ""))}</div>'
                 for e in events[-6:])
    return (f'<div class="qs-activity" role="region" aria-label="Pipeline activity">{head}<ol>{rows}</ol>'
            + (f'<div class="ev" aria-label="latest events">{ev}</div>' if ev else "") + "</div>")


def capability_panel(status: dict | None, error: str | None = None) -> None:
    """Capability facts from the REAL /api/v1/status response (same states as status_bar)."""
    if status is None:
        st.markdown('<div class="qs-facts"><h3>Capabilities</h3><div class="qs-fact bad"><div><div class="k">Backend'
                    f'</div><div class="v">Unreachable</div></div><span class="st">{html.escape(error or "unavailable")}'
                    '</span></div></div>', unsafe_allow_html=True)
        return

    def ok(key):
        return bool((status.get(key) or {}).get("ok"))
    pg, gnn, rl, llm = (status.get(k, {}) or {} for k in ("postgresql", "gnn", "rl", "llm"))
    facts = [
        ("PostgreSQL", (pg.get("version", "") or "-").split(" (")[0], "ok" if ok("postgresql") else "bad",
         "Online" if ok("postgresql") else "Unavailable"),
        ("HypoPG", str((status.get("hypopg") or {}).get("version", "") or "-"), "ok" if ok("hypopg") else "bad",
         "Online" if ok("hypopg") else "Unavailable"),
        ("pg_stat_statements", "workload statistics", "ok" if ok("pg_stat_statements") else "bad",
         "Online" if ok("pg_stat_statements") else "Unavailable"),
        ("Privacy vault", (status.get("privacy_vault") or {}).get("backend", "?"), "ok" if ok("privacy_vault") else "bad",
         "Online" if ok("privacy_vault") else "Unavailable"),
        ("GNN", gnn.get("mode", "?"), "ok" if gnn.get("mode") == "trained" else "warn",
         "Trained" if gnn.get("mode") == "trained" else "Fallback"),
        ("RL", rl.get("mode", "?"), "ok" if rl.get("mode") == "trained_policy" else "warn",
         "Trained" if rl.get("mode") == "trained_policy" else "Fallback"),
        ("LLM", llm.get("provider", "none") + (f"/{llm.get('model')}" if llm.get("enabled") else ""),
         "ok" if llm.get("enabled") else "warn", "Enabled" if llm.get("enabled") else "Disabled"),
        ("LangGraph", "agent orchestration", "ok" if ok("langgraph") else "bad",
         "Online" if ok("langgraph") else "Unavailable"),
    ]
    rows = "".join(f'<div class="qs-fact {c}"><div class="k">{html.escape(k)}</div><div class="v">'
                   f'{html.escape(str(v))}</div><span class="st">{html.escape(s)}</span></div>'
                   for k, v, c, s in facts)
    st.markdown(f'<div class="qs-facts" role="region" aria-label="Capabilities"><h3>Capabilities</h3>'
                f'<div class="qs-factgrid">{rows}</div>'
                '<div class="qs-tn" style="margin-top:8px">From the backend status check on this page load. '
                'LLM disabled is normal: everything runs locally.</div></div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ existing helpers (restyled)
def chip(label: str, state: str, detail: str = "") -> str:
    cls = {"ok": "qs-ok", "bad": "qs-bad", "warn": "qs-warn"}[state]
    tip = f' title="{html.escape(detail)}"' if detail else ""
    return f'<span class="qs-chip {cls}"{tip}>{html.escape(label)}</span>'


def status_bar(status: dict | None, error: str | None = None) -> None:
    """Top status bar from REAL backend responses (Section 42) - no fake indicators."""
    if status is None:
        st.markdown(chip(f"Backend unreachable: {error or ''}", "bad"), unsafe_allow_html=True)
        return
    def ok(key):
        return bool((status.get(key) or {}).get("ok"))
    pg = status.get("postgresql", {})
    gnn = status.get("gnn", {})
    rl = status.get("rl", {})
    llm = status.get("llm", {})
    chips = [
        chip(f"PostgreSQL {pg.get('version', '')}".strip(), "ok" if ok("postgresql") else "bad", pg.get("error", "")),
        chip("HypoPG " + str((status.get('hypopg') or {}).get('version', '')), "ok" if ok("hypopg") else "bad"),
        chip("pg_stat_statements", "ok" if ok("pg_stat_statements") else "bad"),
        chip(f"Privacy Vault ({(status.get('privacy_vault') or {}).get('backend', '?')})", "ok" if ok("privacy_vault") else "bad"),
        chip(f"LLM: {llm.get('provider', 'none')}" + (f"/{llm.get('model')}" if llm.get('enabled') else " (disabled)"),
             "ok" if llm.get("enabled") else "warn"),
        chip(f"GNN: {gnn.get('mode', '?')}", "ok" if gnn.get("mode") == "trained" else "warn", str(gnn.get("error") or "")),
        chip(f"RL: {rl.get('mode', '?')}", "ok" if rl.get("mode") == "trained_policy" else "warn", str(rl.get("error") or "")),
        chip("LangGraph", "ok" if ok("langgraph") else "bad"),
    ]
    st.markdown("".join(chips), unsafe_allow_html=True)


def badge(text: str, color: str) -> str:
    return f'<span class="qs-badge" style="background:{color}">{html.escape(text)}</span>'


def agent_tree(statuses: dict[str, str]) -> None:
    def s(name: str) -> str:
        v = statuses.get(name, "QUEUED")
        return badge(v, STATUS_COLORS.get(v, "#6B6F76"))
    lines = [
        f"Supervisor {s('supervisor')}",
        "│",
        f"├── SQL Rewriter {s('sql_rewriter')}",
        f"├── Schema Expert {s('schema_expert')}",
        f"├── Index Strategist {s('index_strategist')}",
        "│",
        f"├── RL Optimizer {s('rl_optimizer')}",
        f"├── Recommendation Validator {s('recommendation_validator')}",
        "│",
        f"├── HypoPG {s('hypopg_sandbox')}",
        "│",
        f"└── Blast Radius {s('blast_radius')}",
        f"&nbsp;&nbsp;&nbsp;&nbsp;└── Final Report {s('final_report')}",
    ]
    st.markdown('<div class="qs-tree">' + "<br>".join(lines) + "</div>", unsafe_allow_html=True)


def labeled_code(label: str, code: str | None, css: str = "", language: str = "sql") -> None:
    st.markdown(f'<div class="qs-label {css}">{html.escape(label)}</div>', unsafe_allow_html=True)
    st.code((fmt_sql(code) if language == "sql" else code) or "(none)", language=language)


def evidence_chain(items: list[dict[str, Any]]) -> None:
    if not items:
        st.info("No evidence chain available.")
        return
    for it in items:
        k = it.get("kind", "inferred")
        st.markdown(f"{badge(it.get('step', ''), '#5C626B')} {badge(k, KIND_COLORS.get(k, '#6B6F76'))} "
                    f"<span style='color:#5C626B;font-size:12px'>source: {html.escape(str(it.get('source_type')))}</span><br>"
                    f"{html.escape(str(it.get('statement')))}", unsafe_allow_html=True)


def advisory(text: str) -> None:
    st.markdown(f'<div class="qs-advisory">{html.escape(text)}</div>', unsafe_allow_html=True)


def explain(text: str) -> None:
    """Plain-language 'what am I looking at' note at the top of a tab."""
    st.markdown(f'<div class="qs-explain">{text}</div>', unsafe_allow_html=True)


def answer_card(sentence: str, safe: bool | None) -> None:
    shield = '<div class="qs-shield">Zero raw data exposed to AI</div>' if safe else ""
    st.markdown(f'<div class="qs-answer"><div class="t">Answer</div>{html.escape(sentence)}{shield}</div>',
                unsafe_allow_html=True)
