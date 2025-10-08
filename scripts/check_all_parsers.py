#!/usr/bin/env python3
"""Check all bank parsers for potential summary section issues"""

import sys
sys.path.insert(0, 'data-importer')

import pdfplumber

test_files = [
    ('../home-expenses/uploads/AMEX-CashBack-71006/2024-09-16.pdf', 'amex'),
    ('../home-expenses/uploads/ING-Everyday-64015854/Orange Everyday (10).pdf', 'ing_orange'),
    ('../home-expenses/uploads/ING-Saver-45070850/Savings Maximiser (1).pdf', 'ing_savings'),
    ('../home-expenses/uploads/uBank-86400-Gagneet/SpendAccount-4257_2025-04.pdf', 'ubank'),
    ('../home-expenses/uploads/CBA-MasterCard-6233/Statement20210218.pdf', 'commbank'),
    ('../home-expenses/uploads/CBA-HomeLoan-466297723/Statement20201223 (1).pdf', 'commbank_homeloan'),
]

summary_keywords = [
    'Account Summary',
    'Transaction Summary',
    'Fees Summary',
    'Interest Summary',
    'Total debits',
    'Total credits',
    'Cashback Summary',
    'Page Total',
    'Statement Summary'
]

for pdf_path, bank_type in test_files:
    print(f'\n{"="*70}')
    print(f'Bank: {bank_type.upper()}')
    print(f'File: {pdf_path.split("/")[-1]}')
    print(f'{"="*70}')

    try:
        with pdfplumber.open(pdf_path) as pdf:
            found_summaries = []

            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    for keyword in summary_keywords:
                        if keyword in text:
                            found_summaries.append(f'Page {page_num}: "{keyword}"')

            if found_summaries:
                print('⚠️  Found summary sections:')
                for summary in found_summaries:
                    print(f'   - {summary}')
            else:
                print('✓ No obvious summary sections found')

    except Exception as e:
        print(f'✗ Error: {e}')
