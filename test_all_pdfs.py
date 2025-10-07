#!/usr/bin/env python3
"""Test all PDFs in a folder"""

import sys
import os
import glob

sys.path.insert(0, 'data-importer')
from statement_parser import StatementParser

def test_all_pdfs(folder_path, bank_type):
    parser = StatementParser()
    pdfs = sorted(glob.glob(os.path.join(folder_path, '*.pdf')))

    print(f"Found {len(pdfs)} PDF files\n")

    results = []
    for pdf_path in pdfs:
        filename = os.path.basename(pdf_path)
        try:
            transactions = parser.parse_statement(pdf_path, bank_type)
            total_income = sum(t.amount for t in transactions if t.amount > 0)
            total_expense = sum(abs(t.amount) for t in transactions if t.amount < 0)

            result = {
                'file': filename,
                'count': len(transactions),
                'income': total_income,
                'expense': total_expense,
                'net': total_income - total_expense
            }
            results.append(result)

            print(f"✓ {filename:40} {len(transactions):3} txns  Income: ${total_income:8.2f}  Expense: ${total_expense:8.2f}")
        except Exception as e:
            print(f"✗ {filename:40} ERROR: {str(e)}")
            results.append({'file': filename, 'count': 0, 'error': str(e)})

    print("\n" + "="*100)
    print(f"Summary: {len(pdfs)} files, {sum(r['count'] for r in results)} total transactions")
    return results

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: test_all_pdfs.py <folder_path> <bank_type>")
        sys.exit(1)

    test_all_pdfs(sys.argv[1], sys.argv[2])
