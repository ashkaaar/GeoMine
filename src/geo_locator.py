import os
import json
import jsonlines
import logging
import re
import requests
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from config import Config
from utils import handle_errors

logger = logging.getLogger(__name__)
load_dotenv(Config.BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME", "radixtest")  # public test account

@handle_errors(logger, "Gemini initialization failed")
def init_gemini():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in .env file")
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-pro')

@handle_errors(logger, "Gemini geolocation failed")
def infer_coordinates_gemini(context: str, model) -> Optional[Tuple[float, float]]:
    """Infer coordinates from context using Gemini"""
    prompt = f"""
    You are an expert in geography and mining. Given the following context about a mining project, 
    infer the most likely latitude and longitude coordinates. If the location is ambiguous, return null.
    Respond ONLY with the coordinates in the format [latitude, longitude] or null.
    
    Context: {context}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Extract coordinates using regex
        match = re.search(r'\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\]', text)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            return (lat, lon)
        return None
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None

@handle_errors(logger, "Geonames geolocation failed")
def infer_coordinates_geonames(location_name: str) -> Optional[Tuple[float, float]]:
    """Fallback geolocation using Geonames search"""
    base_url = "http://api.geonames.org/searchJSON"
    params = {
        "q": location_name,
        "maxRows": 1,
        "username": GEONAMES_USERNAME
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if "geonames" in data and data["geonames"]:
            place = data["geonames"][0]
            return (float(place["lat"]), float(place["lng"]))
        return None
    except Exception as e:
        logger.error(f"Geonames error: {e}")
        return None

@handle_errors(logger, "Geolocation update failed")
def update_coordinates(entities: List[Dict]) -> List[Dict]:
    """Update entities with coordinates using multi-stage approach"""
    gemini_model = init_gemini() if GEMINI_API_KEY else None
    
    for entity in entities:
        context = entity["context_sentence"]
        project_name = entity["project_name"]
        
        # Try Gemini first if available
        coords = None
        if gemini_model:
            coords = infer_coordinates_gemini(context, gemini_model)
        
        # Fallback to Geonames project name search
        if not coords:
            coords = infer_coordinates_geonames(project_name)
        
        entity["coordinates"] = list(coords) if coords else None
    
    return entities

@handle_errors(logger, "Geolocation processing failed")
def process_geolocation(input_path: Path, output_path: Path) -> None:
    """Process geolocation for all entities"""
    # Load entities
    entities = []
    with jsonlines.open(input_path) as reader:
        for entity in reader:
            entities.append(entity)
    
    # Update coordinates
    updated_entities = update_coordinates(entities)
    
    # Save results
    with jsonlines.open(output_path, "w") as writer:
        writer.write_all(updated_entities)
    logger.info(f"Geolocated {len(updated_entities)} projects")

if __name__ == "__main__":
    Config.setup_logging()
    process_geolocation(
        Config.TEMP_DIR / "entities.jsonl",
        Config.OUTPUT_DIR / "final_results.jsonl"
    )