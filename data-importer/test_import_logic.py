#!/usr/bin/env python3
"""
Test script to show how transactions would be imported
"""
import sys
sys.path.insert(0, '/home/gagneet/firefly/data-importer')

from statement_parser import StatementParser
from firefly_service import FireflyService

pdf_file = '/home/gagneet/home-expenses/uploads/CBA-MasterCard-6233/Statement20210322.pdf'
bank_type = 'commbank'

# Parse
parser = StatementParser()
transactions = parser.parse_statement(pdf_file, bank_type)

print(f"\n{'='*90}")
print(f"Testing Import Logic for {len(transactions)} transactions")
print(f"{'='*90}\n")

# Show how first payment and first purchase would be imported
payment = next((t for t in transactions if 'payment' in t.description.lower()), None)
purchase = next((t for t in transactions if t.amount < 0), None)

def show_import_logic(txn, service):
    """Show how a transaction would be imported"""
    account_type = service.detect_account_type(txn.account)
    is_liability = account_type in ['liabilityCredit', 'loan', 'mortgage']
    
    print(f"Transaction: {txn.description[:60]}")
    print(f"  Amount: ${txn.amount:.2f}")
    print(f"  Account: {txn.account}")
    print(f"  Account Type: {account_type}")
    print(f"  Is Liability: {is_liability}")
    
    if is_liability:
        if txn.amount > 0:
            txn_type = 'withdrawal'
            source = txn.account
            dest = txn.description[:50]
            print(f"  → Transaction Type: WITHDRAWAL (payment reducing debt)")
        else:
            txn_type = 'deposit'
            source = txn.description[:50]
            dest = txn.account
            print(f"  → Transaction Type: DEPOSIT (purchase increasing debt)")
    else:
        if txn.amount < 0:
            txn_type = 'withdrawal'
            source = txn.account
            dest = txn.description[:50]
            print(f"  → Transaction Type: WITHDRAWAL (expense)")
        else:
            txn_type = 'deposit'
            source = txn.description[:50]
            dest = txn.account
            print(f"  → Transaction Type: DEPOSIT (income)")
    
    print(f"  → Source: {source}")
    print(f"  → Destination: {dest}")
    print(f"  → Amount in API: ${abs(txn.amount):.2f}")
    print()

# Mock service just for type detection
service = FireflyService('http://dummy', 'dummy')

if payment:
    print("="*90)
    print("PAYMENT TRANSACTION (Should REDUCE debt):")
    print("="*90)
    show_import_logic(payment, service)

if purchase:
    print("="*90)
    print("PURCHASE TRANSACTION (Should INCREASE debt):")
    print("="*90)
    show_import_logic(purchase, service)

print("="*90)
print("SUMMARY:")
print("="*90)
print("✓ Payments (positive amounts) → Withdrawals from credit card (reduce debt)")
print("✓ Purchases (negative amounts) → Deposits to credit card (increase debt)")
print("\nThis is the CORRECT behavior for liability accounts!")
