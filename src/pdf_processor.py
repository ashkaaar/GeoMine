import pdfplumber
import json
import logging
from pathlib import Path
from config import Config
from utils import handle_errors

logger = logging.getLogger(__name__)

@handle_errors(logger, "PDF text extraction failed")
def extract_text_from_pdf(pdf_path: Path) -> list[dict]:
    """Extract text with page numbers preserving document structure"""
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    logger.warning(f"Empty page {i} in {pdf_path.name}")
                    continue
                pages.append({
                    "page_number": i,
                    "text": text
                })
        logger.info(f"Extracted {len(pages)} pages from {pdf_path.name}")
        return pages
    except Exception as e:
        logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
        return []

@handle_errors(logger, "PDF processing failed")
def process_pdfs(input_dir: Path, output_path: Path) -> dict:
    """Process all PDFs in directory"""
    results = {}
    for pdf_file in input_dir.glob("*.pdf"):
        if pdf_file.suffix.lower() != ".pdf":
            continue
        logger.info(f"Processing {pdf_file.name}")
        pages = extract_text_from_pdf(pdf_file)
        results[pdf_file.name] = pages
    
    # Save intermediate output
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved text from {len(results)} PDFs to {output_path}")
    return results

if __name__ == "__main__":
    Config.setup_logging()
    process_pdfs(
        Config.PDF_DIR,
        Config.TEMP_DIR / "pdf_texts.json"
    )