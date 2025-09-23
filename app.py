import gradio as gr
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
from utils.skills import extract_skills, compare_skills
import re

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf):
    reader = PdfReader(pdf)
    return "\n".join([p.extract_text() or "" for p in reader.pages])

def chunk_text(text, size=900, overlap=100):
    words = text.split()
    out, idx = [], 0
    while idx < len(words):
        chunk = " ".join(words[idx:idx+size])
        out.append(chunk)
        idx += size - overlap
    return out

def get_embeddings(texts):
    return model.encode(texts, normalize_embeddings=True)

def section_similarity(resume_chunks, jd_chunks):
    re = get_embeddings(resume_chunks)
    jd = get_embeddings(jd_chunks)
    scores = [np.max(np.dot(re, emb) / (np.linalg.norm(re, axis=1) * np.linalg.norm(emb))) for emb in jd]
    return np.mean(scores), scores

def analyze(pdf_file, jd_text, show_resume):
    resume_text = extract_text_from_pdf(pdf_file)
    if not resume_text.strip():
        return (
            "Error: Resume text not extracted. Please try with a different PDF.",
            "", "", "", ""
        )
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    missing_skills = compare_skills(resume_skills, jd_skills)
    jd_chunks = chunk_text(jd_text)
    resume_chunks = chunk_text(resume_text)
    overall_score = round(section_similarity(resume_chunks, jd_chunks)[0] * 100, 2)

    # Outputs
    overview = (
        f"<h2 style='color:#2563eb;'>📊 ATS Match Score:</h2><p style='font-size:1.7em;color:green;'>{overall_score}%</p>"
        f"<hr><h4>Resume Skills Matched:</h4> {len(set(resume_skills) & set(jd_skills))} / {len(jd_skills)}"
        f"<hr><details><summary>JD Skills Coverage</summary>{', '.join(resume_skills)}</details>"
    )
    missing_md = (
        "<h2 style='color:#be123c;'>🔎 Missing Skills for ATS</h2>" +
        "<ul>" +
        "".join([f"<li style='color:#be123c;'>{sk}</li>" for sk in missing_skills]) +
        "</ul>" if missing_skills else
        "<span style='color:green;'>✔️ All ATS skills covered!</span>"
    )
    section_md = (
        "<h2>Resume Preview</h2>"
        f"<details><summary>Show Extracted Text</summary><pre style='background:#f3f4f6;'>{resume_text[:2500]}</pre></details>"
        if show_resume else ""
    )
    # (You can add advanced matching details and per-section scores here)
    resume_view = (
        "<h2>Resume Raw Text</h2>"
        f"<pre style='background:#f3f4f6;'>{resume_text[:5000]}</pre>"
        if show_resume else ""
    )
    skills_display = (
        "<h3 style='color:#3b82f6;'>Resume Skills</h3>"
        + " ".join([f"<span style='color:green; font-weight: bold;'>{skill}</span>" for skill in resume_skills])
        + "<br><h3 style='color:#be123c;'>JD Skills</h3>"
        + " ".join([f"<span style='color:#be123c;'>{skill}</span>" for skill in jd_skills])
    )
    return overview, missing_md, section_md, resume_view, skills_display

with gr.Blocks(theme=gr.themes.Base()) as demo:
    gr.Image("https://img.icons8.com/color/96/000000/open-resume.png", elem_id="logo", show_label=False)
    gr.Markdown("""
    # 🎯 ATS Resume Analyzer
    *Upload your resume PDF, paste a job description, and get instant ATS match score, missing skill highlights, and resume preview — optimized for software engineering roles.*
    """)
    with gr.Row():
        pdf_input = gr.File(label="Upload Resume PDF")
        jd_input = gr.Textbox(label="Paste Job Description", lines=8, interactive=True)
    with gr.Row():
        show_resume = gr.Checkbox(label="Show full resume text in output", value=False)
    with gr.Tabs():
        with gr.TabItem("Overview"):
            out_overview = gr.HTML()
        with gr.TabItem("Missing Skills"):
            out_missing = gr.HTML()
        with gr.TabItem("Preview"):
            out_section = gr.HTML()
        with gr.TabItem("Resume Raw"):
            out_resume = gr.HTML()
        with gr.TabItem("Skills"):
            out_skills = gr.HTML()
    submit = gr.Button("🔍 Analyze and Highlight", size="lg")
    submit.click(analyze, inputs=[pdf_input, jd_input, show_resume], outputs=[out_overview, out_missing, out_section, out_resume, out_skills])
demo.launch()
