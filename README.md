---
title: Resume ATS Analyzer
emoji: 📄
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: "5.38.0"
app_file: app.py
pinned: false
---

# 📄 Resume ATS Analyzer

[![Open in Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Open%20in%20Spaces-blue?logo=huggingface&logoColor=white)](https://huggingface.co/spaces/your-username/resume-ats-analyzer)
[![Duplicate this Space](https://img.shields.io/badge/Duplicate-Resume%20ATS%20Analyzer-8A2BE2?logo=huggingface&logoColor=white)](https://huggingface.co/spaces/your-username/resume-ats-analyzer?duplicate=true)

A **resume analyzer** that matches resumes to job descriptions, highlights missing ATS skills, and provides a **calibrated ATS score**.  
Built with **Gradio**, **SentenceTransformers**, and a custom **skills taxonomy**.

---

## 🚀 Features
- 📄 **Resume parsing** (PyMuPDF for speed, PyPDF2 fallback)  
- 🧠 **Embeddings** with `all-MiniLM-L6-v2` (Sentence Transformers)  
- 🎯 **Skill extraction & matching** (canonical + aliases + fuzzy)  
- ⚖️ **Weighted scoring** with category caps + down-weighted common skills  
- 🌗 **Dark/light theme** with custom CSS  
- ✨ **Highlights tab**: inline `<mark>` for matched skills in resume & JD  
- ✅ **Lenient toggle**: ATS-friendly fuzzy matching  

---

## 🛠️ Run locally

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python -m venv .venv
# Activate venv:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
python app.py
