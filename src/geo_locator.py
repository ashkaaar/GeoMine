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
    Use Gemini 2.5 Flash to infer coordinates with reasoning.
    Returns [lat, lon] or None.
    """
    prompt = f"""
You are a mining geography expert. A vague project description is provided below.

1. First, analyze the sentence for location clues (city, district, region, etc.)
2. Reason step by step to infer the most probable Indian coordinates.
3. Output ONLY the result as a JSON array [latitude, longitude] — or null if unsure.

Context:
\"\"\"{context}\"\"\"
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}]
        )
        reply = response.text.strip()

        # Safely parse reply
        if "null" in reply.lower():
            return None
        if reply.startswith("[") and reply.endswith("]"):
            parts = reply.strip("[]").split(",")
            lat, lon = float(parts[0]), float(parts[1])
            return [lat, lon]
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
