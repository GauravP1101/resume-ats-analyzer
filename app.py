import gradio as gr
import re
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
from skills import extract_skills, compare_skills

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf):
    reader = PdfReader(pdf)
    return "\n".join([p.extract_text() or "" for p in reader.pages])

def split_sections(text):
    headers = re.finditer(r'(Education|Experience|Projects|Skills|Technical Skills):', text)
    sections, last_idx, last_title = {}, 0, "Other"
    for m in headers:
        start, name = m.start(), m.group(1)
        if last_title != "Other":
            sections[last_title] = text[last_idx:start].strip()
        last_idx, last_title = start + len(name) + 1, name
    sections[last_title] = text[last_idx:].strip()
    return sections

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

def analyze(pdf_file, jd_text):
    resume_text = extract_text_from_pdf(pdf_file)
    sections = split_sections(resume_text)
    jd_chunks = chunk_text(jd_text)
    sec_scores = {sec: round(section_similarity(chunk_text(txt), jd_chunks)[0]*100,2)
                  for sec, txt in sections.items()}
    resume_skills, jd_skills = extract_skills(resume_text), extract_skills(jd_text)
    missing_skills = compare_skills(resume_skills, jd_skills)
    summary = (
        f"**Overall score**: {round(section_similarity(chunk_text(resume_text), jd_chunks)[0]*100,2)}%\n" +
        "\n".join([f"{k}: {v}%" for k,v in sec_scores.items()]) +
        f"\nResume skills: {', '.join(resume_skills)}\nJD skills: {', '.join(jd_skills)}\nMissing: {', '.join(missing_skills)}"
    )
    return summary, resume_text, ", ".join(missing_skills), str(sec_scores)

with gr.Blocks() as demo:
    gr.Markdown("# Enhanced ATS Resume Analyzer")
    pdf_input = gr.File(label="Upload Resume PDF")
    jd_input = gr.Textbox(label="Paste Job Description")
    out_summary = gr.Markdown()
    out_resume = gr.Textbox(show_copy_button=True)
    out_missing = gr.Textbox(label="Missing Skills", show_copy_button=True)
    out_sec_scores = gr.Textbox(label="Section Scores", show_copy_button=True)
    btn = gr.Button("Analyze")
    btn.click(analyze, inputs=[pdf_input, jd_input], outputs=[out_summary, out_resume, out_missing, out_sec_scores])
demo.launch()
