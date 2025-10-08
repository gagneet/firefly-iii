#!/usr/bin/env python3
"""
Pre-create all accounts before bulk statement upload

This script creates all accounts that will be referenced in bank statements,
ensuring that transfer transactions work correctly regardless of upload order.
"""

import sys
import os
from firefly_service import FireflyService
from typing import List, Tuple


# Account definitions: (name, type, liability_type)
# type: 'asset' or 'liability'
# liability_type: 'debt', 'loan', 'mortgage', or None
ACCOUNTS_TO_CREATE = [
    # Credit Cards (Liability - debt)
    ('AMEX-BusinessPlatinum-43006', 'liability', 'debt'),
    ('AMEX-CashBack-71006', 'liability', 'debt'),
    ('CBA-MasterCard-6233', 'liability', 'debt'),

    # Home Loans (Liability - mortgage)
    ('CBA-HomeLoan-466297723', 'liability', 'mortgage'),
    ('CBA-HomeLoan-466297731', 'liability', 'mortgage'),
    ('CBA-HomeLoan-470379959', 'liability', 'mortgage'),

    # Personal Loans (Liability - loan)
    ('CBA-PL-466953719', 'liability', 'loan'),

    # Everyday Savings / Transaction Accounts (Asset)
    ('CBA-87Hoolihan-9331', 'asset', None),
    ('CBA-EveryDayOffset-7964', 'asset', None),
    ('ING-Everyday-64015854', 'asset', None),
    ('ING-Saver-45070850', 'asset', None),
    ('ING-Saver-817278720', 'asset', None),
    ('uBank-86400-Gagneet1', 'asset', None),
    ('uBank-86400-Gagneet2', 'asset', None),
    ('uBank-86400-Gagneet3', 'asset', None),
    ('uBank-86400-Gagneet4', 'asset', None),
    ('uBank-86400-Avneet1', 'asset', None),
    ('uBank-86400-Avneet2', 'asset', None),

    # India Savings Accounts (Asset)
    ('India-ICICI-Bank', 'asset', None),
    ('India-SBI-Account1', 'asset', None),
    ('India-SBI-Account2', 'asset', None),
    ('India-ING-Account', 'asset', None),
]


def pre_create_accounts(firefly_url: str, access_token: str, accounts: List[Tuple[str, str, str]]) -> dict:
    """
    Pre-create all specified accounts in Firefly III

    Args:
        firefly_url: Base URL of Firefly III
        access_token: API access token
        accounts: List of (name, type, liability_type) tuples

    Returns:
        Dictionary with statistics
    """
    print("=" * 80)
    print("FIREFLY III ACCOUNT PRE-CREATION")
    print("=" * 80)
    print(f"\nFirefly URL: {firefly_url}")
    print(f"Total accounts to process: {len(accounts)}\n")

    # Initialize service
    service = FireflyService(firefly_url, access_token)

    # Test connection
    if not service.test_connection():
        print("\n❌ ERROR: Cannot connect to Firefly III")
        print("Please check:")
        print("  1. Firefly III URL is correct")
        print("  2. Firefly III is running")
        print("  3. Access token is valid")
        return {
            'success': False,
            'error': 'Connection failed'
        }

    print("✓ Connection successful\n")

    stats = {
        'total': len(accounts),
        'created': 0,
        'existing': 0,
        'failed': 0,
        'created_accounts': [],
        'existing_accounts': [],
        'failed_accounts': []
    }

    # Group accounts by type for better output
    accounts_by_type = {
        'Credit Cards': [],
        'Home Loans': [],
        'Personal Loans': [],
        'Everyday Savings': [],
        'India Savings': []
    }

    for name, acc_type, liability_type in accounts:
        if liability_type == 'debt':
            accounts_by_type['Credit Cards'].append((name, acc_type, liability_type))
        elif liability_type == 'mortgage':
            accounts_by_type['Home Loans'].append((name, acc_type, liability_type))
        elif liability_type == 'loan':
            accounts_by_type['Personal Loans'].append((name, acc_type, liability_type))
        elif 'India' in name:
            accounts_by_type['India Savings'].append((name, acc_type, liability_type))
        else:
            accounts_by_type['Everyday Savings'].append((name, acc_type, liability_type))

    # Process each account type group
    for group_name, group_accounts in accounts_by_type.items():
        if not group_accounts:
            continue

        print(f"\n{group_name} ({len(group_accounts)} accounts)")
        print("-" * 80)

        for account_name, account_type, liability_type in group_accounts:
            # Check if account already exists
            existing = service.find_account_by_name(account_name, account_type)

            if existing:
                account_id = existing['id']
                print(f"  ✓ EXISTS:  {account_name} (ID: {account_id})")
                stats['existing'] += 1
                stats['existing_accounts'].append(account_name)
            else:
                # Create the account
                type_tuple = (account_type, liability_type)
                result = service.create_account(account_name, type_tuple, 'AUD')

                if result:
                    account_id = result['id']
                    account_type_str = result['attributes']['type']
                    if liability_type:
                        account_type_str = f"{account_type_str} ({liability_type})"
                    print(f"  ✓ CREATED: {account_name} (ID: {account_id}, Type: {account_type_str})")
                    stats['created'] += 1
                    stats['created_accounts'].append(account_name)
                else:
                    print(f"  ✗ FAILED:  {account_name}")
                    stats['failed'] += 1
                    stats['failed_accounts'].append(account_name)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total accounts:    {stats['total']}")
    print(f"Created:           {stats['created']}")
    print(f"Already existed:   {stats['existing']}")
    print(f"Failed:            {stats['failed']}")

    if stats['failed'] > 0:
        print("\n⚠️  Failed accounts:")
        for account in stats['failed_accounts']:
            print(f"  - {account}")
        stats['success'] = False
    else:
        print("\n✓ All accounts ready for bulk import!")
        stats['success'] = True

    return stats


def main():
    """Main entry point"""
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python3 pre_create_accounts.py <firefly_url> <access_token>")
        print("\nExample:")
        print("  python3 pre_create_accounts.py http://localhost:8080 eyJ0eXAiOiJKV1QiLCJh...")
        print("\nYou can also set environment variables:")
        print("  export FIREFLY_URL=http://localhost:8080")
        print("  export FIREFLY_TOKEN=eyJ0eXAiOiJKV1QiLCJh...")
        print("  python3 pre_create_accounts.py")
        sys.exit(1)

    # Get configuration from args or environment
    if len(sys.argv) >= 3:
        firefly_url = sys.argv[1]
        access_token = sys.argv[2]
    else:
        firefly_url = os.environ.get('FIREFLY_URL')
        access_token = os.environ.get('FIREFLY_TOKEN')

        if not firefly_url or not access_token:
            print("ERROR: Please provide firefly_url and access_token")
            sys.exit(1)

    # Run account creation
    result = pre_create_accounts(firefly_url, access_token, ACCOUNTS_TO_CREATE)

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
