# ui_enhancements.py
from __future__ import annotations
import math
from typing import Optional

# -------------------- Color-aware, accessible SVG gauge --------------------
def score_badge(
    score: float,
    label: Optional[str] = None,          # optional label override
    subtitle: Optional[str] = None        # optional hint under the label
) -> str:
    """
    Circular gauge with accessible contrast, color-blind friendly hues,
    and clean typography. Backward compatible with score_badge(score).
    """
    score = max(0.0, min(100.0, float(score)))

    # Thresholds tuned for your calibrated scoring
    if score < 50:
        tone = "danger"
        auto_label = "Needs Work"
    elif score < 75:
        tone = "warning"
        auto_label = "Okay Match"
    else:
        tone = "success"
        auto_label = "Strong Fit"

    label = label or auto_label
    subtitle = subtitle or "Calibrated ATS score • Skills-weighted + Semantics"

    radius, stroke = 56, 11
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100.0)

    # Use CSS variables so colors adapt to light/dark automatically
    # Gradient is subtle and falls back to solid stroke if not supported
    return f"""
    <div class="score-wrap" role="group" aria-label="ATS score">
      <svg width="140" height="140" viewBox="0 0 140 140" role="img"
           aria-label="ATS score gauge {score:.0f} percent">
        <title>ATS Match {score:.0f}%</title>
        <desc>Higher is better. This score blends semantic similarity and weighted skill coverage.</desc>
        <defs>
          <linearGradient id="gauge-{tone}" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%"  stop-color="var(--tone-{tone}-a)"/>
            <stop offset="100%" stop-color="var(--tone-{tone}-b)"/>
          </linearGradient>
        </defs>
        <circle cx="70" cy="70" r="{radius}" fill="none"
                stroke="var(--gauge-track)" stroke-width="{stroke}" />
        <circle cx="70" cy="70" r="{radius}" fill="none"
                stroke="url(#gauge-{tone})"
                stroke-width="{stroke}" stroke-linecap="round"
                stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                transform="rotate(-90 70 70)"/>
        <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
              class="score-val">{score:.0f}%</text>
      </svg>
      <div class="score-meta">
        <div class="h2">ATS Match Score</div>
        <div class="score-label tone-{tone}">{label}</div>
        <div class="hint">{subtitle}</div>
      </div>
    </div>
    """

# -------------------- Small UI atoms --------------------
def pill(text: str, ok: bool, title: Optional[str] = None) -> str:
    """
    Skill pill with improved contrast and optional tooltip.
    Backward compatible with pill(text, ok).
    """
    tone = "ok" if ok else "miss"
    title_attr = f" title='{_esc_attr(title)}'" if title else ""
    return (
        f"<span class='pill pill-{tone}'{title_attr}>{_esc_html(text)}</span>"
    )

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

# -------------------- Global CSS (light + dark, hi-contrast) --------------------
def base_css() -> str:
    """
    Refined palette, spacing, typography, and component polish.
    - Color system with brand/success/warn/danger
    - Dark mode + reduced motion + high-contrast support
    - Softer shadows & subtle borders
    - Cleaner inputs, tabs, buttons, cards
    """
    return """
    <style>
      /* --------- Design tokens --------- */
      :root{
        /* Light theme neutrals */
        --bg:          #f6f7fb;
        --panel:       #ffffff;
        --panel-alt:   #f8fafc;
        --text:        #0f172a;   /* slate-900 */
        --muted:       #64748b;   /* slate-500 */
        --border:      #e5e7eb;   /* slate-200 */
        --shadow:      0 10px 28px rgba(15,23,42,.06);

        /* Brand */
        --brand:       #4f46e5;   /* indigo-600 */
        --brand-weak:  #eef2ff;   /* indigo-50 */

        /* Status tones (color-blind friendly) */
        --tone-success:   #2aa876;
        --tone-success-a: #2aa876;
        --tone-success-b: #45c39b;

        --tone-warning:   #ed9f2d;
        --tone-warning-a: #f2a93f;
        --tone-warning-b: #e3881e;

        --tone-danger:    #e24a33;
        --tone-danger-a:  #e24a33;
        --tone-danger-b:  #ff6a4f;

        --gauge-track:    #e5e7eb;

        /* Pills */
        --pill-ok-bg:   #d1fae5;  /* emerald-100 */
        --pill-ok-fg:   #065f46;
        --pill-miss-bg: #fee2e2;  /* red-100 */
        --pill-miss-fg: #991b1b;
        --pill-border:  rgba(0,0,0,.06);

        /* Meters */
        --meter-track:  #e5e7eb;
        --meter-fill:   var(--brand);

        /* Stats */
        --stat-k:       #64748b;
        --stat-v:       #0f172a;

        /* Focus ring */
        --focus:        0 0 0 3px rgba(79,70,229,.35);
      }

      @media (prefers-color-scheme: dark){
        :root{
          --bg:          #0b1220;
          --panel:       #111827;  /* slate-900ish */
          --panel-alt:   #0f182a;
          --text:        #e6eaf3;
          --muted:       #9aa7bf;
          --border:      #26314a;
          --shadow:      0 8px 24px rgba(0,0,0,.35);

          --brand:       #8ea2ff;
          --brand-weak:  #101739;

          --tone-success:   #76e4bf;
          --tone-success-a: #76e4bf;
          --tone-success-b: #3fcaa2;

          --tone-warning:   #f2c35b;
          --tone-warning-a: #f2c35b;
          --tone-warning-b: #e5a83d;

          --tone-danger:    #ff8a7a;
          --tone-danger-a:  #ff8a7a;
          --tone-danger-b:  #ff6a5a;

          --gauge-track:    #1d2740;

          --pill-ok-bg:   #0a2e25;
          --pill-ok-fg:   #7ee4c4;
          --pill-miss-bg: #321519;
          --pill-miss-fg: #ffb3ba;
          --pill-border:  rgba(255,255,255,.06);

          --meter-track:  #223150;
          --meter-fill:   #8ea2ff;

          --stat-k:       #9aa7bf;
          --stat-v:       #e6eaf3;
        }
      }

      @media (prefers-contrast: more){
        :root{
          --border: #94a3b8; /* boost border visibility */
          --focus:  0 0 0 3px rgba(79,70,229,.65);
        }
      }

      /* --------- Motion safety --------- */
      @media (prefers-reduced-motion: reduce) {
        * { animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; transition: none !important; }
      }

      /* --------- Base & layout --------- */
      .gradio-container{
        font-family: Inter, ui-sans-serif, -apple-system, Segoe UI, Roboto, Noto Sans, Ubuntu, Cantarell, Helvetica Neue, Arial;
        background: var(--bg) !important;
        color: var(--text);
      }
      .wrap { max-width: 1180px; margin: 0 auto; padding: 0 12px; }

      .h1 { font: 800 28px/1.2 Inter, system-ui; letter-spacing:-0.01em; color: var(--text); }
      .h2 { font: 700 18px/1.2 Inter, system-ui; color: var(--text); }
      .hint { color: var(--muted); font: 400 13px/1.35 Inter, system-ui; }

      a, .link { color: var(--brand); text-decoration: none; }
      a:hover, .link:hover { text-decoration: underline; }

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

      /* --------- Inputs --------- */
      .upload-box .wrap{
        border: 1.5px dashed var(--border);
        border-radius: 12px;
        padding: 20px;
        transition: border .15s ease, background .15s ease;
        background: var(--panel-alt);
      }
      .upload-box .wrap:hover{
        border-color: var(--brand);
        background: color-mix(in srgb, var(--panel-alt) 85%, var(--brand) 15%);
      }
      .textarea textarea{
        min-height: 280px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
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

      /* --------- Tabs --------- */
      .tabs .tabitem{ padding:6px 0 0; }
      .tabs button[role="tab"]{
        font-weight: 600;
        border-radius: 10px !important;
      }
      .tabs button[role="tab"][aria-selected="true"]{
        background: var(--brand-weak);
        border-color: var(--brand);
      }
      .tabs button[role="tab"]:focus-visible{
        box-shadow: var(--focus); outline: none;
      }

      /* --------- Buttons --------- */
      .btn-lg button{
        font-weight:700; font-size:16px; padding:12px 16px;
        background: var(--brand);
        border: 1px solid transparent;
        color: #fff;
        border-radius: 12px !important;
      }
      .btn-lg button:hover{ filter: brightness(0.95); }
      .btn-lg button:focus-visible{ box-shadow: var(--focus); outline: none; }

      /* --------- Results / Preview --------- */
      .result-card{
        background: var(--panel-alt);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
      }
      .score-wrap{ display:flex; align-items:center; gap:18px; }
      .score-val{ font: 800 24px Inter, system-ui; fill: var(--text); }
      .score-label{ font: 700 14px Inter, system-ui; margin-top: 2px; }
      .score-meta .tone-success{ color: var(--tone-success); }
      .score-meta .tone-warning{ color: var(--tone-warning); }
      .score-meta .tone-danger{  color: var(--tone-danger);  }

      pre{
        background: var(--panel-alt) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        overflow:auto;
      }

      /* --------- Pills --------- */
      .pill{
        display:inline-block;
        margin:4px 6px 0 0;
        padding:6px 10px;
        border-radius:9999px;
        font:600 12px Inter, system-ui;
        transition: transform .15s ease, background .15s ease;
        border: 1px solid var(--pill-border);
      }
      .pill:hover{ transform: translateY(-1px); }
      .pill-ok{ background: var(--pill-ok-bg); color: var(--pill-ok-fg); }
      .pill-miss{ background: var(--pill-miss-bg); color: var(--pill-miss-fg); }

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
        display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px; margin-top: 12px;
      }
      .stat{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 14px;
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
    return (_esc_html(s).replace('"', "&quot;").replace("'", "&#39;"))
