# app.py — fast UI + Highlights tab + Lenient matching toggle
from __future__ import annotations

import os
import hashlib
from functools import lru_cache
from typing import List, Set

import gradio as gr
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# Prefer PyMuPDF (much faster). Fallback to PyPDF2.
try:
    import fitz  # PyMuPDF
    HAVE_FITZ = True
except Exception:
    from PyPDF2 import PdfReader
    HAVE_FITZ = False

# --- skills helpers -----------------------------------------------------------
from utils.skills import (
    extract_skills,
    compare_skills,
    # optional richer report (if you pasted the advanced skills.py)
    analyze_skills,
    # highlighter helpers
    highlight_text_with_skills,
)
# If you didn't paste the richer skills.py, import errors will happen.
# In that case, comment out analyze_skills/highlight_text_with_skills lines above,
# or add simple fallbacks here.

# --- UI atoms -----------------------------------------------------------------
from utils.ui_enhancements import score_badge, pill, base_css


# ============================ Runtime / Model =================================
# Cap threads to avoid CPU oversubscription
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
torch.set_num_threads(int(os.environ["OMP_NUM_THREADS"]))

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
# speed-up with shorter context
model.max_seq_length = 256


# =============================== Utilities ====================================
def extract_text_from_pdf(pdf_path_or_file) -> str:
    """
    Fast path: PyMuPDF. Fallback: PyPDF2.
    Accepts a Gradio temp file path or a file object.
    """
    path = pdf_path_or_file if isinstance(pdf_path_or_file, str) else pdf_path_or_file.name
    if HAVE_FITZ:
        parts = []
        with fitz.open(path) as doc:
            for page in doc:
                parts.append(page.get_text("text") or "")
        return "\n".join(parts)
    else:
        reader = PdfReader(path)
        return "\n".join([(p.extract_text() or "") for p in reader.pages])


def chunk_text_tokens(text: str, max_tokens: int = 256, overlap: int = 32):
    """
    Token-aware chunking keeps chunk counts low for faster encoding.
    """
    text = (text or "").strip()
    if not text:
        return []
    tok = model.tokenizer
    ids = tok(text, add_special_tokens=False)["input_ids"]
    chunks, start = [], 0
    step = max_tokens - max(0, overlap)
    while start < len(ids):
        end = min(start + max_tokens, len(ids))
        chunk_ids = ids[start:end]
        chunks.append(tok.decode(chunk_ids, skip_special_tokens=True))
        start += step
    return chunks


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


@lru_cache(maxsize=64)
def _encode_cached(key: str, *texts) -> np.ndarray:
    """
    LRU cache of embeddings keyed by a stable string.
    """
    with torch.no_grad():
        emb = model.encode(
            list(texts),
            batch_size=64,                 # tune to 16/32 if RAM is tight
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
    return emb


def get_embeddings_cached(texts: List[str], key_prefix: str) -> np.ndarray:
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)
    key = key_prefix + ":" + _sha1("||".join(texts))
    return _encode_cached(key, *texts)


def section_similarity(resume_chunks: List[str], jd_chunks: List[str]):
    """
    Mean of max cosine similarity for each JD chunk vs. all resume chunks.
    Returns (mean_score_0to1, per_jd_scores).
    """
    R = get_embeddings_cached(resume_chunks, key_prefix="resume")
    J = get_embeddings_cached(jd_chunks, key_prefix="jd")
    if R.size == 0 or J.size == 0:
        return 0.0, []
    sims = R @ J.T  # cosine because normalized
    per_jd = np.max(sims, axis=0)
    return float(np.mean(per_jd)), per_jd.tolist()


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- Lenient matching helper -------------------------------------------
def _lenient_unify(resume_sk: Set[str], jd_sk: Set[str], ratio: float = 0.80) -> Set[str]:
    """
    Expand 'matched' by allowing near-equal (fuzzy) skill names.
    This makes the analyzer a bit less rigorous (ATS-friendly).
    """
    import difflib
    matched = set(resume_sk & jd_sk)
    rem_r = [r.lower() for r in resume_sk]
    rem_j = [j.lower() for j in jd_sk]
    for j in rem_j:
        # pick best close match from resume skills
        best = difflib.get_close_matches(j, rem_r, n=1, cutoff=ratio)
        if best:
            # unify with original canonical casing if present
            # find the original strings that lower() to these
            j_orig = next((x for x in jd_sk if x.lower() == j), j)
            r_orig = next((x for x in resume_sk if x.lower() == best[0]), best[0])
            matched.add(j_orig if len(j_orig) >= len(r_orig) else r_orig)
    return matched


# ============================== Core Handler ==================================
def analyze(pdf_file, jd_text: str, show_resume: bool, lenient: bool):
    # Guards
    if pdf_file is None:
        return ("<b style='color:#991b1b'>Please upload a PDF resume.</b>", "", "", "", "", "")
    jd_text = (jd_text or "").strip()
    if not jd_text:
        return ("<b style='color:#991b1b'>Please paste a job description to analyze.</b>", "", "", "", "", "")

    # Extract text
    resume_text = extract_text_from_pdf(pdf_file)
    if not resume_text.strip():
        return ("<b style='color:#991b1b'>Error: Resume text could not be extracted. Try another PDF.</b>", "", "", "", "", "")

    # Token-chunking (fast)
    resume_chunks = chunk_text_tokens(resume_text, max_tokens=256, overlap=32)
    jd_chunks     = chunk_text_tokens(jd_text,     max_tokens=256, overlap=32)

    # Embedding similarity score
    overall = round(section_similarity(resume_chunks, jd_chunks)[0] * 100, 2)

    # Skills
    resume_sk = set(extract_skills(resume_text))
    # Use richer JD extraction if available
    try:
        from utils.skills import extract_jd_skills
        jd_sk = set(extract_jd_skills(jd_text))
    except Exception:
        jd_sk = set(extract_skills(jd_text))

    # Matched / missing (lenient if toggle is on)
    matched = sorted(_lenient_unify(resume_sk, jd_sk) if lenient else (resume_sk & jd_sk))
    missing = sorted(jd_sk - set(matched))
    total_jd = len(jd_sk)

    # Optional weighted coverage (if you added it)
    coverage_line = ""
    try:
        report = analyze_skills(resume_text, jd_text)
        cov = report.get("coverage_score", 0.0)
        # if lenient, nudge coverage slightly (friendlier presentation)
        if lenient and cov < 100:
            cov = min(100.0, round(cov + 3.0, 2))  # soft boost
        coverage_line = f"<div class='hint'>Weighted skill coverage: <b>{cov}%</b>{' • Lenient' if lenient else ''}</div>"
    except Exception:
        pass

    r_words = len(resume_text.split())
    j_words = len(jd_text.split())

    # ---------------- UI HTML blocks ----------------
    # Overview
    overview = f"""
    {score_badge(overall)}
    <div class="result-card" style="margin-top:12px">
      <div class="h2">Skills Summary{(' — Lenient matching' if lenient else '')}</div>
      {coverage_line}
      <div class="hint" style="margin-top:6px">
        Matched <b>{len(matched)}</b> of <b>{total_jd}</b> JD skills •
        Resume words: <b>{r_words}</b> • JD words: <b>{j_words}</b>
      </div>
      <div style="margin-top:8px">
        {"".join(pill(s, True) for s in matched) or "<span class='hint'>No direct overlaps found.</span>"}
      </div>
    </div>
    """

    # Missing skills panel
    if missing:
        missing_md = (
            "<div class='h2' style='color:#991b1b'>Missing Skills for ATS</div>"
            + "<div class='result-card' style='margin-top:8px'>"
            + "".join(pill(sk, False) for sk in missing)
            + "</div>"
        )
    else:
        missing_md = "<div style='color:#065f46;font:600 14px Inter,system-ui'>✔ All JD skills are represented in your resume.</div>"

    # Highlights (inline <mark>) for matched skills
    # We highlight using the matched set (lenient-aware) so the view matches the counts above.
    try:
        resume_h_html, _ = highlight_text_with_skills(resume_text, matched, color="#fef3c7", border="#f59e0b")
        jd_h_html, _     = highlight_text_with_skills(jd_text, matched, color="#dbf4ff", border="#38bdf8")
        highlights_html = f"""
        <div class='h2'>Highlighted Resume (matched skills)</div>
        <pre style="white-space:pre-wrap">{resume_h_html}</pre>
        <div class='h2' style="margin-top:10px">Highlighted Job Description (matched skills)</div>
        <pre style="white-space:pre-wrap">{jd_h_html}</pre>
        """
    except Exception:
        # Fallback: plain preview if highlighter is unavailable
        highlights_html = ""

    # Preview & Raw (optional)
    section_md = ""
    resume_view = ""
    if show_resume:
        snippet = _esc(resume_text[:3000])
        section_md = f"""
        <div class="h2">Resume Preview</div>
        <details open style="margin-top:8px">
          <summary class="hint">Show Extracted Text (first 3000 chars)</summary>
          <pre>{snippet}</pre>
        </details>
        """
        raw = _esc(resume_text[:8000])
        resume_view = f"<pre>{raw}</pre>"

    # Skills tab
    skills_display = (
        "<div class='h2' style='color:#1f2937'>Skills</div>"
        "<div class='result-card' style='margin:8px 0'><b>Resume:</b><br>"
        + ("".join(pill(s, True) for s in sorted(resume_sk)) or "<span class='hint'>None found.</span>")
        + "</div><div class='result-card' style='margin-top:8px'><b>Job Description:</b><br>"
        + ("".join(pill(s, True) for s in sorted(jd_sk)) or "<span class='hint'>None found.</span>")
        + "</div>"
    )

    return overview, missing_md, section_md, resume_view, skills_display, highlights_html


# ============================== Gradio Layout =================================
with gr.Blocks(theme=gr.themes.Soft(), css=base_css()) as demo:
    gr.Markdown("""
    <div class="wrap">
      <div class="h1">ATS Resume Analyzer</div>
      <div class="hint">Upload your resume and paste a job description to see a clear, defensible ATS score plus missing skills.</div>
    </div>
    """)

    # Inputs
    with gr.Row(elem_classes=["wrap"], equal_height=True):
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["card", "upload-box"]):
                gr.Markdown("<div class='h2'>Upload Resume PDF</div><div class='hint'>Drag & drop or click to select</div>")
                pdf_input = gr.File(label=None, file_types=[".pdf"], type="filepath")

        with gr.Column(scale=1):
            with gr.Group(elem_classes=["card"]):
                gr.Markdown("<div class='h2'>Paste Job Description</div>")
                jd_input = gr.Textbox(
                    label=None, lines=14, placeholder="Paste the JD here…",
                    elem_classes=["textarea"]
                )

    with gr.Row(elem_classes=["wrap"]):
        show_resume = gr.Checkbox(label="Show full resume text in output", value=False)
        lenient = gr.Checkbox(label="Lenient matching (ATS-friendly)", value=True)

    # Results
    with gr.Tabs(elem_classes=["wrap", "tabs"]):
        with gr.TabItem("Overview"):       out_overview  = gr.HTML()
        with gr.TabItem("Missing Skills"): out_missing   = gr.HTML()
        with gr.TabItem("Preview"):        out_section   = gr.HTML()
        with gr.TabItem("Resume Raw"):     out_resume    = gr.HTML()
        with gr.TabItem("Skills"):         out_skills    = gr.HTML()
        with gr.TabItem("Highlights"):     out_highlight = gr.HTML()

    with gr.Row(elem_classes=["wrap", "btn-lg"]):
        submit = gr.Button("🔍 Analyze and Highlight", variant="primary")

    submit.click(
        analyze,
        inputs=[pdf_input, jd_input, show_resume, lenient],
        outputs=[out_overview, out_missing, out_section, out_resume, out_skills, out_highlight],
    )

if __name__ == "__main__":
    demo.launch()
