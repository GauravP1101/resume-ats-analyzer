# ui_enhancements.py
from __future__ import annotations
import math
from typing import Optional

# -------------------- Color-aware, accessible SVG gauge --------------------
def score_badge(
    score: float,
    label: Optional[str] = None,          # optional: override label
    subtitle: Optional[str] = None        # optional: small hint under label
) -> str:
    """
    Circular gauge with color-aware ring, ARIA labels, and better dark/color-blind handling.
    Backward compatible with score_badge(score) calls from app.py.
    """
    score = max(0.0, min(100.0, float(score)))

    # Color-blind friendly shades (red/orange/green that work in dark & light)
    # Thresholds designed for your calibrated scale (<=50: Needs Work, <75: Okay Match).
    if score < 50:
        color = "#e24a33"  # cb-safe red
        auto_label = "Needs Work"
    elif score < 75:
        color = "#ed9f2d"  # cb-safe orange/amber
        auto_label = "Okay Match"
    else:
        color = "#2aa876"  # cb-safe green
        auto_label = "Strong Fit"

    label = label or auto_label
    subtitle = subtitle or "Calibrated ATS score • Skills-weighted + Semantics"

    radius, stroke = 56, 10
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100.0)

    # Extra contrast ring for dark mode + focus state for keyboard users
    return f"""
    <div class="score-wrap" role="group" aria-label="ATS score">
      <svg width="140" height="140" viewBox="0 0 140 140" role="img"
           aria-label="ATS score gauge {score:.0f} percent">
        <title>ATS Match {score:.0f}%</title>
        <desc>Higher is better. This score blends semantic similarity and weighted skill coverage.</desc>
        <circle cx="70" cy="70" r="{radius}" fill="none"
                stroke="var(--gauge-track)" stroke-width="{stroke}" />
        <circle cx="70" cy="70" r="{radius}" fill="none"
                stroke="{color}" stroke-width="{stroke}" stroke-linecap="round"
                stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                transform="rotate(-90 70 70)"/>
        <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
              class="score-val" style="fill:{color};">{score:.0f}%</text>
      </svg>
      <div>
        <div class="h2">ATS Match Score</div>
        <div class="score-label" style="color:{color};">{label}</div>
        <div class="hint">{subtitle}</div>
      </div>
    </div>
    """

# -------------------- Small UI atoms --------------------
def pill(text: str, ok: bool, title: Optional[str] = None) -> str:
    """
    Skill pill with improved contrast and optional tooltip (title).
    Backward compatible with pill(text, ok) calls.
    """
    bg = "var(--pill-ok-bg)" if ok else "var(--pill-miss-bg)"
    fg = "var(--pill-ok-fg)" if ok else "var(--pill-miss-fg)"
    border = "var(--pill-border)"
    title_attr = f" title='{_esc_attr(title)}'" if title else ""
    return (
        f"<span class='pill' style='background:{bg};color:{fg};border:1px solid {border};'"
        f"{title_attr}>{_esc_html(text)}</span>"
    )

# Optional helpers (you can ignore if not needed)
def meter(label: str, value_pct: float, hint: Optional[str] = None) -> str:
    """
    Compact horizontal meter (for showing coverage vs similarity, etc.)
    """
    v = max(0.0, min(100.0, float(value_pct)))
    return f"""
    <div class="meter" role="group" aria-label="{_esc_attr(label)} {v:.0f}%">
      <div class="meter-head">
        <div class="meter-label">{_esc_html(label)}</div>
        <div class="meter-val">{v:.0f}%</div>
      </div>
      <div class="meter-track"><div class="meter-fill" style="width:{v:.0f}%"></div></div>
      {f"<div class='hint'>{_esc_html(hint)}</div>" if hint else ""}
    </div>
    """

def stat_row(items: list[tuple[str, str]]) -> str:
    """
    Simple two-column stat row: [(label, value), ...]
    """
    cells = "".join(
        f"<div class='stat'><div class='stat-k'>{_esc_html(k)}</div><div class='stat-v'>{_esc_html(v)}</div></div>"
        for k, v in items
    )
    return f"<div class='stat-row'>{cells}</div>"

# -------------------- Global CSS (light + dark) --------------------
def base_css() -> str:
    """
    Clean, accessible palette + thin borders + distinctive result backgrounds.
    Adds: focus styles, reduced motion support, scrollbar polish, gauge track var,
    color-blind friendly tweaks. Backward compatible with your app.py layout.
    """
    return """
    <style>
      /* --------- Palette --------- */
      :root{
        /* light theme */
        --bg: #f6f7fb;               /* page background */
        --panel: #ffffff;            /* cards / form panels */
        --panel-alt: #f8fafc;        /* result/preview background */
        --text: #0f172a;             /* slate-900 */
        --muted: #64748b;            /* slate-500 */
        --brand: #4f46e5;            /* indigo-600 */
        --border: #e2e8f0;           /* slate-200 */
        --shadow: 0 8px 24px rgba(15,23,42,.06);

        --pill-ok-bg:#d1fae5;        /* emerald-100 */
        --pill-ok-fg:#065f46;        /* emerald-900 */
        --pill-miss-bg:#fee2e2;      /* red-100 */
        --pill-miss-fg:#991b1b;      /* red-800 */
        --pill-border: rgba(0,0,0,.06);

        --gauge-track: #e5e7eb;      /* neutral track */

        /* meters */
        --meter-track: #e5e7eb;
        --meter-fill: #4f46e5;

        /* stat */
        --stat-k: #64748b;
        --stat-v: #0f172a;

        /* focus ring */
        --focus: 0 0 0 3px rgba(79,70,229,.35);
      }

      @media (prefers-color-scheme: dark){
        :root{
          --bg: #0b1220;             /* deep slate */
          --panel: #121a2b;          /* card */
          --panel-alt: #0f182a;      /* result bg (slightly different) */
          --text: #e6eaf3;
          --muted: #9aa7bf;
          --brand: #8ea2ff;
          --border: #26314a;         /* thin, not glaring white */
          --shadow: 0 6px 20px rgba(0,0,0,.35);

          --pill-ok-bg:#0a2e25;
          --pill-ok-fg:#7ee4c4;
          --pill-miss-bg:#321519;
          --pill-miss-fg:#ffb3ba;
          --pill-border: rgba(255,255,255,.06);

          --gauge-track: #1d2740;

          --meter-track: #223150;
          --meter-fill: #8ea2ff;

          --stat-k: #9aa7bf;
          --stat-v: #e6eaf3;
        }
      }

      /* --------- Reduced motion --------- */
      @media (prefers-reduced-motion: reduce) {
        * { animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; transition: none !important; }
      }

      /* --------- Base typography & container --------- */
      .gradio-container{
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Ubuntu, Cantarell, Helvetica Neue, Arial;
        background: var(--bg) !important;
        color: var(--text);
      }
      .wrap { max-width: 1150px; margin: 0 auto; padding: 0 10px; }

      .h1 { font: 800 28px/1.2 Inter, system-ui; letter-spacing:-0.01em; color: var(--text); }
      .h2 { font: 700 18px/1.2 Inter, system-ui; color: var(--text); }
      .hint { color: var(--muted); font: 400 13px/1.3 Inter, system-ui; }

      /* --------- Cards / Panels --------- */
      .card{
        background: var(--panel);
        border: 1px solid var(--border) !important;
        border-radius: 14px;
        box-shadow: var(--shadow);
        padding: 18px;
      }
      .gr-panel, .gr-box, .gr-group{
        background: var(--panel) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        box-shadow: var(--shadow) !important;
      }

      /* --------- Upload box & Textarea --------- */
      .upload-box .wrap{
        border: 1.5px dashed var(--border);
        border-radius: 12px;
        padding: 20px;
        transition: border .15s ease, background .15s ease;
        background: transparent;
      }
      .upload-box .wrap:hover{
        border-color: var(--brand);
        background: color-mix(in srgb, var(--panel) 92%, var(--brand) 8%);
      }
      .textarea textarea{
        min-height: 270px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        background: var(--panel-alt) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
      }
      .textarea textarea:focus{
        outline: none !important;
        box-shadow: var(--focus);
        border-color: transparent !important;
      }

      /* --------- Tabs polish --------- */
      .tabs .tabitem{ padding:6px 0 0; }
      .tabs button[role="tab"]{
        font-weight: 600;
        border-radius: 10px !important;
      }
      .tabs button[role="tab"]:focus-visible{
        box-shadow: var(--focus);
        outline: none;
      }

      /* --------- Buttons --------- */
      .btn-lg button{
        font-weight:700; font-size:16px; padding:12px 16px;
        background: var(--brand);
        border: 1px solid transparent;
        border-radius: 12px !important;
      }
      .btn-lg button:hover{ filter: brightness(0.95); }
      .btn-lg button:focus-visible{ box-shadow: var(--focus); outline: none; }

      /* --------- Result blocks --------- */
      .result-card{
        background: var(--panel-alt);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
      }
      .score-wrap{ display:flex; align-items:center; gap:18px; }
      .score-val{ font: 800 24px Inter, system-ui; }

      /* --------- Pills --------- */
      .pill{
        display:inline-block;
        margin:4px 6px 0 0;
        padding:6px 10px;
        border-radius:9999px;
        font:600 12px Inter, system-ui;
        transition: transform .15s ease;
      }
      .pill:hover{ transform: translateY(-1px); }

      /* --------- Previews --------- */
      pre{
        background: var(--panel-alt) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        overflow:auto;
      }

      /* --------- Meters --------- */
      .meter{ margin-top:10px; }
      .meter-head{ display:flex; justify-content:space-between; margin-bottom:6px; }
      .meter-label{ font: 600 13px Inter, system-ui; color: var(--text); }
      .meter-val{ font: 700 13px Inter, system-ui; color: var(--text); }
      .meter-track{
        height:10px; border-radius:9999px; background: var(--meter-track); overflow:hidden;
        border: 1px solid var(--border);
      }
      .meter-fill{ height:100%; background: var(--meter-fill); }

      /* --------- Stats --------- */
      .stat-row{
        display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 10px; margin-top: 10px;
      }
      .stat{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 10px 12px;
      }
      .stat-k{ color: var(--stat-k); font: 600 12px Inter, system-ui; }
      .stat-v{ color: var(--stat-v); font: 700 14px Inter, system-ui; }

      /* --------- Scrollbar (webkit) --------- */
      ::-webkit-scrollbar{ height: 10px; width: 10px; }
      ::-webkit-scrollbar-track{ background: transparent; }
      ::-webkit-scrollbar-thumb{ background: rgba(100,116,139,.35); border-radius: 8px; }
      ::-webkit-scrollbar-thumb:hover{ background: rgba(100,116,139,.55); }
    </style>
    """

# -------------------- internal escapes --------------------
def _esc_html(s: str | None) -> str:
    if s is None:
        return ""
    return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

def _esc_attr(s: str | None) -> str:
    if s is None:
        return ""
    # quotes also need escaping for attributes
    return (_esc_html(s).replace('"', "&quot;").replace("'", "&#39;"))
