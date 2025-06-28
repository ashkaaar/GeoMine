#!/bin/bash

# Step 1: Setup environment
echo "Setting up environment..."
export PYTHONPATH=$PWD:$PYTHONPATH  # Set to project root

# Step 2: Process PDFs
echo "Processing PDFs..."
python src/pdf_processor.py

# Step 3: Extract entities
echo "Extracting entities..."
python src/entity_extractor.py

# Step 4: Geolocation
echo "Geolocating projects..."
python src/geo_locator.py

echo "Pipeline completed! Results saved to data/output/final_results.jsonl"
