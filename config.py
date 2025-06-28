# config.py
import os
from pathlib import Path

class Config:
    # Directory setup
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    INPUT_DIR = DATA_DIR / "input"
    PDF_DIR = INPUT_DIR / "pdf_reports"
    OUTPUT_DIR = DATA_DIR / "output"
    TEMP_DIR = DATA_DIR / "temp"
    
    # Create directories
    for d in [PDF_DIR, OUTPUT_DIR, TEMP_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Geolocation settings
    GEOLOC_MAX_RETRIES = 3
    GEOLOC_TIMEOUT = 10
    
    # NER settings
    NER_MODEL_PATH = BASE_DIR / "ner_model"
    NER_TRAIN_ITERATIONS = 30
    
    @staticmethod
    def setup_logging():
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("pipeline.log"),
                logging.StreamHandler()
            ]
        )