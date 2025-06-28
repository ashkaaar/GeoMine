import pdfplumber
import json
from pathlib import Path
import logging
from config import Config

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: Path) -> list:
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                pages.append({
                    "page_number": i,
                    "text": text
                })
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {e}")
    return pages

def process_pdfs(input_dir: Path, output_path: Path) -> None:
    pdf_texts = {}
    for pdf_file in input_dir.glob("*.pdf"):
        logger.info(f"Processing {pdf_file.name}")
        pages = extract_text_from_pdf(pdf_file)
        pdf_texts[pdf_file.name] = pages
    
    with open(output_path, 'w') as f:
        json.dump(pdf_texts, f, indent=2)
    logger.info(f"Saved text from {len(pdf_texts)} PDFs to {output_path}")

if __name__ == "__main__":
    Config.setup_directories()
    Config.setup_logging()
    process_pdfs(
        Config.INPUT_DIR / "pdf_reports",
        Config.TEMP_DIR / "pdf_texts.json"
    )