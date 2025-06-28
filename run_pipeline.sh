#!/bin/bash

# Exit immediately on error
set -e

# Step 1: Setup environment
echo "Setting up environment..."
export PYTHONPATH=$PWD:$PYTHONPATH

# Step 2: Process PDFs
echo "Processing PDFs..."
python src/pdf_processor.py
echo "PDF processing completed successfully"

# Step 3: Extract entities
echo "Extracting entities..."
python src/entity_extractor.py
if [ ! -f "data/temp/entities.jsonl" ]; then
    echo "Error: Entity extraction failed to create output file"
    exit 1
fi
echo "Entity extraction completed successfully"

# Step 4: Geolocation
echo "Geolocating projects..."
python src/geo_locator.py
if [ ! -f "data/output/final_results.jsonl" ]; then
    echo "Error: Geolocation failed to create output file"
    exit 1
fi
echo "Geolocation completed successfully"

echo "Pipeline completed! Results saved to data/output/final_results.jsonl"
