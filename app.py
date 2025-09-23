import gradio as gr
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf):
    reader = PdfReader(pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def get_embedding(text):
    return model.encode([text], normalize_embeddings=True)[0]

def find_similarity(resume_text, jd_text):
    emb_resume = get_embedding(resume_text)
    emb_jd = get_embedding(jd_text)
    score = np.dot(emb_resume, emb_jd) / (np.linalg.norm(emb_resume) * np.linalg.norm(emb_jd))
    return float(score)

def analyze_resume(pdf_file, jd_text):
    resume_text = extract_text_from_pdf(pdf_file)
    if not resume_text.strip():
        return "Error: Could not extract text from PDF.", None
    score = find_similarity(resume_text, jd_text)
    return f"Similarity Score: {score:.3f}", resume_text

with gr.Blocks() as demo:
    gr.Markdown("## ATS Resume Analyzer")
    with gr.Row():
        pdf_input = gr.File(label="Upload Resume PDF")
        jd_input = gr.Textbox(label="Paste Job Description", lines=6)
    score_output = gr.Textbox(label="Similarity Score / Error", show_copy_button=True)
    resume_output = gr.Textbox(label="Extracted Resume Text", show_copy_button=True)
    analyze_btn = gr.Button("Analyze")
    analyze_btn.click(analyze_resume, inputs=[pdf_input, jd_input], outputs=[score_output, resume_output])

demo.launch()
