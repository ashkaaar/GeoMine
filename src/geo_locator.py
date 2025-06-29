import sys
from pathlib import Path
import logging
import os
import json
import re
from dotenv import load_dotenv
from config import Config
from google import genai

# Setup
logger = logging.getLogger(__name__)
load_dotenv(Config.BASE_DIR / ".env")
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

def infer_coordinates_with_llm(context: str) -> list:
    """
    Use Gemini 2.5 Flash to infer coordinates with reasoning.
    Returns [lat, lon] or None.
    """
    prompt = f"""
You are a mining geography expert. A vague project description is provided below.

1. Analyze the sentence for location clues (e.g., district, region, nearby mines).
2. If a precise match isn't possible, use your knowledge of mining regions in India or Australia to guess approximate coordinates.
3. Output ONLY a JSON array like [latitude, longitude]. If it's completely ambiguous, return null.

Context:
\"\"\"{context}\"\"\"
"""


    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        reply = response.text.strip()

        # Regex to extract [lat, lon] safely
        match = re.search(r"\[\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*\]", reply)
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            return [lat, lon]
        else:
            logger.warning(f"Could not parse coords from Gemini response: {reply}")
            return None
    except Exception as e:
        logger.warning(f"Gemini coordinate inference failed: {e}")
        return None

if __name__ == "__main__":
    Config.setup_logging()
    Config.setup_directories()

    input_path = Config.TEMP_DIR / "entities.jsonl"
    output_path = Config.OUTPUT_DIR / "final_results.jsonl"

    entities = []
    with open(input_path, "r") as f:
        for line in f:
            entity = json.loads(line)
            context = entity.get("context_sentence", "")
            coords = infer_coordinates_with_llm(context)
            entity["coordinates"] = coords
            entities.append(entity)

    with open(output_path, "w") as f:
        for entity in entities:
            f.write(json.dumps(entity) + "\n")

    logger.info(f"Inferred coordinates for {len(entities)} entities. Output saved to: {output_path}")
