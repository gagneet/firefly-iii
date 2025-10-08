#!/usr/bin/env python3
"""
Check which transaction was marked as duplicate in Statement20210524.pdf
"""
import sys
sys.path.insert(0, '/home/gagneet/firefly/data-importer')

from statement_parser import StatementParser
from firefly_service import FireflyService
import os

# Parse the PDF
pdf = '/home/gagneet/home-expenses/uploads/CBA-MasterCard-6233/Statement20210524.pdf'
parser = StatementParser()
transactions = parser.parse_statement(pdf, 'commbank')

print(f'Total transactions in PDF: {len(transactions)}')
print('\nAll transactions:')
for i, txn in enumerate(transactions, 1):
    print(f'{i:2d}. {txn.date} | ${txn.amount:>10.2f} | {txn.description[:70]}')

# Get token and check database
token_file = os.path.expanduser('~/.firefly_token')
if os.path.exists(token_file):
    with open(token_file) as f:
        token = f.read().strip()

    print('\n' + '='*100)
    print('Checking which transactions already exist in Firefly III...')
    print('='*100)

    service = FireflyService('https://firefly.gagneet.com', token)

    # Check each transaction
    found_in_db = []
    for i, txn in enumerate(transactions, 1):
        # Try to find this exact transaction
        response = service.session.get(
            f'{service.firefly_url}/api/v1/transactions',
            params={
                'start': txn.date,
                'end': txn.date,
            }
        )

        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', []):
                for journal in item.get('attributes', {}).get('transactions', []):
                    # Check if amount matches
                    api_amount = float(journal.get('amount', 0))
                    if abs(abs(api_amount) - abs(txn.amount)) < 0.01:
                        # Check if description matches
                        api_desc = journal.get('description', '')
                        if api_desc[:50] == txn.description[:50]:
                            found_in_db.append((i, txn, api_desc))
                            print(f'\n✓ FOUND IN DB: Transaction #{i}')
                            print(f'  Date: {txn.date}')
                            print(f'  Amount: ${txn.amount:.2f}')
                            print(f'  Description: {txn.description}')
                            break

    print(f'\n\nSummary:')
    print(f'Total in PDF: {len(transactions)}')
    print(f'Found in DB: {len(found_in_db)}')
    print(f'New transactions: {len(transactions) - len(found_in_db)}')
