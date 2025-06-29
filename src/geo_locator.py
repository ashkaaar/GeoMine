import sys
from pathlib import Path
import logging
import os
import json
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
    Use Gemini 2.5 Flash to infer coordinates from a mining project context.
    Returns [lat, lon] or None.
    """
    prompt = f"""
Context: \"{context}\"

Give best-guess geographic coordinates [latitude, longitude] for the mining project described in the context.

If no guess is possible, return null.
Respond ONLY in this format: [lat, lon] or null
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        reply = response.text.strip()

        if "null" in reply.lower():
            return None
        if reply.startswith("[") and reply.endswith("]"):
            latlon = eval(reply)
            if isinstance(latlon, list) and len(latlon) == 2:
                return [float(latlon[0]), float(latlon[1])]
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
