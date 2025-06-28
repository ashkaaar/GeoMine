import os
import time
import jsonlines
import google.generativeai as genai
import logging
import re
from geopy.geocoders import GeoNames
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv
from config import Config
from .utils import handle_errors

logger = logging.getLogger(__name__)
load_dotenv(Config.BASE_DIR / ".env")

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')
else:
    logger.warning("Gemini API key not found. Using Geonames only")

# Initialize Geonames
GEONAMES_USER = os.getenv("GEONAMES_USERNAME")
geolocator = GeoNames(username=GEONAMES_USER) if GEONAMES_USER else None

def extract_location_keywords(context: str) -> str:
    """Extract location keywords from context"""
    patterns = [
        r"\b(?:near|in|at|close to|region of)\s+([A-Z][a-zA-Z\s,]+)",
        r"\b([A-Z][a-z]+\s*(?:Region|Province|State|Territory))\b",
        r"\b([A-Z]{2,})\b"  # State abbreviations
    ]
    
    locations = []
    for pattern in patterns:
        matches = re.findall(pattern, context)
        locations.extend(matches)
    
    return ", ".join(set(locations)) if locations else context[:100]

@handle_errors(logger, "Gemini geolocation failed", default=None)
def gemini_geolocate(context: str) -> Optional[List[float]]:
    """Infer coordinates using Gemini API"""
    if not GEMINI_API_KEY:
        return None
        
    prompt = f"""
    As a geological expert, determine coordinates for mining projects based on context.
    Respond ONLY with coordinates as [latitude, longitude] or 'null' if uncertain.
    
    Context: {context}
    
    Examples:
    "Western Australia" → [-25.2744, 133.7751]
    "Near Lima, Peru" → [-12.0464, -77.0428]
    "No location" → null
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        result