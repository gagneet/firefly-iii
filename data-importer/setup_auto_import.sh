#!/bin/bash
#
# Automated Import Setup Script
# This script helps set up automated bank statement imports
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Firefly III Auto-Import Setup"
echo "========================================="
echo ""

# Check if Python dependencies are installed
echo "✓ Checking Python dependencies..."
if ! python3 -c "import pdfplumber" 2>/dev/null; then
    echo "⚠ pdfplumber not found. Installing..."
    pip install -r requirements.txt
else
    echo "✓ pdfplumber is installed"
fi

# Check if Docker container is running
echo "✓ Checking Data Importer container..."
if ! docker ps | grep -q firefly_importer; then
    echo "❌ Data Importer is not running!"
    echo "Starting container..."
    docker compose up -d
    sleep 5
fi

if docker ps | grep -q firefly_importer; then
    echo "✓ Data Importer is running"
else
    echo "❌ Failed to start Data Importer"
    exit 1
fi

# Check if Personal Access Token is configured
echo "✓ Checking authentication..."
if grep -q "FIREFLY_III_ACCESS_TOKEN=$" .importer.env || grep -q "FIREFLY_III_ACCESS_TOKEN=\"\"" .importer.env; then
    echo ""
    echo "⚠ WARNING: Personal Access Token not configured!"
    echo ""
    echo "To configure authentication:"
    echo "1. Go to https://firefly.gagneet.com"
    echo "2. Navigate to Options > Profile > OAuth"
    echo "3. Click 'Create New Token'"
    echo "4. Copy the token and run:"
    echo "   nano .importer.env"
    echo "5. Set FIREFLY_III_ACCESS_TOKEN=your_token_here"
    echo "6. Save and run: docker compose restart"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
else
    echo "✓ Authentication configured"
fi

# Create directories if they don't exist
echo "✓ Setting up directories..."
mkdir -p "$SCRIPT_DIR/import"
mkdir -p "$SCRIPT_DIR/configurations"
mkdir -p "$HOME/bank_statements"

echo "✓ Directories ready:"
echo "  - Import: $SCRIPT_DIR/import"
echo "  - Configurations: $SCRIPT_DIR/configurations"
echo "  - Statements: $HOME/bank_statements"

# Create example cron script
echo ""
echo "========================================="
echo "Setting up automated import script"
echo "========================================="

cat > "$SCRIPT_DIR/auto_import.sh" << 'CRON_SCRIPT'
#!/bin/bash
#
# Automated Bank Statement Import
# Run this script via cron to automatically import bank statements
#

IMPORT_DIR="/home/gagneet/firefly/data-importer"
STATEMENTS_DIR="$HOME/bank_statements"
LOG_FILE="$IMPORT_DIR/auto_import.log"

cd "$IMPORT_DIR"

echo "[$(date)] Starting automated import" >> "$LOG_FILE"

# Find all PDF files in statements directory
PDF_COUNT=$(find "$STATEMENTS_DIR" -name "*.pdf" -type f | wc -l)

if [ "$PDF_COUNT" -eq 0 ]; then
    echo "[$(date)] No PDF files found in $STATEMENTS_DIR" >> "$LOG_FILE"
    exit 0
fi

echo "[$(date)] Found $PDF_COUNT PDF files" >> "$LOG_FILE"

# Convert all PDFs to CSV
python3 convert_to_firefly_csv.py --batch "$STATEMENTS_DIR" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date)] Successfully converted statements" >> "$LOG_FILE"

    # Move CSV to import directory
    if [ -f "firefly_import_batch.csv" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        cp firefly_import_batch.csv "import/import_$TIMESTAMP.csv"
        echo "[$(date)] CSV ready for import: import_$TIMESTAMP.csv" >> "$LOG_FILE"

        # Archive processed PDFs
        ARCHIVE_DIR="$HOME/bank_statements_processed/$(date +%Y%m)"
        mkdir -p "$ARCHIVE_DIR"
        mv "$STATEMENTS_DIR"/*.pdf "$ARCHIVE_DIR/"
        echo "[$(date)] Archived PDFs to $ARCHIVE_DIR" >> "$LOG_FILE"
    fi
else
    echo "[$(date)] Error converting statements" >> "$LOG_FILE"
    exit 1
fi

echo "[$(date)] Import complete" >> "$LOG_FILE"
CRON_SCRIPT

chmod +x "$SCRIPT_DIR/auto_import.sh"
echo "✓ Created automated import script: $SCRIPT_DIR/auto_import.sh"

# Offer to set up cron job
echo ""
echo "========================================="
echo "Cron Job Setup (Optional)"
echo "========================================="
echo ""
echo "Would you like to set up a cron job for automated imports?"
echo "This will run the import script daily at 9 AM."
echo ""
read -p "Set up cron job? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    CRON_LINE="0 9 * * * $SCRIPT_DIR/auto_import.sh"

    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "auto_import.sh"; then
        echo "⚠ Cron job already exists"
    else
        # Add cron job
        (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
        echo "✓ Cron job added"
        echo "  Schedule: Daily at 9:00 AM"
        echo "  Command: $SCRIPT_DIR/auto_import.sh"
    fi

    echo ""
    echo "To view your cron jobs: crontab -l"
    echo "To edit cron jobs: crontab -e"
    echo "To remove this job: crontab -e (then delete the line)"
else
    echo "⊘ Skipped cron job setup"
    echo ""
    echo "To run imports manually:"
    echo "  $SCRIPT_DIR/auto_import.sh"
fi

# Create a test import script
cat > "$SCRIPT_DIR/test_import.sh" << 'TEST_SCRIPT'
#!/bin/bash
#
# Test Import - Process a single statement
#

if [ $# -lt 2 ]; then
    echo "Usage: ./test_import.sh <bank_type> <pdf_file>"
    echo ""
    echo "Supported banks: amex, ing_orange, ing_savings, ubank, commbank"
    echo ""
    echo "Example:"
    echo "  ./test_import.sh amex ~/Downloads/amex_statement.pdf"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BANK_TYPE="$1"
PDF_FILE="$2"

echo "Converting $BANK_TYPE statement: $PDF_FILE"
python3 convert_to_firefly_csv.py "$BANK_TYPE" "$PDF_FILE"

if [ $? -eq 0 ] && [ -f "firefly_import.csv" ]; then
    echo ""
    echo "✓ Conversion successful!"
    echo "  CSV created: firefly_import.csv"
    echo ""
    echo "Preview (first 5 transactions):"
    head -6 firefly_import.csv | column -t -s,
    echo ""
    echo "Next steps:"
    echo "1. Copy to import directory: cp firefly_import.csv import/"
    echo "2. Open Data Importer: http://localhost:8081"
    echo "3. Import the CSV file"
else
    echo ""
    echo "❌ Conversion failed"
    exit 1
fi
TEST_SCRIPT

chmod +x "$SCRIPT_DIR/test_import.sh"
echo "✓ Created test import script: $SCRIPT_DIR/test_import.sh"

# Summary
echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "What was created:"
echo "  ✓ Automated import script: $SCRIPT_DIR/auto_import.sh"
echo "  ✓ Test import script: $SCRIPT_DIR/test_import.sh"
echo "  ✓ Directory for statements: $HOME/bank_statements"
echo ""
echo "How to use:"
echo ""
echo "1. Test with a single statement:"
echo "   $SCRIPT_DIR/test_import.sh amex ~/Downloads/statement.pdf"
echo ""
echo "2. Run automated batch import:"
echo "   - Place PDFs in: $HOME/bank_statements"
echo "   - Run: $SCRIPT_DIR/auto_import.sh"
echo ""
echo "3. Import via web interface:"
echo "   - Open: http://localhost:8081"
echo "   - Upload CSV from: $SCRIPT_DIR/import/"
echo ""
echo "Logs: $SCRIPT_DIR/auto_import.log"
echo ""
echo "========================================="
echo ""
