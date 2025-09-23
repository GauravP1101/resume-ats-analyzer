# ui_enhancements.py
from __future__ import annotations
import math

# ---- gauge + HTML helpers ----------------------------------------------------

def score_badge(score: float) -> str:
    """
    SVG circular gauge (0–100). Returns HTML string.
    """
    score = max(0.0, min(100.0, float(score)))
    # color ramps: red <50, amber 50–74, green 75+
    if score < 50:
        color = "#ef4444"  # red-500
        label = "Needs Work"
    elif score < 75:
        color = "#f59e0b"  # amber-500
        label = "Okay Match"
    else:
        color = "#10b981"  # emerald-500
        label = "Strong Fit"

    radius = 56
    stroke = 10
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100.0)

    return f"""
    <div style="display:flex;align-items:center;gap:18px;">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="{radius}" fill="none" stroke="#e5e7eb" stroke-width="{stroke}" />
        <circle cx="70" cy="70" r="{radius}" fill="none"
                stroke="{color}" stroke-width="{stroke}"
                stroke-linecap="round"
                stroke-dasharray="{circumference:.1f}"
                stroke-dashoffset="{offset:.1f}"
                transform="rotate(-90 70 70)"/>
        <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
              style="font:700 24px Inter, system-ui; fill:{color};">{score:.0f}%</text>
      </svg>
      <div>
        <div style="font:700 18px Inter, system-ui;">ATS Match Score</div>
        <div style="color:{color}; font:600 16px Inter, system-ui;">{label}</div>
        <div style="color:#6b7280; font:400 13px Inter, system-ui;">Higher is better • Cosine-based semantic match</div>
      </div>
    </div>
    """

def pill(text: str, ok: bool) -> str:
    bg = "#d1fae5" if ok else "#fee2e2"
    fg = "#065f46" if ok else "#991b1b"
    return f"<span style='display:inline-block;margin:4px 6px 0 0;padding:6px 10px;border-radius:9999px;background:{bg};color:{fg};font:600 12px Inter,system-ui'>{text}</span>"

def base_css() -> str:
    return """
    <style>
      :root { --brand: #4f46e5; --text:#111827; --muted:#6b7280; }
      .wrap { max-width: 1150px; margin: 0 auto; }
      .card { background:#fff; border-radius:16px; box-shadow: 0 8px 24px rgba(17,24,39,.06); padding:20px; }
      .h1 { font: 800 28px Inter, system-ui; color: var(--text); letter-spacing:-0.01em; }
      .h2 { font: 700 18px Inter, system-ui; color: var(--text); }
      .hint { color: var(--muted); font: 400 13px Inter, system-ui; }
      .btn-lg button { font-weight:700; font-size:16px; padding:12px 16px; }
      /* Gradio polish */
      .gradio-container { font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Noto Sans, Ubuntu, Cantarell, Helvetica Neue, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
      .upload-box .wrap { border:2px dashed #e5e7eb; border-radius:14px; padding:24px; transition: border .15s ease; }
      .upload-box .wrap:hover { border-color:#a5b4fc; }
      .textarea textarea { min-height: 270px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
      .tabs .tabitem { padding: 4px 0 0 0; }
    </style>
    """
