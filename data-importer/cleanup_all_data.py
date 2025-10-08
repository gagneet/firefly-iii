#!/usr/bin/env python3
"""
Clean up all transactions and expense/revenue accounts from Firefly III
Keeps asset and liability accounts intact
"""
import requests
import sys
import time
from pathlib import Path

def get_token():
    """Get Firefly III access token"""
    token_file = Path.home() / '.firefly_token'
    if token_file.exists():
        return token_file.read_text().strip()

    token = input("Enter your Firefly III Personal Access Token: ").strip()
    return token

def main():
    print("="*80)
    print("FIREFLY III DATA CLEANUP")
    print("="*80)
    print()
    print("⚠️  WARNING: This will DELETE:")
    print("   - ALL transactions")
    print("   - ALL expense accounts")
    print("   - ALL revenue accounts")
    print()
    print("✓  This will KEEP:")
    print("   - Asset accounts (your bank accounts)")
    print("   - Liability accounts (credit cards, loans)")
    print()

    confirm = input("Type 'DELETE ALL' to confirm: ").strip()
    if confirm != 'DELETE ALL':
        print("Cancelled.")
        sys.exit(0)

    token = get_token()
    firefly_url = 'https://firefly.gagneet.com'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    # Test connection
    print("\nTesting connection...")
    response = requests.get(f'{firefly_url}/api/v1/about', headers=headers)
    if response.status_code != 200:
        print(f"ERROR: Cannot connect to Firefly III (status {response.status_code})")
        sys.exit(1)
    print("✓ Connected\n")

    # Step 1: Delete all transactions
    print("="*80)
    print("STEP 1: Deleting all transactions")
    print("="*80)

    deleted_transactions = 0
    page = 1

    while True:
        print(f"\nFetching transactions page {page}...", end=' ')
        response = requests.get(
            f'{firefly_url}/api/v1/transactions',
            headers=headers,
            params={'page': page, 'limit': 50}
        )

        if response.status_code != 200:
            print(f"ERROR: {response.status_code}")
            break

        data = response.json()
        transactions = data.get('data', [])

        if not transactions:
            print("(no more transactions)")
            break

        print(f"found {len(transactions)}")

        for transaction in transactions:
            txn_id = transaction['id']

            # Delete transaction
            del_response = requests.delete(
                f'{firefly_url}/api/v1/transactions/{txn_id}',
                headers=headers
            )

            if del_response.status_code == 204:
                deleted_transactions += 1
                print(f"  ✓ Deleted transaction {txn_id}")
            else:
                print(f"  ✗ Failed to delete transaction {txn_id}: {del_response.status_code}")

            # Rate limiting
            time.sleep(0.1)

        # Don't increment page - we're deleting from page 1 each time
        # page += 1

        if page > 1000:  # Safety limit
            print("Safety limit reached!")
            break

    print(f"\n✓ Deleted {deleted_transactions} transactions\n")

    # Step 2: Delete expense accounts
    print("="*80)
    print("STEP 2: Deleting expense accounts")
    print("="*80)

    deleted_expense = 0
    page = 1

    while True:
        print(f"\nFetching expense accounts page {page}...", end=' ')
        response = requests.get(
            f'{firefly_url}/api/v1/accounts',
            headers=headers,
            params={'page': page, 'limit': 50, 'type': 'expense'}
        )

        if response.status_code != 200:
            print(f"ERROR: {response.status_code}")
            break

        data = response.json()
        accounts = data.get('data', [])

        if not accounts:
            print("(no more expense accounts)")
            break

        print(f"found {len(accounts)}")

        for account in accounts:
            acc_id = account['id']
            acc_name = account['attributes']['name']

            # Delete account
            del_response = requests.delete(
                f'{firefly_url}/api/v1/accounts/{acc_id}',
                headers=headers
            )

            if del_response.status_code == 204:
                deleted_expense += 1
                print(f"  ✓ Deleted expense account: {acc_name}")
            else:
                print(f"  ✗ Failed to delete {acc_name}: {del_response.status_code}")

            time.sleep(0.1)

        # Don't increment page
        # page += 1

        if page > 100:
            print("Safety limit reached!")
            break

    print(f"\n✓ Deleted {deleted_expense} expense accounts\n")

    # Step 3: Delete revenue accounts
    print("="*80)
    print("STEP 3: Deleting revenue accounts")
    print("="*80)

    deleted_revenue = 0
    page = 1

    while True:
        print(f"\nFetching revenue accounts page {page}...", end=' ')
        response = requests.get(
            f'{firefly_url}/api/v1/accounts',
            headers=headers,
            params={'page': page, 'limit': 50, 'type': 'revenue'}
        )

        if response.status_code != 200:
            print(f"ERROR: {response.status_code}")
            break

        data = response.json()
        accounts = data.get('data', [])

        if not accounts:
            print("(no more revenue accounts)")
            break

        print(f"found {len(accounts)}")

        for account in accounts:
            acc_id = account['id']
            acc_name = account['attributes']['name']

            # Delete account
            del_response = requests.delete(
                f'{firefly_url}/api/v1/accounts/{acc_id}',
                headers=headers
            )

            if del_response.status_code == 204:
                deleted_revenue += 1
                print(f"  ✓ Deleted revenue account: {acc_name}")
            else:
                print(f"  ✗ Failed to delete {acc_name}: {del_response.status_code}")

            time.sleep(0.1)

        # Don't increment page
        # page += 1

        if page > 100:
            print("Safety limit reached!")
            break

    print(f"\n✓ Deleted {deleted_revenue} revenue accounts\n")

    # Summary
    print("="*80)
    print("CLEANUP COMPLETE")
    print("="*80)
    print(f"Deleted:")
    print(f"  - {deleted_transactions} transactions")
    print(f"  - {deleted_expense} expense accounts")
    print(f"  - {deleted_revenue} revenue accounts")
    print()
    print("Your asset and liability accounts are intact.")
    print("You can now re-import your statements with the fixed code.")
    print("="*80)

if __name__ == '__main__':
    main()
