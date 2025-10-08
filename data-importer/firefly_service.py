#!/usr/bin/env python3
"""
Firefly III Service
Handles interaction with Firefly III API for creating transactions and accounts
"""

import requests
import json
import sys
import logging
import re
from typing import List, Dict, Optional
from statement_parser import Transaction, StatementParser
from duplicate_detector import DuplicateDetector


class FireflyService:
    """Service to interact with Firefly III API"""

    @staticmethod
    def normalize_merchant_name(description: str) -> str:
        """
        Normalize merchant/payee names to avoid creating duplicate expense/revenue accounts.

        Examples:
            "WOOLWORTHS 1234 BELCONNEN" -> "Woolworths"
            "Salary SAI GLOBAL PAYRO 006064" -> "Salary"
            "Direct Debit 000517 AMERICAN EXPRESS 376011940042008" -> "American Express"
        """
        # Remove common prefixes/suffixes
        desc = description.strip()

        # Remove card numbers and value dates
        desc = re.sub(r'\bCard\s+xx\d+\b', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'\bTap and Pay\s+xx\d+\b', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'\bValue Date:.*$', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'\bxx\d+\b', '', desc)

        # Remove location codes and numbers after merchant name
        desc = re.sub(r'\b\d{4,}\b', '', desc)  # Remove 4+ digit numbers (branch codes, etc)
        desc = re.sub(r'\s+\d{1,3}\s+', ' ', desc)  # Remove small numbers between words

        # Remove country codes
        desc = re.sub(r'\b(AUS|AU|AUSTRALIA)\b', '', desc, flags=re.IGNORECASE)

        # Remove common transaction prefixes (but keep the rest)
        desc = re.sub(r'^(Direct Debit|BPAY|Transfer from|Transfer to|Payment to|Payment from|Deposit from)\s+\d+\s+', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'^(DD|BP|TRF|PMT)\s+\d+\s+', '', desc, flags=re.IGNORECASE)

        # Clean up multiple spaces
        desc = re.sub(r'\s+', ' ', desc).strip()

        # Check against known patterns first (using search instead of match to find anywhere in string)
        desc_upper = desc.upper()

        # Specific patterns - check these first (order matters!)
        # Map AMEX card numbers to specific accounts
        if re.search(r'376011940042008', desc_upper):
            return 'AMEX-BusinessPlatinum-43006'
        if re.search(r'377354019081005', desc_upper):
            return 'AMEX-CashBack-71006'
        if re.search(r'43006', desc_upper):  # Last 5 digits
            return 'AMEX-BusinessPlatinum-43006'
        if re.search(r'71006', desc_upper):  # Last 5 digits
            return 'AMEX-CashBack-71006'

        # Map generic AMEX to Business Platinum as default
        if re.search(r'AMERICAN\s+EXPRESS', desc_upper) or re.search(r'AMEX', desc_upper):
            return 'AMEX-BusinessPlatinum-43006'  # Default to Business Platinum

        specific_patterns = [
            (r'COSTCO\s+FUEL', 'Costco Fuel'),
            (r'COSTCO', 'Costco'),
            (r'WOOLWORTHS', 'Woolworths'),
            (r'COLES', 'Coles'),
            (r'BUNNINGS', 'Bunnings'),
            (r'IKEA', 'IKEA'),
            (r'ALDI', 'Aldi'),
            (r'IGA\b', 'IGA'),
            (r'KMART', 'Kmart'),
            (r'TARGET', 'Target'),
            (r'BIG\s*W', 'Big W'),
            (r'SPOTLIGHT', 'Spotlight'),
            (r'LINCRAFT', 'Lincraft'),
            (r'MCDONALD', 'McDonalds'),
            (r'KFC', 'KFC'),
            (r'SUBWAY', 'Subway'),
            (r'GUZMAN', 'Guzman Y Gomez'),
            (r'CHEMIST\s+WAREHOUSE', 'Chemist Warehouse'),
            (r'WILSON\s+PARKING', 'Wilson Parking'),
            (r'BEEM\s*IT', 'Beem It'),
            (r'CALTEX', 'Caltex'),
            (r'SHELL', 'Shell'),
            (r'\bBP\b', 'BP'),
            (r'ACT\s+GOV.*PARKING', 'ACT Government Parking'),
            (r'ACT\s+GOV', 'ACT Government'),
        ]

        for pattern, normalized_name in specific_patterns:
            if re.search(pattern, desc_upper):
                return normalized_name

        # Income patterns (must match from start)
        if re.match(r'SAI\s+GLOBAL', desc_upper) or re.match(r'SALARY', desc_upper):
            return 'Salary'

        # Map loan repayment numbers to specific loan accounts
        if re.search(r'695943637', desc_upper):
            return 'CBA-HomeLoan-466297723'  # Map based on loan number
        if re.search(r'LOAN\s+REPAYMENT|LN\s+REPAY', desc_upper):
            # Generic loan repayment - default to first home loan
            return 'CBA-HomeLoan-466297723'

        # If no pattern matched, extract first 1-3 words (likely the merchant name)
        words = desc.split()
        if len(words) >= 3:
            # Take first 3 words, remove common suffixes
            name = ' '.join(words[:3])
        elif len(words) >= 2:
            name = ' '.join(words[:2])
        else:
            name = desc

        # Remove PTY LTD and similar
        name = re.sub(r'\b(PTY|LTD|CO|INC|LLC)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+', ' ', name).strip()

        # Capitalize properly
        name = name.title()

        return name if name else description[:50]

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

    @staticmethod
    def detect_account_type(account_name: str) -> tuple:
        """
        Detect the appropriate Firefly III account type based on account name

        Args:
            account_name: Name of the account

        Returns:
            Tuple of (type, liability_type) for API
        """
        account_lower = account_name.lower()

        # Credit cards (check first to avoid catching 'cashback' as savings)
        if any(keyword in account_lower for keyword in [
            'amex', 'american express', 'mastercard', 'visa',
            'credit card', 'diamond', 'platinum', 'cashback'
        ]):
            return ('liability', 'debt')

        # Mortgages / Home Loans (check before general 'loan')
        if any(keyword in account_lower for keyword in [
            'home loan', 'homeloan', 'home-loan', 'mortgage'
        ]):
            return ('liability', 'mortgage')

        # Personal Loans (check for specific patterns)
        if any(keyword in account_lower for keyword in [
            'personal loan', 'car loan', '-pl-', 'loan'
        ]):
            return ('liability', 'loan')

        # Default to asset account (bank accounts, savings, etc.)
        return ('asset', None)

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

    def create_account(self, account_name: str, account_type: tuple = None, currency_code: str = 'AUD') -> Optional[Dict]:
        """
        Create a new account in Firefly III

        Args:
            account_name: Name of the account
            account_type: Tuple of (type, liability_type) or None to auto-detect
            currency_code: Currency code (default AUD)

        Returns:
            Created account dict or None
        """
        # Auto-detect if not provided
        if account_type is None:
            account_type = self.detect_account_type(account_name)

        type_str, liability_type = account_type

        payload = {
            'name': account_name,
            'type': type_str,
            'currency_code': currency_code,
            'active': True,
        }

        # Add account_role for asset accounts
        if type_str == 'asset':
            payload['account_role'] = 'defaultAsset'

        # For liability accounts, add liability-specific fields
        if type_str == 'liability':
            payload['liability_type'] = liability_type
            payload['liability_direction'] = 'credit'  # Credit cards/loans are credits (you owe)
            payload['opening_balance'] = '0'
            payload['opening_balance_date'] = '2020-01-01'

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

    def get_or_create_account(self, account_name: str, account_type: tuple = None) -> Optional[str]:
        """
        Get account ID by name, create if doesn't exist
        If account_type is None, auto-detect based on account name

        Returns:
            Account ID or None
        """
        # Auto-detect account type if not provided
        if account_type is None:
            account_type = self.detect_account_type(account_name)
            type_str, liability_type = account_type
            liability_str = f" ({liability_type})" if liability_type else ""
            print(f"Auto-detected account type for '{account_name}': {type_str}{liability_str}")

        type_str, liability_type = account_type

        # Try to find existing account - search across common type names
        # Map to database type names for searching
        if type_str == 'liability':
            if liability_type == 'debt':
                search_types = ['Credit card', 'Liability credit account']
            elif liability_type == 'mortgage':
                search_types = ['Mortgage']
            elif liability_type == 'loan':
                search_types = ['Loan']
            else:
                search_types = []
        else:
            search_types = ['Asset account']

        for search_type in search_types:
            account = self.find_account_by_name(account_name, search_type)
            if account:
                print(f"Found existing account: {account_name} (ID: {account['id']})")
                return account['id']

        # Create new account with detected type
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
        # Detect account type to determine transaction type correctly
        source_type, _ = self.detect_account_type(source_account)
        dest_type, _ = self.detect_account_type(destination_account)

        # Determine transaction type based on account types and amount
        # For liability accounts, positive amounts are payments (withdrawals)
        is_liability_account = source_type == 'liability' or dest_type == 'liability'

        if is_liability_account:
            # For liability accounts:
            # - If source is liability (positive amount) = withdrawal (payment)
            # - If dest is liability (negative amount) = deposit (purchase)
            if transaction.amount > 0:
                transaction_type = 'withdrawal'
                amount = transaction.amount
            else:
                transaction_type = 'deposit'
                amount = abs(transaction.amount)
        else:
            # For asset accounts (normal logic):
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
            'accounts_created': [],
            'skipped': 0  # Track skipped transactions
        }

        # Detect duplicates and transfers
        if detect_duplicates or detect_transfers:
            detector = DuplicateDetector()
            result = detector.categorize_duplicates(transactions)

            # Count pre-filtered duplicates as part of total duplicates
            pre_filtered_duplicates = result['stats']['exact_duplicates_removed']
            stats['duplicates'] = pre_filtered_duplicates
            stats['duplicates_removed'] = pre_filtered_duplicates
            stats['transfers_found'] = result['stats']['transfers_found']

            # Pre-create all accounts that appear in transfers to avoid creation failures
            if detect_transfers and len(result['transfers']) > 0:
                transfer_accounts = set()
                for txn1, txn2 in result['transfers']:
                    transfer_accounts.add(txn1.account)
                    transfer_accounts.add(txn2.account)

                if transfer_accounts:
                    print(f"\n[ACCOUNT PRE-CREATION] Found {len(transfer_accounts)} unique accounts in transfers")
                    for account_name in sorted(transfer_accounts):
                        # Check if already created for unique transactions
                        if account_name not in stats['accounts_created']:
                            account_id = self.get_or_create_account(account_name)
                            if account_id:
                                stats['accounts_created'].append(account_name)
                                print(f"  ✓ Pre-created account: {account_name}")
                            else:
                                print(f"  ✗ Failed to create account: {account_name}")
                                logging.error(f"Failed to pre-create transfer account: {account_name}")

            # Import transfers
            if detect_transfers:
                for txn1, txn2 in result['transfers']:
                    transfer_result = self.create_transfer(txn1, txn2)
                    if transfer_result:
                        if transfer_result.get('status') == 'duplicate':
                            stats['duplicates'] += 1
                            # Log duplicate transfer
                            print(f"  [DUPLICATE TRANSFER] {txn1.date} | ${abs(txn1.amount):>9.2f} | {txn1.account} → {txn2.account}")
                            logging.warning(f"DUPLICATE transfer detected: Date={txn1.date}, Amount=${abs(txn1.amount):.2f}, From={txn1.account}, To={txn2.account}, Desc='{txn1.description}'")
                        else:
                            stats['transfers'] += 1
                            # Log successful transfer
                            print(f"  [TRANSFER] {txn1.date} | ${abs(txn1.amount):>9.2f} | {txn1.account} → {txn2.account}")
                            logging.info(f"TRANSFER created: Date={txn1.date}, Amount=${abs(txn1.amount):.2f}, From={txn1.account}, To={txn2.account}")
                    else:
                        stats['errors'] += 1
                        # Log transfer error
                        print(f"  [ERROR TRANSFER] Failed: {txn1.date} | ${abs(txn1.amount):>9.2f} | {txn1.account} → {txn2.account}")
                        logging.error(f"ERROR creating transfer: Date={txn1.date}, Amount=${abs(txn1.amount):.2f}, From={txn1.account}, To={txn2.account}, Desc='{txn1.description}'")

            # Import unique transactions
            transactions_to_import = result['unique']
        else:
            transactions_to_import = transactions

        # Ensure all accounts exist (auto-detect account type)
        accounts_needed = set(txn.account for txn in transactions_to_import)
        for account_name in accounts_needed:
            account_id = self.get_or_create_account(account_name)  # Auto-detect type
            if account_id and account_name not in stats['accounts_created']:
                stats['accounts_created'].append(account_name)

        # Import transactions
        for txn in transactions_to_import:
            # Skip zero-amount transactions (like fee waivers)
            if abs(txn.amount) < 0.01:
                print(f"Skipping zero-amount transaction: {txn.description}")
                stats['skipped'] += 1
                continue

            # Normalize merchant/payee name to avoid creating duplicate expense/revenue accounts
            normalized_merchant = self.normalize_merchant_name(txn.description)

            # Detect if this is a liability account (credit card, loan, mortgage)
            account_type, _ = self.detect_account_type(txn.account)
            is_liability = account_type == 'liability'

            if is_liability:
                # For liability accounts, the logic is INVERTED:
                # - Positive amount (credit/payment) = withdrawal (reduces debt)
                # - Negative amount (debit/purchase) = deposit (increases debt)
                if txn.amount > 0:
                    # Payment/Credit: Withdrawal from liability account
                    source_account = txn.account
                    destination_account = normalized_merchant
                else:
                    # Purchase/Debit: Deposit to liability account
                    source_account = normalized_merchant
                    destination_account = txn.account
            else:
                # For asset accounts, normal logic:
                if txn.amount < 0:
                    # Expense: source = user account, destination = merchant/expense
                    source_account = txn.account
                    destination_account = normalized_merchant  # Expense account (auto-created by Firefly)
                else:
                    # Income: source = payer/revenue, destination = user account
                    source_account = normalized_merchant  # Revenue account (auto-created by Firefly)
                    destination_account = txn.account

            result = self.create_transaction(txn, source_account, destination_account)

            if result:
                if result.get('status') == 'duplicate':
                    stats['duplicates'] += 1
                    # Log duplicate transaction details
                    print(f"  [DUPLICATE] {txn.date} | ${txn.amount:>9.2f} | {txn.description[:60]}")
                    logging.warning(f"DUPLICATE transaction detected: Date={txn.date}, Amount=${txn.amount:.2f}, Desc='{txn.description}', Account={txn.account}")
                else:
                    stats['created'] += 1
            else:
                stats['errors'] += 1
                # Log error details
                print(f"  [ERROR] Failed to create: {txn.date} | ${txn.amount:>9.2f} | {txn.description[:60]}")
                logging.error(f"ERROR creating transaction: Date={txn.date}, Amount=${txn.amount:.2f}, Desc='{txn.description}', Account={txn.account}, Source={source_account}, Dest={destination_account}")

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

    # Generate unique statement_id for this batch
    # This ensures transactions within the same statement are never marked as duplicates
    import hashlib
    import time
    import os
    statement_id = hashlib.md5(f"{os.path.basename(pdf_path)}_{time.time()}".encode()).hexdigest()[:12]

    # Assign statement_id to all transactions and auto-categorize
    for txn in transactions:
        txn.statement_id = statement_id
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
