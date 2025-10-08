#!/usr/bin/env python3
"""
Test script to parse a PDF and show transactions without uploading
"""
import sys
from statement_parser import StatementParser

if len(sys.argv) < 3:
    print("Usage: python test_parser.py <bank_type> <pdf_file>")
    sys.exit(1)

bank_type = sys.argv[1]
pdf_file = sys.argv[2]

parser = StatementParser()
transactions = parser.parse_statement(pdf_file, bank_type)

if not transactions:
    print("No transactions found!")
    sys.exit(1)

# Show first 10 transactions
print(f"\n{'='*80}")
print(f"Parsed {len(transactions)} transactions from {pdf_file}")
print(f"{'='*80}\n")

# Look specifically for payments
payments = [t for t in transactions if 'payment' in t.description.lower() or 'thank you' in t.description.lower()]

if payments:
    print(f"Found {len(payments)} PAYMENT transactions:\n")
    print(f"{'Date':<12} {'Description':<50} {'Amount':>12} {'Type':<10}")
    print("-" * 88)

    for txn in payments[:10]:
        print(f"{txn.date:<12} {txn.description[:48]:<50} ${txn.amount:>10.2f} {txn.transaction_type:<10}")
else:
    print("No payment transactions found.\n")

# Show some regular transactions
print(f"\n\nFirst 5 regular transactions:\n")
print(f"{'Date':<12} {'Description':<50} {'Amount':>12} {'Type':<10}")
print("-" * 88)

for txn in transactions[:5]:
    print(f"{txn.date:<12} {txn.description[:48]:<50} ${txn.amount:>10.2f} {txn.transaction_type:<10}")
