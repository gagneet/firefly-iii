#!/usr/bin/env python3
"""Check what types of accounts were created"""
import requests
import sys

# Get token from user or environment
token = input("Enter your Firefly III Personal Access Token: ").strip()

headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

# Get all accounts (paginated)
all_accounts = []
page = 1

while True:
    response = requests.get(f'https://firefly.gagneet.com/api/v1/accounts?page={page}&limit=100', headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        sys.exit(1)

    data = response.json()
    accounts = data['data']

    if not accounts:
        break

    all_accounts.extend(accounts)
    page += 1

    if page > 100:  # Safety limit
        break

# Analyze accounts
asset_accounts = []
expense_accounts = []
revenue_accounts = []
liability_accounts = []
other_accounts = []

for account in all_accounts:
    attrs = account['attributes']
    name = attrs['name']
    acc_type = attrs['type']

    if acc_type == 'asset':
        asset_accounts.append(name)
    elif acc_type == 'expense':
        expense_accounts.append(name)
    elif acc_type == 'revenue':
        revenue_accounts.append(name)
    elif acc_type in ['liabilities', 'liability', 'debt', 'loan', 'mortgage']:
        liability_accounts.append(name)
    else:
        other_accounts.append((name, acc_type))

print(f'\n{"="*80}')
print('ACCOUNT TYPE SUMMARY')
print(f'{"="*80}\n')

print(f'Total accounts: {len(all_accounts)}')
print(f'  Asset accounts: {len(asset_accounts)}')
print(f'  Expense accounts: {len(expense_accounts)}')
print(f'  Revenue accounts: {len(revenue_accounts)}')
print(f'  Liability accounts: {len(liability_accounts)}')
print(f'  Other: {len(other_accounts)}')

# Show sample asset accounts (should be bank accounts)
print(f'\n{"="*80}')
print('ASSET ACCOUNTS (first 20 - should be YOUR bank accounts):')
print(f'{"="*80}\n')
for name in asset_accounts[:20]:
    print(f'  - {name}')

# Show sample expense accounts (should be merchants/vendors)
print(f'\n{"="*80}')
print('EXPENSE ACCOUNTS (first 20 - should be merchants/vendors):')
print(f'{"="*80}\n')
for name in expense_accounts[:20]:
    print(f'  - {name}')

# Show sample revenue accounts (should be income sources)
print(f'\n{"="*80}')
print('REVENUE ACCOUNTS (first 20 - should be income sources):')
print(f'{"="*80}\n')
for name in revenue_accounts[:20]:
    print(f'  - {name}')

# Check for suspicious patterns
suspicious_assets = [name for name in asset_accounts if any(
    keyword in name.upper() for keyword in [
        'WOOLWORTHS', 'COLES', 'ALDI', 'BUNNINGS', 'MCDONALD',
        'CAFE', 'RESTAURANT', 'SHOP', 'STORE', 'PTY', 'LTD'
    ]
)]

if suspicious_assets:
    print(f'\n{"="*80}')
    print(f'⚠ SUSPICIOUS: {len(suspicious_assets)} asset accounts that look like merchants:')
    print(f'{"="*80}\n')
    for name in suspicious_assets[:30]:
        print(f'  - {name}')
