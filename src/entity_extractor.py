import spacy
import json
import jsonlines
import logging
import re
from pathlib import Path
from typing import List, Dict
from config import Config
from utils import handle_errors
from ner_trainer import PROJECT_PATTERNS

logger = logging.getLogger(__name__)

@handle_errors(logger, "Model loading failed")
def load_ner_model(model_path: Path):
    """Load trained NER model with fallback to training"""
    try:
        # Check if model directory exists and has files
        if model_path.exists() and any(model_path.iterdir()):
            return spacy.load(model_path)
        else:
            raise OSError("Model directory empty")
    except (OSError, IOError):
        logger.warning("Model not found, training new model")
        from ner_trainer import train_ner_model
        train_ner_model(
            Config.ANNOTATIONS_FILE,  # Use the correct config path
            model_path
        )
        return spacy.load(model_path)

def calculate_confidence(ent) -> float:
    """Calculate confidence score based on entity properties"""
    confidence = 0.7  # Base confidence
    
    # Length-based confidence
    if len(ent.text) > 15:
        confidence += 0.15
    elif len(ent.text) > 10:
        confidence += 0.1
    
    # Regex pattern match
    if any(re.search(pattern, ent.text) for pattern in PROJECT_PATTERNS):
        confidence += 0.1
    
    # Location context bonus
    location_terms = ["region", "province", "state", "near", "located"]
    if any(term in ent.sent.text.lower() for term in location_terms):
        confidence += 0.05
    
    return min(0.99, round(confidence, 2))

@handle_errors(logger, "Entity extraction failed")
def extract_projects(nlp, pdf_data: dict) -> List[Dict]:
    """Extract projects from processed PDF data"""
    results = []
    seen_entities = set()
    
    for pdf_name, pages in pdf_data.items():
        for page in pages:
            doc = nlp(page["text"])
            for ent in doc.ents:
                if ent.label_ == "PROJECT":
                    # Deduplication
                    entity_key = f"{pdf_name}|{page['page_number']}|{ent.text}"
                    if entity_key in seen_entities:
                        continue
                    seen_entities.add(entity_key)
                    
                    # Get context sentence
                    context = next(
                        (sent.text for sent in doc.sents 
                         if ent.start >= sent.start and ent.end <= sent.end),
                        ent.sent.text
                    )
                    
                    results.append({
                        "pdf_file": pdf_name,
                        "page_number": page["page_number"],
                        "project_name": ent.text,
                        "context_sentence": context,
                        "confidence": calculate_confidence(ent),
                        "coordinates": None
                    })
    return results

@handle_errors(logger, "Output saving failed")
def save_to_jsonl(data: List[Dict], output_path: Path) -> None:
    """Save results in JSONL format"""
    with jsonlines.open(output_path, "w") as writer:
        writer.write_all(data)

if __name__ == "__main__":
    Config.setup_logging()
    nlp = load_ner_model(Config.NER_MODEL_PATH)
    
    # Load extracted text
    with open(Config.TEMP_DIR / "pdf_texts.json", "r") as f:
        pdf_data = json.load(f)
    
    # Extract projects
    projects = extract_projects(nlp, pdf_data)
    
    # Save results
    save_to_jsonl(projects, Config.TEMP_DIR / "entities.jsonl")
    logger.info(f"Extracted {len(projects)} projects")