import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))  # add src/ to path

import jsonlines
import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv
from config import Config
from geopy.geocoders import GeoNames


logger = logging.getLogger(__name__)
load_dotenv(Config.BASE_DIR / ".env")

def setup_gemini():
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-pro")
    except Exception as e:
        logger.warning(f"Gemini unavailable: {e}")
        return None

def infer_coordinates(context: str, gemini_model) -> list:
    """Try Gemini API first, fallback to GeoNames"""
    if gemini_model:
        try:
            prompt = f"""Given this context about a mining project: "{context.strip()}"
            What are the most likely latitude and longitude coordinates?
            Respond ONLY with coordinates like: [latitude, longitude]
            If unsure, respond with null."""
            response = gemini_model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("[") and text.endswith("]"):
                coords = eval(text)
                if isinstance(coords, list) and len(coords) == 2:
                    return coords
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")

    # ➤ Fallback to GeoNames
    try:
        username = os.getenv("GEONAMES_USERNAME")
        if not username:
            raise ValueError("GEONAMES_USERNAME not set in .env")
        geolocator = GeoNames(username=username)
        location = geolocator.geocode(context)
        if location:
            return [location.latitude, location.longitude]
    except Exception as e:
        logger.warning(f"GeoNames failed: {e}")

    return None

if __name__ == "__main__":
    Config.setup_logging()
    Config.setup_directories()

    gemini_model = setup_gemini()

    entities = []
    with jsonlines.open(Config.TEMP_DIR / "entities.jsonl") as reader:
        for entity in reader:
            entities.append(entity)

    for entity in entities:
        context = entity.get("context_sentence", "")
        entity["coordinates"] = infer_coordinates(context, gemini_model)

    with jsonlines.open(Config.OUTPUT_DIR / "final_results.jsonl", "w") as writer:
        writer.write_all(entities)

    logger.info(f"Geolocated {len(entities)} projects")
