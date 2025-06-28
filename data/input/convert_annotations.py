import json
from pathlib import Path

def convert_annotations(input_path: Path, output_path: Path):
    """Convert Label Studio format to our expected format"""
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    converted = []
    for item in data:
        text = item.get('text') or item.get('data', {}).get('text', '')
        annotations = []
        
        for ann in item.get('annotations', []):
            for res in ann.get('result', []):
                if res.get('type') == 'labels':
                    value = res['value']
                    annotations.append({
                        "start": value['start'],
                        "end": value['end'],
                        "label": value['labels'][0].upper()  # Convert to uppercase
                    })
        
        if text and annotations:
            converted.append({
                "text": text,
                "annotations": annotations
            })
    
    with open(output_path, 'w') as f:
        json.dump(converted, f, indent=2)

if __name__ == "__main__":
    input_path = Path("annotations.json")
    output_path = Path("converted_annotations.json")
    convert_annotations(input_path, output_path)
    print(f"Converted annotations saved to {output_path}")