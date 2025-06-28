#!/bin/bash

# Exit on error
set -e

echo "Setting up environment..."
export PYTHONPATH=$PWD:$PYTHONPATH

echo "Processing PDFs..."
python src/pdf_processor.py

echo "Training NER model..."
python src/ner_trainer.py

echo "Extracting entities..."
python src/entity_extractor.py

echo "Geolocating projects..."
python src/geo_locator.py

echo "Pipeline completed! Results saved to data/output/final_results.jsonl"