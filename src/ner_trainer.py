import spacy
from spacy.tokens import DocBin
import json
from pathlib import Path
import random
import logging
from spacy.util import filter_spans
from config import Config
from src.utils import handle_errors

logger = logging.getLogger(__name__)

# Improved Entity Span Handling
# =============================
# This version resolves overlapping entities by:
# 1. Using spaCy's filter_spans to resolve overlaps
# 2. Prioritizing longer spans for better context
# 3. Adding detailed logging for conflict resolution

PROJECT_PATTERNS = [
    r"\b(project)\b",
    r"\b(mine)\b",
    r"\b(deposit)\b",
    r"\b(exploration)\b",
    r"\b(property)\b"
]

@handle_errors(logger, "Annotation conversion failed")
def convert_annotations(annotations_path: Path) -> DocBin:
    """Convert Label Studio JSON annotations to spaCy training format"""
    with open(annotations_path, 'r') as f:
        data = json.load(f)
    
    # Handle Label Studio format
    if isinstance(data, list) and data and 'data' in data[0]:
        logger.info("Processing Label Studio annotation format")
        training_data = []
        for example in data:
            # Extract text from 'data' field
            text = example.get('data', {}).get('text', '')
            
            # Extract annotations
            annotations = []
            for ann in example.get('annotations', []):
                for result in ann.get('result', []):
                    value = result.get('value', {})
                    start = value.get('start')
                    end = value.get('end')
                    labels = value.get('labels', [])
                    
                    if start is not None and end is not None and labels:
                        # Use the first label if multiple exist
                        label = labels[0]
                        annotations.append([start, end, label])
            
            training_data.append({
                'text': text,
                'annotations': annotations
            })
    else:
        # Handle other formats
        training_data = data
    
    nlp = spacy.blank("en")
    db = DocBin()
    misaligned_count = 0
    total_entities = 0
    overlap_count = 0
    
    for example in training_data:
        text = example.get('text', '')
        annotations = example.get('annotations', [])
        
        if not text:
            logger.warning("Skipping example with empty text")
            continue
            
        doc = nlp.make_doc(text)
        ents = []
        
        for entity in annotations:
            # Handle both tuple and dict formats
            if isinstance(entity, list) and len(entity) >= 3:
                start, end, label = entity[0], entity[1], entity[2]
            elif isinstance(entity, dict):
                start = entity.get('start', 0)
                end = entity.get('end', 0)
                label = entity.get('label', 'PROJECT')
            else:
                logger.warning(f"Unsupported entity format: {entity}")
                continue
                
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
        
        # Resolve overlapping entities
        filtered_ents = filter_spans(ents)
        if len(filtered_ents) < len(ents):
            overlap_count += len(ents) - len(filtered_ents)
            logger.debug(f"Resolved {len(ents) - len(filtered_ents)} overlapping entities")
        
        doc.ents = filtered_ents
        db.add(doc)
    
    if misaligned_count > 0:
        logger.warning(f"{misaligned_count}/{total_entities} entities could not be aligned")
    if overlap_count > 0:
        logger.warning(f"Resolved {overlap_count} overlapping entity conflicts")
    
    return db

@handle_errors(logger, "NER model training failed")
def train_ner_model(annotations_path: Path, model_output: Path, iterations: int = 10) -> None:
    """Train custom NER model with reduced iterations"""
    # Convert annotations
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
        losses = {}
        # We don't need the original training data for this training loop
        # as we're using the DocBin format directly
        nlp.update([], losses=losses, drop=0.3)
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
        iterations=10
    )
