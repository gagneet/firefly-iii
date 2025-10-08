#!/usr/bin/env python3
"""Test merchant name normalization"""
import sys
sys.path.insert(0, '/home/gagneet/firefly/data-importer')

from firefly_service import FireflyService

# Test cases
test_cases = [
    "WOOLWORTHS 1234 BELCONNEN AUS",
    "WOOLWORTHS 5678 GUNGAHLIN AUS Card xx1234",
    "Coles 0779 Belconnen",
    "COLES 0748 Macquarie",
    "BUNNINGS 475000 Majura",
    "BUNNINGS 436000 Belconnen",
    "Salary SAI GLOBAL PAYRO 006064",
    "Loan Repayment LN REPAY 695943637",
    "Direct Debit 000517 AMERICAN EXPRESS 376011940042008",
    "Direct Debit 000517 AMERICAN EXPRESS 377354019081005",
    "DESI HATTI STANHOPE GARD AUS Tap and Pay xx1788 Value Date: 02/01/2019",
    "STANHOPE FRUIT BARN STANHOPE GARD AUS Tap and Pay xx1788 Value Date: 02/01/2019",
    "COSTCO Fuel Majura Majura",
    "Costco Wholesale Aus Canberra Airp",
    "Wilson Parking Cans Barton",
    "ACT Gov Parking Fees Canberra",
    "IKEA Canberra Majura",
    "Target 5123 Belconnen",
    "Big W 0151 Woden",
    "Chemist Warehouse Belconnen",
    "Guzman Y Gomez Belconnen",
    "Subway Weston Weston",
    "McDonalds Majura Majura",
    "BEEM IT BEEM.COM.AU AU Card xx1361",
]

print("="*80)
print("MERCHANT NAME NORMALIZATION TEST")
print("="*80)
print()

results = {}
for description in test_cases:
    normalized = FireflyService.normalize_merchant_name(description)

    if normalized not in results:
        results[normalized] = []
    results[normalized].append(description)

print(f"Original: {len(test_cases)} descriptions")
print(f"Normalized: {len(results)} unique merchants")
print()

for normalized, originals in sorted(results.items()):
    print(f"✓ {normalized}")
    if len(originals) > 1:
        print(f"   (from {len(originals)} variations)")
    for orig in originals:
        print(f"   ← {orig}")
    print()
