# 📄 Resume ATS Analyzer

[![Open in Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Open%20in%20Spaces-blue?logo=huggingface&logoColor=white)](https://huggingface.co/spaces/Gauravp1101/resume-ats-analyzer)

A smart **Resume Analyzer** that evaluates resumes against job descriptions, highlights missing ATS keywords, and generates a **calibrated ATS score**.  
Designed to help job seekers improve their resumes for **Applicant Tracking Systems (ATS)** used by recruiters.

---

## ✨ Features

- 📑 **Resume Parsing**  
  - Fast parsing with **PyMuPDF**  
  - **PyPDF2** as a fallback for better compatibility  

- 🧠 **AI-Powered Embeddings**  
  - Uses `all-MiniLM-L6-v2` from **Sentence Transformers**  
  - Captures semantic similarity beyond keyword matching  

- 🎯 **Skill Extraction & Matching**  
  - Custom **skills taxonomy** with canonical forms, aliases, and fuzzy matching  
  - Detects missing skills and flags overused/common ones  

- ⚖️ **Scoring System**  
  - Weighted scoring across categories  
  - Down-weights generic skills  
  - Caps overemphasized areas  

- 🎨 **User Interface**  
  - Built with **Gradio**  
  - **Dark/Light themes** with custom CSS  
  - **Highlights Tab**: inline `<mark>` for matched skills in both JD & Resume  
  - **Lenient Toggle**: expands fuzzy matches for ATS-friendly evaluation  

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
