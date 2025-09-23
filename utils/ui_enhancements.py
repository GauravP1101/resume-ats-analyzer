# ui_enhancements.py
from __future__ import annotations
import math

# -------------------- Color-aware SVG gauge --------------------
def score_badge(score: float) -> str:
    score = max(0.0, min(100.0, float(score)))
    if score < 50:
        color, label = "#ef4444", "Needs Work"   # red-500
    elif score < 75:
        color, label = "#f59e0b", "Okay Match"   # amber-500
    else:
        color, label = "#10b981", "Strong Fit"   # emerald-500

    radius, stroke = 56, 10
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100.0)

    return f"""
    <div class="score-wrap">
      <svg width="140" height="140" viewBox="0 0 140 140" role="img" aria-label="ATS score gauge">
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="var(--border)" stroke-width="{stroke}" />
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
        <div class="hint">Higher is better • Cosine-based semantic match</div>
      </div>
    </div>
    """

# -------------------- Small UI atoms --------------------
def pill(text: str, ok: bool) -> str:
    bg = "var(--pill-ok-bg)" if ok else "var(--pill-miss-bg)"
    fg = "var(--pill-ok-fg)" if ok else "var(--pill-miss-fg)"
    return (
        f"<span class='pill' style='background:{bg};color:{fg};'>"
        f"{text}</span>"
    )

# -------------------- Global CSS (light + dark) --------------------
def base_css() -> str:
    """
    Clean, accessible palette + thin borders + distinctive result backgrounds.
    Works with your existing app.py layout (no code changes needed).
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
        }
      }

      /* --------- Base typography & container --------- */
      .gradio-container{
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Ubuntu, Cantarell, Helvetica Neue, Arial;
        background: var(--bg) !important;
        color: var(--text);
      }
      .wrap { max-width: 1150px; margin: 0 auto; }

      .h1 { font: 800 28px/1.2 Inter, system-ui; letter-spacing:-0.01em; color: var(--text); }
      .h2 { font: 700 18px/1.2 Inter, system-ui; color: var(--text); }
      .hint { color: var(--muted); font: 400 13px/1.2 Inter, system-ui; }

      /* --------- Cards / Panels (fix thick white borders) --------- */
      .card{
        background: var(--panel);
        border: 1px solid var(--border) !important;   /* thin border */
        border-radius: 14px;
        box-shadow: var(--shadow);
        padding: 18px;
      }
      /* Gradio defaults sometimes add thicker borders; normalize: */
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
        background: color-mix(in srgb, var(--panel) 86%, var(--brand) 14%);
      }
      .textarea textarea{
        min-height: 270px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        background: var(--panel-alt) !important;  /* softer contrast so text is readable */
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
      }

      /* --------- Tabs polish --------- */
      .tabs .tabitem{ padding:6px 0 0; }
      .tabs button[role="tab"]{
        font-weight: 600;
      }

      /* --------- Buttons --------- */
      .btn-lg button{
        font-weight:700; font-size:16px; padding:12px 16px;
        background: var(--brand);
        border: 1px solid transparent;
      }
      .btn-lg button:hover{
        filter: brightness(0.95);
      }

      /* --------- Result blocks (distinct background) --------- */
      .result-card{
        background: var(--panel-alt);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
      }
      .score-wrap{ display:flex; align-items:center; gap:18px; }
      .score-val{ font: 700 24px Inter, system-ui; }

      /* --------- Pills --------- */
      .pill{
        display:inline-block;
        margin:4px 6px 0 0;
        padding:6px 10px;
        border-radius:9999px;
        font:600 12px Inter, system-ui;
        border: 1px solid rgba(0,0,0,.04);
      }

      /* --------- Previews --------- */
      pre{
        background: var(--panel-alt) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        overflow:auto;
      }
    </style>
    """
