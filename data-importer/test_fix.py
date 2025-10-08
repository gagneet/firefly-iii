#!/usr/bin/env python3
"""Test the duplicate detector fix"""
import sys
sys.path.insert(0, '/home/gagneet/firefly/data-importer')

# Force reload to pick up changes
import importlib
if 'duplicate_detector' in sys.modules:
    del sys.modules['duplicate_detector']
if 'statement_parser' in sys.modules:
    del sys.modules['statement_parser']

from duplicate_detector import DuplicateDetector, Transaction
from statement_parser import StatementParser

# Test with simple transactions first
print("Test 1: Two transactions with same details but opposite amounts")
print("="*80)

txn1 = Transaction(
    date='2021-04-26',
    description='Target 5123 Belconnen',
    amount=20.00,
    account='CommBank Diamond'
)

txn2 = Transaction(
    date='2021-04-26',
    description='Target 5123 Belconnen',
    amount=-20.00,
    account='CommBank Diamond'
)

print(f"Transaction 1: {txn1.date} | ${txn1.amount:>9.2f} | {txn1.description}")
print(f"  ID: {txn1.transaction_id}")
print()
print(f"Transaction 2: {txn2.date} | ${txn2.amount:>9.2f} | {txn2.description}")
print(f"  ID: {txn2.transaction_id}")
print()

if txn1.transaction_id == txn2.transaction_id:
    print("❌ FAIL: IDs are the same (bug still exists)")
else:
    print("✓ PASS: IDs are different (refund and purchase are distinct)")

print()
print("Test 2: Real PDF statement")
print("="*80)

pdf = '/home/gagneet/home-expenses/uploads/CBA-MasterCard-6233/Statement20210524.pdf'
parser = StatementParser()
transactions = parser.parse_statement(pdf, 'commbank')

detector = DuplicateDetector()
result = detector.categorize_duplicates(transactions)

print(f"Total transactions: {len(transactions)}")
print(f"Unique: {len(result['unique'])}")
print(f"Duplicates removed: {result['stats']['exact_duplicates_removed']}")
print()

# Check if all 75 are now unique
if len(result['unique']) == 75:
    print("✓ PASS: All 75 transactions are now treated as unique")
else:
    print(f"❌ FAIL: Still removing {result['stats']['exact_duplicates_removed']} duplicate(s)")

print()
print("Transactions #12 and #17:")
for i in [11, 16]:
    txn = transactions[i]
    print(f"  #{i+1}: {txn.date} | ${txn.amount:>9.2f} | {txn.description}")
    print(f"       ID: {txn.transaction_id}")
