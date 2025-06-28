#!/bin/bash
set -e

echo "Setting up environment..."
export PYTHONPATH=$PWD/src:$PYTHONPATH

echo "Processing PDFs..."
python src/pdf_processor.py || { 
    echo "PDF processing failed! Check logs for details." 
    exit 1
}

echo "Extracting entities..."
python src/entity_extractor.py || {
    echo "Entity extraction failed! Check logs for details."
    exit 1
}

echo "Geolocating projects..."
python src/geo_locator.py || {
    echo "Geolocation failed! Check logs for details."
    exit 1
}

echo "Pipeline completed successfully!"
echo "Results saved to: data/output/final_results.jsonl"