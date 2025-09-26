# 📄 Resume ATS Analyzer

[![Open in Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Open%20in%20Spaces-blue?logo=huggingface&logoColor=white)](https://huggingface.co/spaces/Gauravp1101/resume-ats-analyzer)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange?logo=gradio&logoColor=white)
![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-NLP-green?logo=huggingface&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF-red?logo=adobeacrobatreader&logoColor=white)
![Deployment](https://img.shields.io/badge/Deploy-HuggingFace%20Spaces-yellow?logo=huggingface&logoColor=white)

A smart **Resume Analyzer** that evaluates resumes against job descriptions, highlights missing ATS keywords, and generates a **calibrated ATS score**.  
Designed to help job seekers improve their resumes for **Applicant Tracking Systems (ATS)** used by recruiters.

---

## ✨ Features

- 📑 **Resume Parsing** – extracts text from PDF resumes quickly & reliably  
- 🧠 **AI-Powered Embeddings** – semantic similarity beyond raw keywords  
- 🎯 **Skill Extraction & Matching** – canonical + aliases + fuzzy matches  
- ⚖️ **Calibrated ATS Scoring** – weighted categories & caps for balance  
- 🎨 **Modern Interface** – responsive UI with dark/light mode  
- 🔍 **Highlights Tab** – inline `<mark>` for matched/missing skills  
- ✅ **Lenient Toggle** – expands fuzzy matching for ATS-friendly evaluation  

---

## 🖥️ Demo

👉 Try it live on HuggingFace Spaces:  
[**Resume ATS Analyzer – HuggingFace**](https://huggingface.co/spaces/Gauravp1101/resume-ats-analyzer)

---
## 🚀 Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/GauravP1101/resume-ats-analyzer.git
cd resume-ats-analyzer
```
2. Setup Environment
```bash
python -m venv .venv
# Activate venv:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```
3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
4. Run App
```bash
python app.py
```

Contributions are welcome! Feel free to open an issue or submit a pull request.
