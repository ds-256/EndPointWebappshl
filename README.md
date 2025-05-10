# 🧰 SHL Assessment Tools Suite

This project contains two main tools to work with SHL assessments:

1. **[SHL Assessment Recommender](./webapp/)**: A web application that recommends SHL assessments based on job descriptions using semantic search and reranking.
2. **`shl_site_scraper.py`**: A Python script to scrape assessment details directly from the SHL website (used to build or update the dataset).

---

## 🔧 Contents

| Folder/File                     | Description |
|--------------------------------|-------------|
| `webapp/`  | Web app (Gradio + FastAPI) for assessment recommendation |
| `scrappingdocsr.py`          | Script to crawl and collect SHL assessment information |
| `README.md`                    | Overview of the entire project |

---

## ⚙️ How to Use

### 🔹 1. SHL Assessment Recommender App

Go to [`shl-assessment-recommender`](./shl-assessment-recommender/) and follow instructions in its README to run the app locally or deploy it.

```bash
cd shl-assessment-recommender
python app.py
