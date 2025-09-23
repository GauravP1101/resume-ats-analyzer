# app.py  — refined Gradio UI using the enhanced CSS atoms
import gradio as gr
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

from utils.skills import extract_skills, compare_skills
from utils.ui_enhancements import score_badge, pill, base_css

# --------------------------- Model -------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------- Helpers -----------------------------------------
def extract_text_from_pdf(pdf) -> str:
    reader = PdfReader(pdf)
    return "\n".join([(p.extract_text() or "") for p in reader.pages])

def chunk_text(text: str, size: int = 900, overlap: int = 100):
    words = text.split()
    if not words:
        return []
    chunks, i = [], 0
    step = max(1, size - overlap)
    while i < len(words):
        chunks.append(" ".join(words[i : i + size]))
        i += step
    return chunks

def get_embeddings(texts):
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)  # MiniLM dim
    return model.encode(texts, normalize_embeddings=True)

def section_similarity(resume_chunks, jd_chunks):
    """
    Mean(max cosine(sim(resume_chunk, jd_chunk))) over all JD chunks.
    Returns (mean_score_0to1, per_jd_scores)
    """
    R = get_embeddings(resume_chunks)  # (nr, d), L2-normalized
    J = get_embeddings(jd_chunks)      # (nj, d)
    if R.size == 0 or J.size == 0:
        return 0.0, []
    sims = R @ J.T                     # cosine (normed)
    per_jd = np.max(sims, axis=0)      # best match per JD chunk
    return float(np.mean(per_jd)), per_jd.tolist()

def _esc(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# --------------------------- Core --------------------------------------------
def analyze(pdf_file, jd_text: str, show_resume: bool):
    # Basic guards
    if pdf_file is None:
        return ("<b style='color:#991b1b'>Please upload a PDF resume.</b>", "", "", "", "")
    jd_text = (jd_text or "").strip()
    if not jd_text:
        return ("<b style='color:#991b1b'>Please paste a job description to analyze.</b>", "", "", "", "")

    # Extract
    resume_text = extract_text_from_pdf(pdf_file)
    if not resume_text.strip():
        return ("<b style='color:#991b1b'>Error: Resume text could not be extracted. Try another PDF.</b>", "", "", "", "")

    # Skills
    resume_skills = extract_skills(resume_text)
    jd_skills     = extract_skills(jd_text)
    missing_skills = compare_skills(resume_skills, jd_skills)
    matched        = sorted(set(resume_skills) & set(jd_skills))
    total_jd       = len(set(jd_skills))

    # Similarity
    jd_chunks     = chunk_text(jd_text)
    resume_chunks = chunk_text(resume_text)
    overall       = round(section_similarity(resume_chunks, jd_chunks)[0] * 100, 2)

    # Small stats
    r_words = len(resume_text.split())
    j_words = len(jd_text.split())

    # ---------------- UI blocks ----------------
    # Overview with soft background for readability
    overview = f"""
    {score_badge(overall)}
    <div class="result-card" style="margin-top:12px">
      <div class="h2">Skills Summary</div>
      <div class="hint" style="margin:6px 0 12px">
        Matched <b>{len(matched)}</b> of <b>{total_jd}</b> JD skills •
        Resume words: <b>{r_words}</b> • JD words: <b>{j_words}</b>
      </div>
      <div>{"".join(pill(s, True) for s in matched) or "<span class='hint'>No direct skill overlaps found.</span>"}</div>
    </div>
    """

    # Missing skills panel (also readable without selection)
    if missing_skills:
        missing_md = (
            "<div class='h2' style='color:#991b1b'>Missing Skills for ATS</div>"
            + "<div class='result-card' style='margin-top:8px'>"
            + "".join(pill(sk, False) for sk in missing_skills)
            + "</div>"
        )
    else:
        missing_md = "<div style='color:#065f46;font:600 14px Inter,system-ui'>✔ All JD skills are represented in your resume.</div>"

    # Preview (short, escaped, soft bg)
    section_md = ""
    if show_resume:
        snippet = _esc(resume_text[:3000])
        section_md = f"""
        <div class="h2">Resume Preview</div>
        <details open style="margin-top:8px">
          <summary class="hint">Show Extracted Text (first 3000 chars)</summary>
          <pre>{snippet}</pre>
        </details>
        """

    # Raw (longer, escaped)
    resume_view = ""
    if show_resume:
        raw = _esc(resume_text[:8000])
        resume_view = f"<pre>{raw}</pre>"

    # Skills tab
    skills_display = (
        "<div class='h2' style='color:#1f2937'>Skills</div>"
        "<div class='result-card' style='margin:8px 0'><b>Resume:</b><br>"
        + ("".join(pill(s, True) for s in resume_skills) or "<span class='hint'>None found.</span>")
        + "</div><div class='result-card' style='margin-top:8px'><b>Job Description:</b><br>"
        + ("".join(pill(s, True) for s in jd_skills) or "<span class='hint'>None found.</span>")
        + "</div>"
    )

    return overview, missing_md, section_md, resume_view, skills_display

# --------------------------- Gradio App ---------------------------------------
with gr.Blocks(theme=gr.themes.Soft(), css=base_css()) as demo:
    gr.Markdown("""
    <div class="wrap">
      <div class="h1">ATS Resume Analyzer</div>
      <div class="hint">Upload your resume and paste a job description to see a clear, defensible ATS score plus missing skills.</div>
    </div>
    """)

    # Input panels (thin borders, no heavy white frames)
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

    # Results tabs — backgrounds use .result-card / <pre> styling from CSS
    with gr.Tabs(elem_classes=["wrap", "tabs"]):
        with gr.TabItem("Overview"):      out_overview = gr.HTML()
        with gr.TabItem("Missing Skills"): out_missing  = gr.HTML()
        with gr.TabItem("Preview"):       out_section  = gr.HTML()
        with gr.TabItem("Resume Raw"):    out_resume   = gr.HTML()
        with gr.TabItem("Skills"):        out_skills   = gr.HTML()

    with gr.Row(elem_classes=["wrap", "btn-lg"]):
        submit = gr.Button("🔍 Analyze and Highlight", variant="primary")

    submit.click(
        analyze,
        inputs=[pdf_input, jd_input, show_resume],
        outputs=[out_overview, out_missing, out_section, out_resume, out_skills],
    )

if __name__ == "__main__":
    demo.launch()
