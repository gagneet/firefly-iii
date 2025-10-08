#!/usr/bin/env python3
"""
Verify all required accounts exist in Firefly III

Quick script to check which accounts are already created
and which ones still need to be created.
"""

import sys
import os
from firefly_service import FireflyService


# Same account list as pre_create_accounts.py
REQUIRED_ACCOUNTS = [
    # Credit Cards
    'AMEX-BusinessPlatinum-43006',
    'AMEX-CashBack-71006',
    'CBA-MasterCard-6233',
    # Home Loans
    'CBA-HomeLoan-466297723',
    'CBA-HomeLoan-466297731',
    'CBA-HomeLoan-470379959',
    # Personal Loans
    'CBA-PL-466953719',
    # Everyday Savings
    'CBA-87Hoolihan-9331',
    'CBA-EveryDayOffset-7964',
    'ING-Everyday-64015854',
    'ING-Saver-45070850',
    'ING-Saver-817278720',
    'uBank-86400-Gagneet1',
    'uBank-86400-Gagneet2',
    'uBank-86400-Gagneet3',
    'uBank-86400-Gagneet4',
    'uBank-86400-Avneet1',
    'uBank-86400-Avneet2',
    # India Savings
    'India-ICICI-Bank',
    'India-SBI-Account1',
    'India-SBI-Account2',
    'India-ING-Account',
]


def verify_accounts(firefly_url: str, access_token: str) -> dict:
    """
    Verify which accounts exist in Firefly III

    Args:
        firefly_url: Base URL of Firefly III
        access_token: API access token

    Returns:
        Dictionary with verification results
    """
    print("=" * 80)
    print("FIREFLY III ACCOUNT VERIFICATION")
    print("=" * 80)
    print(f"\nFirefly URL: {firefly_url}")
    print(f"Checking {len(REQUIRED_ACCOUNTS)} required accounts...\n")

    # Initialize service
    service = FireflyService(firefly_url, access_token)

    # Test connection
    if not service.test_connection():
        print("\n❌ ERROR: Cannot connect to Firefly III")
        return {'success': False, 'error': 'Connection failed'}

    print("✓ Connection successful\n")

    results = {
        'total': len(REQUIRED_ACCOUNTS),
        'existing': [],
        'missing': [],
    }

    # Check each account
    print("Status  | Account Name")
    print("-" * 80)

    for account_name in sorted(REQUIRED_ACCOUNTS):
        # Try to find as asset first, then liability
        found = None
        for acc_type in ['asset', 'liability']:
            found = service.find_account_by_name(account_name, acc_type)
            if found:
                break

        if found:
            account_id = found['id']
            account_type = found['attributes']['type']
            print(f"✓ FOUND | {account_name} (ID: {account_id}, Type: {account_type})")
            results['existing'].append(account_name)
        else:
            print(f"✗ MISSING | {account_name}")
            results['missing'].append(account_name)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total required:    {results['total']}")
    print(f"Existing:          {len(results['existing'])}")
    print(f"Missing:           {len(results['missing'])}")

    if results['missing']:
        print("\n⚠️  Missing accounts:")
        for account in results['missing']:
            print(f"  - {account}")
        print("\nRun pre_create_accounts.py to create missing accounts")
        results['success'] = False
    else:
        print("\n✓ All required accounts exist!")
        results['success'] = True

    return results


def main():
    """Main entry point"""
    # Get configuration from args or environment
    if len(sys.argv) >= 3:
        firefly_url = sys.argv[1]
        access_token = sys.argv[2]
    else:
        firefly_url = os.environ.get('FIREFLY_URL')
        access_token = os.environ.get('FIREFLY_TOKEN')

        if not firefly_url or not access_token:
            print("Usage: python3 verify_accounts.py <firefly_url> <access_token>")
            print("\nOr set environment variables:")
            print("  export FIREFLY_URL=http://localhost:8080")
            print("  export FIREFLY_TOKEN=your_token_here")
            sys.exit(1)

    # Run verification
    result = verify_accounts(firefly_url, access_token)

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
