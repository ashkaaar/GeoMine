from pathlib import Path

class Config:
    # Base directory should be the project root
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Input directories (relative to project root)
    INPUT_DIR = BASE_DIR / "data" / "input"
    PDF_DIR = INPUT_DIR / "pdf_reports"
    ANNOTATIONS_FILE = INPUT_DIR / "converted_annotations.json"
    
    # Output directories (relative to project root)
    OUTPUT_DIR = BASE_DIR / "data" / "output"
    TEMP_DIR = BASE_DIR / "data" / "temp"
    
    # Model paths
    NER_MODEL_PATH = BASE_DIR / "ner_model"
    
    @staticmethod
    def setup_logging():
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("pipeline.log"),
                logging.StreamHandler()
            ]
        )