#!/bin/bash

# Exit immediately on error
set -e

echo "Setting up environment..."
export PYTHONPATH=$PWD:$PYTHONPATH

echo "Processing PDFs..."
python3 src/pdf_processor.py

echo "Training NER model..."
python3 src/ner_trainer.py

echo "Extracting entities..."
python3 src/entity_extractor.py

echo "Geolocating projects..."
python3 src/geo_locator.py

echo "Pipeline completed! Results saved to data/output/final_results.jsonl"
