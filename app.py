import json
import re
import pdfplumber
from pathlib import Path
from geopy.geocoders import Nominatim

INPUT_DIR = Path("input/pdf_reports")
OUTPUT_FILE = Path("output/results.jsonl")

COUNTRY_COORDS = {
    "Australia": [133.77, -25.27],
    "Canada": [-106.35, 56.13],
    "Chile": [-71.54, -35.67],
    "Peru": [-75.0, -9.0],
    "South Africa": [24.0, -29.0],
    "USA": [-98.58, 39.83]
}

def extract_text_from_pdf(pdf_path: Path) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except:
        pass
    return text

def find_projects(text: str) -> list[dict]:
    projects = []
    patterns = [
        r'\b([A-Z][a-zA-Z\s]+?Project)\b',
        r'\b([A-Z][a-zA-Z\s]+?Mine)\b',
        r'\b([A-Z][a-zA-Z\s]+?Deposit)\b'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for name in matches:
            m = re.search(rf'[^.]*?{re.escape(name)}[^.]*\.', text)
            context = m.group(0).strip() if m else ""
            projects.append({
                "name": name,
                "context": context
            })
    return projects

def get_coordinates(context: str) -> list[float] | None:
    for country, coords in COUNTRY_COORDS.items():
        if country.lower() in context.lower():
            return coords
    try:
        geolocator = Nominatim(user_agent="mining_locator")
        location = geolocator.geocode(context.split('.')[0], exactly_one=True)
        if location:
            return [location.longitude, location.latitude]
    except:
        pass
    return None

def main():
    results = []
    for pdf_file in INPUT_DIR.glob("*.pdf"):
        text = extract_text_from_pdf(pdf_file)
        if not text:
            continue
        projects = find_projects(text)
        for project in projects:
            coords = get_coordinates(project["context"])
            results.append({
                "pdf_file": pdf_file.name,
                "page_number": 1,
                "project_name": project["name"],
                "context_sentence": project["context"],
                "coordinates": coords
            })
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    main()
