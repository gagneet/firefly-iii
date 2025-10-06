#!/usr/bin/env python3
"""
Convert Australian bank PDF statements to Firefly III CSV format
Supports: AMEX, ING Orange, ING Savings, uBank, CommBank
"""

import csv
import sys
import os
from pathlib import Path
from typing import List
from statement_parser import StatementParser, Transaction


def convert_to_firefly_csv(transactions: List[Transaction], output_file: str):
    """
    Convert transactions to Firefly III CSV format

    Firefly III CSV Format:
    - date: Transaction date (YYYY-MM-DD or DD/MM/YYYY)
    - description: Transaction description
    - amount: Amount (positive for income, negative for expenses)
    - source-name: Source account name
    - destination-name: Destination account name
    - currency-code: Currency (AUD)
    - category-name: Category (optional)
    - budget-name: Budget (optional)
    - bill-name: Bill (optional)
    - tags: Comma-separated tags (optional)
    - notes: Additional notes (optional)
    - internal-reference: Internal reference (optional)
    - external-id: External ID (optional)
    """

    fieldnames = [
        'date',
        'description',
        'amount',
        'source-name',
        'destination-name',
        'currency-code',
        'category-name',
        'budget-name',
        'bill-name',
        'tags',
        'notes',
        'internal-reference',
        'external-id'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for txn in transactions:
            # For Firefly III:
            # - Expense: source = your account, destination = expense account/merchant
            # - Income: source = revenue account/employer, destination = your account
            # - Transfer: source = from account, destination = to account

            if txn.amount < 0:
                # Expense transaction
                source_name = txn.account
                destination_name = txn.description[:50]  # Use description as destination
                amount_abs = abs(txn.amount)
            else:
                # Income transaction
                source_name = txn.description[:50]  # Use description as source
                destination_name = txn.account
                amount_abs = txn.amount

            # Check if it's a transfer between own accounts
            if txn.transaction_type == 'transfer' or 'transfer' in txn.description.lower():
                # For transfers, both source and destination should be your accounts
                # You may need to customize this based on your account names
                if 'from' in txn.description.lower():
                    source_name = txn.account
                elif 'to' in txn.description.lower():
                    destination_name = txn.account

            row = {
                'date': txn.date,
                'description': txn.description,
                'amount': f"{amount_abs:.2f}",
                'source-name': source_name,
                'destination-name': destination_name,
                'currency-code': 'AUD',
                'category-name': txn.category if txn.category else '',
                'budget-name': '',
                'bill-name': '',
                'tags': f"{txn.account},{txn.transaction_type}",
                'notes': f"Imported from {txn.account}",
                'internal-reference': '',
                'external-id': ''
            }

            writer.writerow(row)

    print(f"✓ Converted {len(transactions)} transactions to {output_file}")


def main():
    """Main function to parse PDFs and convert to CSV"""

    if len(sys.argv) < 3:
        print("Usage: python convert_to_firefly_csv.py <bank_type> <pdf_file> [output_csv]")
        print("\nSupported bank types:")
        print("  - amex          (American Express)")
        print("  - ing_orange    (ING Orange Everyday)")
        print("  - ing_savings   (ING Savings Maximiser)")
        print("  - ubank         (uBank Spend Account)")
        print("  - commbank      (Commonwealth Bank)")
        print("\nExample:")
        print("  python convert_to_firefly_csv.py amex statement.pdf transactions.csv")
        sys.exit(1)

    bank_type = sys.argv[1]
    pdf_file = sys.argv[2]
    output_csv = sys.argv[3] if len(sys.argv) > 3 else 'firefly_import.csv'

    # Validate bank type
    valid_banks = ['amex', 'ing_orange', 'ing_savings', 'ubank', 'commbank']
    if bank_type not in valid_banks:
        print(f"Error: Invalid bank type '{bank_type}'")
        print(f"Must be one of: {', '.join(valid_banks)}")
        sys.exit(1)

    # Validate PDF file exists
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file not found: {pdf_file}")
        sys.exit(1)

    print(f"Parsing {bank_type} statement: {pdf_file}")

    # Parse the PDF
    parser = StatementParser()
    try:
        transactions = parser.parse_statement(pdf_file, bank_type)
        print(f"✓ Extracted {len(transactions)} transactions")
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        sys.exit(1)

    # Auto-categorize
    print("Categorizing transactions...")
    for txn in transactions:
        if not txn.category:
            txn.category = parser.categorize_transaction(txn)

    # Convert to Firefly III CSV
    convert_to_firefly_csv(transactions, output_csv)
    print(f"\n✓ Import file ready: {output_csv}")
    print(f"\nNext steps:")
    print(f"1. Copy {output_csv} to the import/ directory")
    print(f"2. Open the Data Importer at http://localhost:8081")
    print(f"3. Upload the CSV file and configure import settings")
    print(f"4. Review and complete the import")


def batch_convert():
    """Convert multiple PDF files in a directory"""

    if len(sys.argv) < 2:
        print("Usage: python convert_to_firefly_csv.py --batch <directory>")
        sys.exit(1)

    directory = sys.argv[2] if len(sys.argv) > 2 else '.'

    # Look for PDFs in directory
    pdf_files = list(Path(directory).glob('*.pdf'))

    if not pdf_files:
        print(f"No PDF files found in {directory}")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF files")

    # You'll need to specify which bank each PDF belongs to
    # This is a simple implementation - you may want to add logic to auto-detect
    parser = StatementParser()
    all_transactions = []

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")

        # Try to detect bank from filename
        filename_lower = pdf_file.name.lower()
        bank_type = None

        if 'amex' in filename_lower or 'american express' in filename_lower:
            bank_type = 'amex'
        elif 'ing' in filename_lower and 'orange' in filename_lower:
            bank_type = 'ing_orange'
        elif 'ing' in filename_lower and 'saving' in filename_lower:
            bank_type = 'ing_savings'
        elif 'ubank' in filename_lower:
            bank_type = 'ubank'
        elif 'commbank' in filename_lower or 'commonwealth' in filename_lower:
            bank_type = 'commbank'

        if not bank_type:
            print(f"  ⚠ Could not detect bank type from filename, skipping...")
            continue

        try:
            transactions = parser.parse_statement(str(pdf_file), bank_type)

            # Auto-categorize
            for txn in transactions:
                if not txn.category:
                    txn.category = parser.categorize_transaction(txn)

            all_transactions.extend(transactions)
            print(f"  ✓ Extracted {len(transactions)} transactions from {bank_type}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    if all_transactions:
        # Sort by date
        all_transactions.sort(key=lambda x: x.date)

        output_file = 'firefly_import_batch.csv'
        convert_to_firefly_csv(all_transactions, output_file)
        print(f"\n✓ Batch import complete: {output_file}")
    else:
        print("\nNo transactions extracted")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        batch_convert()
    else:
        main()
