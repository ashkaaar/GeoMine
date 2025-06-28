import spacy
import json
import re
import logging
from spacy.tokens import DocBin
from pathlib import Path
from config import Config
from .utils import handle_errors

logger = logging.getLogger(__name__)

# Regex patterns for mining project names
PROJECT_PATTERNS = [
    r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Project|Mine|Deposit|Site)\b",
    r"\b(?:Mount|Mt)\.?\s+[A-Z][a-z]+\s+(?:Project|Mine)\b",
    r"\b[A-Z]{2,}\s+(?:Project|Mine)\b"
]

@handle_errors(logger, "Annotation conversion failed")
def convert_annotations(annotations_path: Path) -> DocBin:
    """Convert JSON annotations to spaCy format with regex augmentation"""
    with open(annotations_path) as f:
        data = json.load(f)
    
    nlp = spacy.blank("en")
    db = DocBin()
    
    for example in data:
        doc = nlp.make_doc(example["text"])
        ents = []
        
        # Add annotated entities
        for start, end, label in example.get("entities", []):
            span = doc.char_span(start, end, label=label)
            if span is not None:
                ents.append(span)
        
        # Augment with regex matches
        for pattern in PROJECT_PATTERNS:
            for match in re.finditer(pattern, doc.text):
                start, end = match.span()
                span = doc.char_span(start, end, label="PROJECT")
                if span and not any(span.intersects(e) for e in ents):
                    ents.append(span)
        
        doc.ents = spacy.util.filter_spans(ents)
        db.add(doc)
    
    return db

@handle_errors(logger, "Model training failed")
def train_ner_model(annotations_path: Path, model_output: Path, iterations: int = 30) -> None:
    """Train NER model with provided annotations"""
    # Convert annotations
    train_data = convert_annotations(annotations_path)
    
    # Initialize model
    nlp = spacy.blank("en")
    nlp.add_pipe("ner")
    ner = nlp.get_pipe("ner")
    ner.add_label("PROJECT")
    
    # Train model
    optimizer = nlp.begin_training()
    for i in range(iterations):
        losses = {}
        nlp.update([train_data], drop=0.2, losses=losses, sgd=optimizer)
        logger.info(f"Iteration {i+1}/{iterations}, Loss: {losses['ner']:.4f}")
    
    # Save model
    nlp.to_disk(model_output)
    logger.info(f"Model saved to {model_output}")

if __name__ == "__main__":
    Config.setup_logging()
    train_ner_model(
        annotations_path=Config.INPUT_DIR / "annotations.json",
        model_output=Config.NER_MODEL_PATH,
        iterations=Config.NER_TRAIN_ITERATIONS
    )