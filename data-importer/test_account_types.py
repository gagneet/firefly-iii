#!/usr/bin/env python3
"""Test account type detection for all accounts"""
import sys
sys.path.insert(0, '/home/gagneet/firefly/data-importer')
from firefly_service import FireflyService

# Your account list
accounts = {
    'AMEX-BusinessPlatinum-43006': 'Credit Card',
    'AMEX-CashBack-71006': 'Credit Card',
    'CBA-87Hoolihan-9331': 'Everyday Savings',
    'CBA-EveryDayOffset-7964': 'Everyday Savings',
    'CBA-HomeLoan-466297723': 'Home Loan',
    'CBA-HomeLoan-466297731': 'Home Loan',
    'CBA-HomeLoan-470379959': 'Home Loan',
    'CBA-MasterCard-6233': 'Credit Card',
    'CBA-PL-466953719': 'Personal Loan',
    'ING-Everyday-64015854': 'Everyday Savings',
    'ING-Saver-45070850': 'Everyday Savings',
    'ING-Saver-817278720': 'Everyday Savings',
    'uBank-86400-Gagneet': 'Everyday Savings',
    'India-ICICI-Bank': 'Savings',
    'India-SBI-Account1': 'Savings',
    'India-SBI-Account2': 'Savings',
    'India-ING-Account': 'Savings',
}

service = FireflyService('http://dummy', 'dummy')

print("\n" + "="*90)
print("ACCOUNT TYPE DETECTION TEST")
print("="*90)
print(f"{'Account Name':<40} {'Expected':<20} {'Detected':<20} {'Status':<10}")
print("-"*90)

expected_mapping = {
    'Credit Card': 'liabilityCredit',
    'Everyday Savings': 'asset',
    'Home Loan': 'mortgage',
    'Personal Loan': 'loan',
    'Savings': 'asset',
}

correct = 0
total = 0

for account_name, expected_category in accounts.items():
    detected = service.detect_account_type(account_name)
    expected_type = expected_mapping[expected_category]
    status = '✓' if detected == expected_type else '✗'
    
    if detected == expected_type:
        correct += 1
    total += 1
    
    print(f"{account_name:<40} {expected_category:<20} {detected:<20} {status:<10}")

print("-"*90)
print(f"Accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
print("="*90)
