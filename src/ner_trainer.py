import spacy
import json
import random
from pathlib import Path
from spacy.training.example import Example

# Regex patterns for project name detection
PROJECT_PATTERNS = [
    r"\b[A-Z][a-z]+\s(?:Mine|Project|Deposit)\b",
    r"\b[A-Z]{2,}\s\d+\b",
    r"\b(?:North|South|East|West)\s[A-Z][a-z]+\b"
]

def create_training_data(annotations_path: Path):
    """Convert annotations to spaCy training format"""
    with open(annotations_path, 'r') as f:
        annotations = json.load(f)
    
    training_data = []
    for item in annotations:
        entities = []
        for annotation in item["annotations"]:
            # Ensure we only train on PROJECT entities
            if annotation["label"] == "PROJECT":
                start = annotation["start"]
                end = annotation["end"]
                entities.append((start, end, "PROJECT"))
        
        training_data.append((item["text"], {"entities": entities}))
    
    return training_data


def train_ner_model(annotations_path: Path, model_path: Path):
    """Train a new NER model"""
    # Create model directory if it doesn't exist
    model_path.mkdir(parents=True, exist_ok=True)
    
    # Create blank English model
    nlp = spacy.blank("en")
    
    # Add NER pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")
    
    ner.add_label("PROJECT")
    
    # Get training data
    train_data = create_training_data(annotations_path)
    
    # Disable other pipes during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        
        # Training loop
        for itn in range(30):  # 30 iterations
            random.shuffle(train_data)
            losses = {}
            
            # Batch training
            for batch in spacy.util.minibatch(train_data, size=2):
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    nlp.update([example], drop=0.5, losses=losses)
            
            print(f"Iteration {itn}, Losses: {losses}")
    
    # Save model
    nlp.to_disk(model_path)
    return nlp