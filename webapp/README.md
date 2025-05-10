# 🧠 SHL Assessment Recommender

This app helps users get the most relevant SHL assessments based on a job description. It uses semantic search (`SentenceTransformers`) to retrieve matching assessments and a lightweight reranker to refine the recommendations.

## 🚀 Live Demo

Try it on [Hugging Face Spaces](https://huggingface.co/spaces/your-username/your-space-name)  
_or_  
Run locally with Gradio and FastAPI.

---

## 📁 File Overview

| File           | Description |
|----------------|-------------|
| `app.py`       | Gradio + FastAPI application combining UI and API endpoints. |
| `retriever.py` | Retrieves top relevant assessments using `all-MiniLM-L6-v2`. |
| `reranker.py`  | Reranks top assessments (mock logic or optionally CrossEncoder). |
| `assessments.csv` | CSV dataset containing SHL test metadata. |
| `requirements.txt` | All dependencies to run the app. |
| `.gitignore`   | Ignores cache and temp files. |

---

## 📦 Installation & Running Locally

1. **Clone this repo**
   ```bash
   git clone https://github.com/your-username/shl-assessment-recommender.git
   cd shl-assessment-recommender




---
title: Endpointwebappshl
emoji: 🐨
colorFrom: pink
colorTo: green
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
pinned: false
short_description: webapp
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
