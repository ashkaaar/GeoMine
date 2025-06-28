import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))  # Add src/ to path

import jsonlines
import logging
import os
from dotenv import load_dotenv
from config import Config
from geopy.geocoders import GeoNames

logger = logging.getLogger(__name__)
load_dotenv(Config.BASE_DIR / ".env")

def infer_coordinates(context: str) -> list:
    """Geolocation using GeoNames API"""
    try:
        username = os.getenv("GEONAMES_USERNAME")
        if not username:
            raise ValueError("GEONAMES_USERNAME not set in .env")

        geolocator = GeoNames(username=username)
        location = geolocator.geocode(context)

        if location:
            return [location.latitude, location.longitude]
    except Exception as e:
        logger.warning(f"GeoNames geolocation failed: {e}")

    return None

if __name__ == "__main__":
    Config.setup_logging()
    Config.setup_directories()

    entities = []
    with jsonlines.open(Config.TEMP_DIR / "entities.jsonl") as reader:
        for entity in reader:
            entities.append(entity)

    for entity in entities:
        context = entity.get("context_sentence", "")
        entity["coordinates"] = infer_coordinates(context)

    with jsonlines.open(Config.OUTPUT_DIR / "final_results.jsonl", "w") as writer:
        writer.write_all(entities)

    logger.info(f"Geolocated {len(entities)} projects")
