import spacy
from spacy.training import Example
import json
from pathlib import Path
import logging
import random
from spacy.util import filter_spans
from config import Config

logger = logging.getLogger(__name__)

def train_ner_model(annotations_path: Path, model_output: Path) -> None:
    # Create blank model
    nlp = spacy.blank("en")
    
    # Add NER pipeline
    ner = nlp.add_pipe("ner")
    ner.add_label("PROJECT")
    
    # Load training data
    with open(annotations_path, 'r') as f:
        data = json.load(f)
    
    # Prepare training data
    train_data = []
    for item in data:
        if 'data' in item and 'text' in item['data']:
            text = item['data']['text']
            entities = []
            for ann in item.get('annotations', []):
                for res in ann.get('result', []):
                    if 'value' in res and 'labels' in res['value']:
                        val = res['value']
                        entities.append((val['start'], val['end'], val['labels'][0]))
            train_data.append((text, {"entities": entities}))
    
    # Convert to spaCy examples with conflict resolution
    examples = []
    for text, annot in train_data:
        doc = nlp.make_doc(text)
        spans = []
        
        # Create span objects
        for start, end, label in annot["entities"]:
            span = doc.char_span(start, end, label=label)
            if span is not None:
                spans.append(span)
        
        # Resolve overlapping entities - keep the longest span
        filtered_spans = filter_spans(spans)
        
        # Create new entity annotations without overlaps
        new_entities = [(span.start_char, span.end_char, span.label_) for span in filtered_spans]
        new_annot = {"entities": new_entities}
        
        example = Example.from_dict(doc, new_annot)
        examples.append(example)
    
    # Train model
    nlp.initialize()
    for itn in range(1):  # 10 iterations
        losses = {}
        random.shuffle(examples)
        for batch in spacy.util.minibatch(examples, size=2):
            nlp.update(batch, losses=losses, drop=0.5)
        logger.info(f"Iteration {itn}, Losses: {losses}")
    
    # Save model
    nlp.to_disk(model_output)
    logger.info(f"Model saved to {model_output}")

if __name__ == "__main__":
    Config.setup_logging()
    Config.setup_directories()
    train_ner_model(
        Config.INPUT_DIR / "annotations.json",
        Config.NER_MODEL_PATH
    )