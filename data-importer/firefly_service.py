#!/usr/bin/env python3
"""
Firefly III Service
Handles interaction with Firefly III API for creating transactions and accounts
"""

import requests
import json
import sys
from typing import List, Dict, Optional
from statement_parser import Transaction, StatementParser
from duplicate_detector import DuplicateDetector


class FireflyService:
    """Service to interact with Firefly III API"""

    def __init__(self, firefly_url: str, access_token: str):
        """
        Initialize Firefly III service

        Args:
            firefly_url: Base URL of Firefly III installation
            access_token: Personal Access Token for API authentication
        """
        self.firefly_url = firefly_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        # Cache for account lookups to reduce API calls
        self._account_cache = {}  # name -> account_id
        self._account_list_cache = {}  # account_type -> list of accounts

    def test_connection(self) -> bool:
        """Test connection to Firefly III API"""
        try:
            response = requests.get(
                f'{self.firefly_url}/api/v1/about',
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def get_accounts(self, account_type: str = 'asset') -> List[Dict]:
        """
        Get all accounts of a specific type (with caching)

        Args:
            account_type: Type of account (asset, expense, revenue, etc.)

        Returns:
            List of account dictionaries
        """
        # Check cache first
        if account_type in self._account_list_cache:
            return self._account_list_cache[account_type]

        try:
            response = requests.get(
                f'{self.firefly_url}/api/v1/accounts',
                headers=self.headers,
                params={'type': account_type},
                timeout=10
            )

            if response.status_code == 200:
                accounts = response.json().get('data', [])
                # Cache the result
                self._account_list_cache[account_type] = accounts
                return accounts
            else:
                print(f"Error fetching accounts: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def find_account_by_name(self, account_name: str, account_type: str = 'asset') -> Optional[Dict]:
        """Find account by name"""
        accounts = self.get_accounts(account_type)

        for account in accounts:
            if account['attributes']['name'].lower() == account_name.lower():
                return account

        return None

    def create_account(self, account_name: str, account_type: str = 'asset', currency_code: str = 'AUD') -> Optional[Dict]:
        """
        Create a new account in Firefly III

        Args:
            account_name: Name of the account
            account_type: Type (asset, expense, revenue)
            currency_code: Currency code (default AUD)

        Returns:
            Created account dict or None
        """
        payload = {
            'name': account_name,
            'type': account_type,
            'currency_code': currency_code,
            'active': True,
            'account_role': 'defaultAsset' if account_type == 'asset' else None  # Required for asset accounts
        }

        try:
            response = requests.post(
                f'{self.firefly_url}/api/v1/accounts',
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('data')
            else:
                print(f"Error creating account: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_or_create_account(self, account_name: str, account_type: str = 'asset') -> Optional[str]:
        """
        Get account ID by name, create if doesn't exist

        Returns:
            Account ID or None
        """
        # Try to find existing account
        account = self.find_account_by_name(account_name, account_type)

        if account:
            return account['id']

        # Create new account
        account = self.create_account(account_name, account_type)

        if account:
            return account['id']

        return None

    def create_transaction(self, transaction: Transaction, source_account: str, destination_account: str) -> Optional[Dict]:
        """
        Create a transaction in Firefly III

        Args:
            transaction: Transaction object
            source_account: Source account name
            destination_account: Destination account name

        Returns:
            Created transaction dict or None
        """
        # Determine transaction type
        if transaction.amount < 0:
            # Withdrawal (expense)
            transaction_type = 'withdrawal'
            amount = abs(transaction.amount)
        else:
            # Deposit (income)
            transaction_type = 'deposit'
            amount = transaction.amount

        payload = {
            'error_if_duplicate_hash': True,
            'apply_rules': True,
            'transactions': [{
                'type': transaction_type,
                'date': transaction.date,
                'amount': str(amount),
                'description': transaction.description,
                'source_name': source_account,
                'destination_name': destination_account,
                'currency_id': None,
                'currency_code': 'AUD',
                'category_name': transaction.category if transaction.category else None,
                'tags': [transaction.account, transaction.transaction_type] if transaction.transaction_type else [transaction.account],
                'notes': f"Imported from {transaction.account}",
                'external_id': transaction.transaction_id
            }]
        }

        try:
            response = requests.post(
                f'{self.firefly_url}/api/v1/transactions',
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('data')
            elif response.status_code == 422:
                # Could be duplicate or validation error
                error_data = response.json()
                if 'duplicate' in str(error_data).lower():
                    return {'status': 'duplicate'}
                else:
                    print(f"Validation error for transaction '{transaction.description[:40]}': {response.text}")
                    return None
            else:
                print(f"Error creating transaction '{transaction.description[:40]}': {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def create_transfer(self, transaction1: Transaction, transaction2: Transaction) -> Optional[Dict]:
        """
        Create a transfer transaction between two accounts

        Args:
            transaction1: Source transaction (negative amount)
            transaction2: Destination transaction (positive amount)

        Returns:
            Created transaction dict or None
        """
        # Determine source and destination
        if transaction1.amount < 0:
            source = transaction1.account
            destination = transaction2.account
            amount = abs(transaction1.amount)
            description = transaction1.description
        else:
            source = transaction2.account
            destination = transaction1.account
            amount = abs(transaction2.amount)
            description = transaction2.description

        payload = {
            'error_if_duplicate_hash': True,
            'apply_rules': True,
            'transactions': [{
                'type': 'transfer',
                'date': transaction1.date,
                'amount': str(amount),
                'description': description,
                'source_name': source,
                'destination_name': destination,
                'currency_id': None,
                'currency_code': 'AUD',
                'tags': ['transfer', 'auto-imported'],
                'notes': f"Transfer from {source} to {destination}",
                'external_id': transaction1.transaction_id
            }]
        }

        try:
            response = requests.post(
                f'{self.firefly_url}/api/v1/transactions',
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 422]:
                if response.status_code == 422:
                    return {'status': 'duplicate'}
                return response.json().get('data')
            else:
                print(f"Error creating transfer: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def import_transactions(
        self,
        transactions: List[Transaction],
        detect_duplicates: bool = True,
        detect_transfers: bool = True
    ) -> Dict:
        """
        Import transactions to Firefly III with duplicate and transfer detection

        Args:
            transactions: List of transactions to import
            detect_duplicates: Remove duplicate transactions
            detect_transfers: Detect and create transfers

        Returns:
            Import result statistics
        """
        stats = {
            'total': len(transactions),
            'created': 0,
            'duplicates': 0,
            'transfers': 0,
            'errors': 0,
            'accounts_created': []
        }

        # Detect duplicates and transfers
        if detect_duplicates or detect_transfers:
            detector = DuplicateDetector()
            result = detector.categorize_duplicates(transactions)

            stats['duplicates_removed'] = result['stats']['exact_duplicates_removed']
            stats['transfers_found'] = result['stats']['transfers_found']

            # Import transfers
            if detect_transfers:
                for txn1, txn2 in result['transfers']:
                    transfer_result = self.create_transfer(txn1, txn2)
                    if transfer_result:
                        if transfer_result.get('status') == 'duplicate':
                            stats['duplicates'] += 1
                        else:
                            stats['transfers'] += 1
                    else:
                        stats['errors'] += 1

            # Import unique transactions
            transactions_to_import = result['unique']
        else:
            transactions_to_import = transactions

        # Ensure all accounts exist
        accounts_needed = set(txn.account for txn in transactions_to_import)
        for account_name in accounts_needed:
            account_id = self.get_or_create_account(account_name, 'asset')
            if account_id and account_name not in stats['accounts_created']:
                stats['accounts_created'].append(account_name)

        # Import transactions
        for txn in transactions_to_import:
            # Skip zero-amount transactions (like fee waivers)
            if abs(txn.amount) < 0.01:
                print(f"Skipping zero-amount transaction: {txn.description}")
                continue

            if txn.amount < 0:
                # Expense: source = user account, destination = merchant/expense
                source_account = txn.account
                destination_account = txn.description[:50]  # Use description as expense account
            else:
                # Income: source = payer/revenue, destination = user account
                source_account = txn.description[:50]  # Use description as revenue source
                destination_account = txn.account

            result = self.create_transaction(txn, source_account, destination_account)

            if result:
                if result.get('status') == 'duplicate':
                    stats['duplicates'] += 1
                else:
                    stats['created'] += 1
            else:
                stats['errors'] += 1

        return stats


def process_pdf_and_import(
    pdf_path: str,
    bank_type: str,
    firefly_url: str,
    access_token: str,
    detect_duplicates: bool = True,
    detect_transfers: bool = True
) -> Dict:
    """
    Process a PDF statement and import to Firefly III

    Args:
        pdf_path: Path to PDF file
        bank_type: Bank type (amex, ing_orange, etc.)
        firefly_url: Firefly III URL
        access_token: API access token
        detect_duplicates: Whether to detect and skip duplicates
        detect_transfers: Whether to detect transfers between accounts

    Returns:
        Import statistics
    """
    # Parse PDF
    parser = StatementParser()
    transactions = parser.parse_statement(pdf_path, bank_type)

    if not transactions:
        return {'error': 'No transactions found in PDF'}

    # Auto-categorize
    for txn in transactions:
        if not txn.category:
            txn.category = parser.categorize_transaction(txn)

    # Import to Firefly III
    service = FireflyService(firefly_url, access_token)

    if not service.test_connection():
        return {'error': 'Cannot connect to Firefly III API'}

    return service.import_transactions(transactions, detect_duplicates, detect_transfers)


if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) < 5:
        print("Usage: python firefly_service.py <bank_type> <pdf_file> <firefly_url> <access_token> [detect_duplicates] [detect_transfers]")
        sys.exit(1)

    bank_type = sys.argv[1]
    pdf_file = sys.argv[2]
    firefly_url = sys.argv[3]
    access_token = sys.argv[4]
    detect_duplicates = sys.argv[5] == '1' if len(sys.argv) > 5 else True
    detect_transfers = sys.argv[6] == '1' if len(sys.argv) > 6 else True

    print(f"Processing {bank_type} statement: {pdf_file}")
    print(f"Detect duplicates: {detect_duplicates}")
    print(f"Detect transfers: {detect_transfers}")

    result = process_pdf_and_import(pdf_file, bank_type, firefly_url, access_token, detect_duplicates, detect_transfers)

    print("\n" + "="*60)
    print("IMPORT RESULTS")
    print("="*60)
    for key, value in result.items():
        print(f"{key:20}: {value}")
