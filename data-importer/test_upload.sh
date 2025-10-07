#!/bin/bash
# Test script to simulate what the PHP controller does

PDF_PATH="/home/gagneet/home-expenses/uploads/Statement20250416.pdf"
BANK_TYPE="commbank"
FIREFLY_URL="https://firefly.gagneet.com"
ACCESS_TOKEN="$1"  # Pass token as first argument

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Usage: $0 <access_token>"
    exit 1
fi

echo "Testing statement import..."
echo "PDF: $PDF_PATH"
echo "Bank: $BANK_TYPE"
echo "URL: $FIREFLY_URL"
echo ""

cd /home/gagneet/firefly/data-importer

python3 firefly_service.py "$BANK_TYPE" "$PDF_PATH" "$FIREFLY_URL" "$ACCESS_TOKEN" "1" "1"
