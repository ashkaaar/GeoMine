import logging
from pathlib import Path
import os

class Config:
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    INPUT_DIR = BASE_DIR / "data" / "input"
    OUTPUT_DIR = BASE_DIR / "data" / "output"
    TEMP_DIR = BASE_DIR / "data" / "temp"
    NER_MODEL_PATH = BASE_DIR / "models" / "ner_model"
    
    @classmethod
    def setup_directories(cls):
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        cls.NER_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def setup_logging(cls):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.BASE_DIR / "pipeline.log"),
                logging.StreamHandler()
            ]
        )
