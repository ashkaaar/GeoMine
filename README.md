## 🛠️ GeoMine: Mining Project Extraction from PDF Reports (NER + GeoLocation)

[![Built with spaCy](https://img.shields.io/badge/Built%20with-spaCy-09a3d5?logo=spacy)](https://spacy.io)
[![Gemini API](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-ffcc00?logo=google)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)](https://www.python.org/downloads/)

> Extract named entities and locations from geological PDFs using spaCy NER and Gemini LLMs. Built for mining industry document parsing.

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
git clone https://github.com/ashkaaar/GeoMine-NER-Geolocation.git
cd GeoMine-NER-Geolocation

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 📁 Project Structure

```
.
├── data/
│   ├── input/
│   │   ├── annotations.json           # NER labels from Label Studio
│   │   └── pdf_reports/               # Input geological PDFs
│   ├── output/                        # Final extracted results
│   └── temp/                          # Intermediate files (e.g., text dump)
├── models/                            # Trained spaCy NER model
├── src/
│   ├── config.py                      # Path setup and logging
│   ├── pdf_processor.py               # PDF → text
│   ├── ner_trainer.py                 # Train custom NER
│   ├── entity_extractor.py           # Detect entities from text
│   ├── geo_locator.py                 # Geolocation logic (LLM)
│   └── utils.py                       # Helpers and error handling
├── tests/                             # Unit tests (pytest)
├── run_pipeline.sh                    # One-command runner
├── requirements.txt
├── README.md
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

## 🐳 Docker Setup (Optional, Recommended)

### Build Docker Image

Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.

From the project root directory, run:

```bash
docker build -t geomine-pipeline:latest .
```

### Run the Pipeline in Docker

Run the entire pipeline inside Docker, mounting your local `data` folder for input/output persistence:

```bash
docker run --rm -v "$PWD/data:/app/data" geomine-pipeline:latest
```

- `--rm` removes the container after it finishes.
- `-v "$PWD/data:/app/data"` mounts your local `data` folder into the container.

### Debug / Interactive Mode

Open an interactive shell inside the container:

```bash
docker run -it --rm -v "$PWD/data:/app/data" geomine-pipeline:latest /bin/bash
```

Inside the container shell, run the pipeline manually:

```bash
./run_pipeline.sh
```

---

## ⚙️ Local Setup (Without Docker)

### 1. Create and activate Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the pipeline

```bash
bash run_pipeline.sh
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

## 📝 License

This project is licensed under the [MIT License](LICENSE).

<sub><i>This project helps in extracting mining project names and estimating their coordinates from unstructured PDF reports using NER and geolocation. Ideal for geological data analysis, natural resource intelligence, and environmental reports.</i></sub>
