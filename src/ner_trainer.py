import spacy
from spacy.tokens import DocBin
import json
from pathlib import Path
import random
import logging
import os
from config import Config
from src.utils import handle_errors

logger = logging.getLogger(__name__)

# Reduced Training Iterations
# ===========================
# Training iterations reduced from 30 to 10 for faster development
# This is sufficient for a prototype/PoC but might need more for production

PROJECT_PATTERNS = [
    r"\b(project)\b",
    r"\b(mine)\b",
    r"\b(deposit)\b",
    r"\b(exploration)\b",
    r"\b(property)\b"
]

@handle_errors(logger, "Annotation conversion failed")
def convert_annotations(annotations_path: Path) -> DocBin:
    """Convert JSON annotations to spaCy training format with better alignment"""
    with open(annotations_path, 'r') as f:
        training_data = json.load(f)
    
    nlp = spacy.blank("en")
    db = DocBin()
    misaligned_count = 0
    total_entities = 0
    
    for example in training_data:
        text = example['text']
        annotations = example['annotations']
        doc = nlp.make_doc(text)
        ents = []
        
        for start, end, label in annotations:
            total_entities += 1
            span = doc.char_span(start, end, label=label)
            
            if span is None:
                # Try to find the closest token boundaries
                start_token = next((i for i, token in enumerate(doc) if token.idx >= start), None)
                end_token = next((i for i, token in enumerate(doc) if token.idx + len(token) >= end), None)
                
                if start_token is not None and end_token is not None:
                    span = doc[start_token:end_token+1]
                    span.label_ = label
                    ents.append(span)
                    logger.debug(f"Adjusted misaligned entity: {text[start:end]} -> {span.text}")
                else:
                    misaligned_count += 1
                    logger.warning(f"Could not align entity: '{text[start:end]}' at ({start}, {end})")
            else:
                ents.append(span)
        
        doc.ents = ents
        db.add(doc)
    
    if misaligned_count > 0:
        logger.warning(f"{misaligned_count}/{total_entities} entities could not be aligned")
    
    return db

@handle_errors(logger, "NER model training failed")
def train_ner_model(annotations_path: Path, model_output: Path, iterations: int = 10) -> None:
    """Train custom NER model with reduced iterations"""
    # Convert annotations
    training_data = json.load(open(annotations_path))
    doc_bin = convert_annotations(annotations_path)
    
    # Initialize blank English model
    nlp = spacy.blank("en")
    
    # Create NER pipeline component
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    
    # Add PROJECT label to the NER model
    ner.add_label("PROJECT")
    
    # Train model with reduced iterations
    optimizer = nlp.begin_training()
    for itn in range(iterations):
        random.shuffle(training_data)
        losses = {}
        for batch in spacy.util.minibatch(training_data, size=2):
            texts = [example['text'] for example in batch]
            annotations = [{'entities': example['annotations']} for example in batch]
            nlp.update(texts, annotations, losses=losses, drop=0.3)
        logger.info(f"NER Training Iteration {itn}, Losses: {losses}")
    
    # Save custom-trained NER model
    nlp.to_disk(model_output)
    logger.info(f"Custom NER model saved to {model_output}")

if __name__ == "__main__":
    Config.setup_directories()
    Config.setup_logging()
    
    # Reduced to 10 iterations for faster training
    train_ner_model(
        Config.INPUT_DIR / "annotations.json",
        Config.NER_MODEL_PATH,
        iterations=10  # Reduced from 30 to 10
    )
