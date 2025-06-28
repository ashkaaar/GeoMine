import spacy
import json
import jsonlines
import logging
import re
import sys
import os
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from src.utils import handle_errors
from src.ner_trainer import PROJECT_PATTERNS

logger = logging.getLogger(__name__)

@handle_errors(logger, "NER model loading failed")
def load_ner_model(model_path: Path):
    """Load custom-trained NER model with sentencizer"""
    try:
        # Ensure model directory exists
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        nlp = spacy.load(model_path)
        
        # Add sentencizer to handle sentence boundaries
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer", first=True)
            logger.info("Added sentencizer to pipeline")
            
        return nlp
    except OSError as e:
        logger.warning(f"NER model not found: {e}, training new model")
        from src.ner_trainer import train_ner_model
        train_ner_model(
            Config.INPUT_DIR / "annotations.json",
            model_path
        )
        nlp = spacy.load(model_path)
        
        # Add sentencizer to new model
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer", first=True)
            
        return nlp

def calculate_confidence(ent) -> float:
    """Calculate confidence score for NER prediction"""
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

@handle_errors(logger, "Entity extraction with NER failed")
def extract_projects(nlp, pdf_data: dict) -> List[Dict]:
    """Extract PROJECT entities using custom NER model"""
    results = []
    seen_entities = set()
    
    logger.info(f"Processing {len(pdf_data)} PDF files...")
    
    for pdf_name, pages in pdf_data.items():
        logger.info(f"Processing {pdf_name} with {len(pages)} pages")
        for page in pages:
            # Skip empty pages
            if not page["text"].strip():
                continue
                
            # Process text with our custom NER model
            doc = nlp(page["text"])
            
            # Extract all recognized PROJECT entities
            for ent in doc.ents:
                if ent.label_ == "PROJECT":
                    # Deduplication
                    entity_key = f"{pdf_name}|{page['page_number']}|{ent.text}"
                    if entity_key in seen_entities:
                        logger.debug(f"Skipping duplicate entity: {ent.text}")
                        continue
                    seen_entities.add(entity_key)
                    
                    # Get context sentence
                    try:
                        # More robust sentence boundary detection
                        context = next(
                            (sent.text for sent in doc.sents 
                             if ent.start >= sent.start and ent.end <= sent.end),
                            ent.sent.text if ent.sent else doc.text
                        )
                    except ValueError:
                        # Fallback to the entire page text if needed
                        context = page["text"][:200] + "..."  # First 200 chars
                    
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
    """Save NER extraction results in JSONL format"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(output_path, "w") as writer:
        writer.write_all(data)
    logger.info(f"Saved {len(data)} entities to {output_path}")

if __name__ == "__main__":
    Config.setup_logging()
    Config.setup_directories()
    
    # Create model directory if it doesn't exist
    Config.NER_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Load our custom-trained NER model
    logger.info("Loading NER model...")
    nlp = load_ner_model(Config.NER_MODEL_PATH)
    logger.info("NER model loaded successfully")
    
    # Load extracted text
    text_path = Config.TEMP_DIR / "pdf_texts.json"
    logger.info(f"Loading extracted text from {text_path}")
    with open(text_path, "r") as f:
        pdf_data = json.load(f)
    
    # Extract projects using NER model
    logger.info("Extracting projects...")
    projects = extract_projects(nlp, pdf_data)
    
    # Save results
    output_path = Config.TEMP_DIR / "entities.jsonl"
    save_to_jsonl(projects, output_path)
    logger.info(f"NER extracted {len(projects)} projects")
