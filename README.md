# 📄 GeoMine: Project Location Extractor

> A lightweight NLP pipeline to extract mining project names and infer their locations from geological PDF reports.

**GeoMine** is a modular information extraction pipeline built to process unstructured mining documents, identify project names using Named Entity Recognition (NER), and estimate their geographic locations using large language models. Designed with simplicity, modularity, and clarity in mind, it's suitable for both production and research use cases.

---

## 📌 Overview

Given a collection of multi-page geological PDF reports, this pipeline:

1. Extracts readable text from each page
2. Identifies mining project names using a custom-trained spaCy NER model
3. Infers coordinates using LLM prompting (Gemini API)
4. Outputs a structured `JSONL` record for each project mention

---

## ✨ Features

- 📄 Accurate text extraction from noisy PDFs with `pdfplumber`
- 🧠 Custom NER model for project detection (trained with Label Studio annotations)
- 🌍 LLM-powered geolocation from contextual clues
- 💬 Clear logging, error handling, and testable modules
- 🔁 Reproducible and modular design for future extension

---

## 🚀 Getting Started

### Installation

```bash
git clone https://github.com/your-org/geomine.git
cd geomine

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Project Structure

```
data/
└── input/
    ├── annotations.json       # Project name annotations (Label Studio format)
    └── pdf_reports/           # Geological PDFs
```

### Run the Pipeline

```bash
bash run_pipeline.sh
```

Outputs will be saved to:

```
data/output/final_results.jsonl
```

---

## 🔍 Output Format

```json
{
  "pdf_file": "Report_4.pdf",
  "page_number": 3,
  "project_name": "Minyari Dome Project",
  "context_sentence": "Minyari Dome Project is located in the Paterson region of WA.",
  "coordinates": [-24.7393, 133.8807]
}
```

---

## 🧰 Built With

| Purpose           | Tool/Library                    |
| ----------------- | ------------------------------- |
| Text extraction   | `pdfplumber`                    |
| NER & NLP         | `spaCy`                         |
| Annotation format | `Label Studio JSON`             |
| Geolocation (LLM) | `Gemini API` (Google AI Studio) |
| Output structure  | `JSONL`                         |

---

## ⚠️ Gemini API Limitations

- **Gemini's API is not fully production-stable**, and namespace import issues may affect integration (`ModuleNotFoundError: No module named 'google'`).
- If unavailable, **GeoMine falls back to `GeoNames`** for coordinate inference using keyword-based matching.
- You can configure `GEONAMES_USERNAME` in your `.env` to enable the fallback behavior.

---

## 🧪 Testing

```bash
pytest
```

Tests live in the `tests/` directory.

---

## ⚙️ Implementation Notes

| Area            | Details                                                                     |
| --------------- | --------------------------------------------------------------------------- |
| NER             | Trained using project-level annotations to detect custom "PROJECT" entities |
| Geolocation     | Context-aware location prediction via Gemini or fallback rules              |
| Data Format     | JSONL for line-by-line structured records                                   |
| Fault Tolerance | Graceful handling of empty pages, missing labels, and broken models         |

---

## 📦 Deliverables

- ✅ End-to-end runnable pipeline
- ✅ Clean, structured JSONL outputs
- ✅ Modular, testable Python code

---

## 💡 Ideas for Improvement

- Confidence scoring on both project detection and coordinate inference
- Interactive annotation review tool
- Gazetteer-backed geolocation fallback
- Dockerized deployment

---

## 👤 Author

**Avishkar Dandge**  
[GitHub](https://github.com/ashkaaar)
