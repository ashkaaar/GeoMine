import spacy
import json
import jsonlines
import logging
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

def extract_projects(pdf_data: dict, nlp):
    results = []
    for pdf_name, pages in pdf_data.items():
        for page in pages:
            text = page["text"]
            if not text.strip():
                continue
                
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PROJECT":
                    results.append({
                        "pdf_file": pdf_name,
                        "page_number": page["page_number"],
                        "project_name": ent.text,
                        "context_sentence": ent.sent.text if ent.sent else "",
                        "confidence": 0.8,  # Simple confidence
                        "coordinates": None
                    })
    return results

if __name__ == "__main__":
    Config.setup_logging()
    Config.setup_directories()
    
    # Load model
    nlp = spacy.load(Config.NER_MODEL_PATH)
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")
    
    # Load extracted text
    with open(Config.TEMP_DIR / "pdf_texts.json", "r") as f:
        pdf_data = json.load(f)
    
    # Extract projects
    projects = extract_projects(pdf_data, nlp)
    
    # Save results
    with jsonlines.open(Config.TEMP_DIR / "entities.jsonl", "w") as writer:
        writer.write_all(projects)
    
    logger.info(f"Extracted {len(projects)} projects")
