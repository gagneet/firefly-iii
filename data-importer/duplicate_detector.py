"""
Transaction Duplicate Detection Module
Handles duplicate transactions across multiple bank accounts and statements
"""

from typing import List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import hashlib


@dataclass
class Transaction:
    """Normalized transaction structure"""
    date: str
    description: str
    amount: float
    category: str = None
    account: str = ""
    transaction_type: str = ""
    transaction_id: str = None  # Unique identifier

    def __post_init__(self):
        if self.transaction_id is None:
            self.transaction_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID based on transaction details"""
        # Include sign of amount to distinguish refunds from purchases
        data = f"{self.date}_{self.description}_{self.amount}_{self.account}"
        return hashlib.md5(data.encode()).hexdigest()[:16]


class DuplicateDetector:
    """Detects and handles duplicate transactions"""

    def __init__(
        self,
        date_tolerance_days: int = 2,
        amount_tolerance: float = 0.01,
        description_similarity_threshold: float = 0.85
    ):
        """
        Initialize duplicate detector

        Args:
            date_tolerance_days: How many days apart transactions can be and still match
            amount_tolerance: Acceptable difference in amounts (for rounding/fees)
            description_similarity_threshold: Minimum similarity score (0-1) for descriptions
        """
        self.date_tolerance_days = date_tolerance_days
        self.amount_tolerance = amount_tolerance
        self.description_similarity_threshold = description_similarity_threshold

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings (0-1)"""
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        return SequenceMatcher(None, text1, text2).ratio()

    def are_dates_close(self, date1: str, date2: str) -> bool:
        """Check if two dates are within tolerance"""
        d1 = datetime.strptime(date1, '%Y-%m-%d')
        d2 = datetime.strptime(date2, '%Y-%m-%d')
        return abs((d1 - d2).days) <= self.date_tolerance_days

    def are_amounts_close(self, amount1: float, amount2: float) -> bool:
        """Check if two amounts are within tolerance"""
        return abs(abs(amount1) - abs(amount2)) <= self.amount_tolerance

    def is_transfer_pair(self, txn1: Transaction, txn2: Transaction) -> bool:
        """
        Detect if two transactions are a transfer between accounts
        (one debit, one credit, similar amounts and dates)
        """
        # Must be from different accounts
        if txn1.account == txn2.account:
            return False

        # One must be debit, one must be credit
        if (txn1.amount * txn2.amount) >= 0:  # Same sign
            return False

        # Amounts must match (one negative, one positive)
        if not self.are_amounts_close(txn1.amount, txn2.amount):
            return False

        # Dates must be close
        if not self.are_dates_close(txn1.date, txn2.date):
            return False

        # Description should mention transfer or payment
        transfer_keywords = ['transfer', 'payment to', 'payment from', 'internal transfer']
        desc1 = txn1.description.lower()
        desc2 = txn2.description.lower()

        has_transfer_keyword = any(kw in desc1 or kw in desc2 for kw in transfer_keywords)

        # Check if descriptions reference each other's accounts
        account_referenced = (
            txn1.account.lower() in desc2 or
            txn2.account.lower() in desc1
        )

        return has_transfer_keyword or account_referenced

    def is_duplicate(self, txn1: Transaction, txn2: Transaction) -> bool:
        """
        Determine if two transactions are duplicates
        (same transaction appearing in multiple statements)
        """
        # Don't compare same transaction object to itself
        if txn1 is txn2:
            return False

        # Different accounts might have legitimate same transactions
        # Only flag as duplicate if from same account
        if txn1.account != txn2.account:
            return False

        # Dates must match closely
        if not self.are_dates_close(txn1.date, txn2.date):
            return False

        # Amounts must match (including sign)
        if not (abs(txn1.amount - txn2.amount) <= self.amount_tolerance):
            return False

        # Descriptions must be very similar
        similarity = self.calculate_similarity(txn1.description, txn2.description)
        if similarity < self.description_similarity_threshold:
            return False

        return True

    def find_duplicates(
        self,
        transactions: List[Transaction]
    ) -> Tuple[List[Transaction], List[Tuple[Transaction, Transaction]]]:
        """
        Find duplicate transactions in a list
        Optimized using transaction_id hash for O(n) performance

        Returns:
            Tuple of (unique_transactions, duplicate_pairs)
        """
        seen_ids = {}  # transaction_id -> Transaction object
        duplicates = []
        unique = []

        for txn in transactions:
            # Use transaction_id hash for quick duplicate detection
            # transaction_id is based on: date, description, amount, account
            txn_id = txn.transaction_id

            if txn_id in seen_ids:
                # Found exact duplicate (same date, description, amount, account)
                duplicates.append((seen_ids[txn_id], txn))
            else:
                # Not a duplicate - add to unique list
                unique.append(txn)
                seen_ids[txn_id] = txn

        return unique, duplicates

    def find_transfers(
        self,
        transactions: List[Transaction]
    ) -> List[Tuple[Transaction, Transaction]]:
        """
        Find transfer pairs (money moving between your own accounts)
        Optimized using date+amount indexing for better performance

        Returns:
            List of transfer pairs
        """
        transfers = []

        # Group transactions by date for faster lookup
        by_date = {}
        for txn in transactions:
            date_key = txn.date
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(txn)

        # Check for transfers only within same date (much faster)
        for date_key, date_txns in by_date.items():
            # Also check adjacent dates (within tolerance)
            date_obj = datetime.strptime(date_key, '%Y-%m-%d')
            dates_to_check = [date_key]

            for days_offset in range(1, self.date_tolerance_days + 1):
                next_date = (date_obj + timedelta(days=days_offset)).strftime('%Y-%m-%d')
                prev_date = (date_obj - timedelta(days=days_offset)).strftime('%Y-%m-%d')
                if next_date in by_date:
                    dates_to_check.append(next_date)
                if prev_date in by_date:
                    dates_to_check.append(prev_date)

            # Compare transactions within date range
            all_candidates = []
            for d in dates_to_check:
                if d in by_date:
                    all_candidates.extend(by_date[d])

            for i, txn1 in enumerate(date_txns):
                for txn2 in all_candidates:
                    if txn1 is not txn2 and self.is_transfer_pair(txn1, txn2):
                        # Avoid duplicate pairs
                        if (txn2, txn1) not in transfers:
                            transfers.append((txn1, txn2))

        return transfers

    def deduplicate(
        self,
        transactions: List[Transaction],
        remove_duplicate_transfers: bool = False
    ) -> List[Transaction]:
        """
        Remove duplicates from transaction list

        Args:
            transactions: List of all transactions
            remove_duplicate_transfers: If True, removes BOTH sides of internal transfers
                                       (use this to avoid double-counting internal moves)

        Returns:
            Deduplicated list of transactions
        """
        # First, find and remove exact duplicates
        unique, _ = self.find_duplicates(transactions)

        # Then handle transfers if requested
        if remove_duplicate_transfers:
            transfers = self.find_transfers(unique)
            transfer_ids = set()

            for txn1, txn2 in transfers:
                transfer_ids.add(txn1.transaction_id)
                transfer_ids.add(txn2.transaction_id)

            # Remove all transfer transactions
            unique = [txn for txn in unique if txn.transaction_id not in transfer_ids]

        return unique

    def categorize_duplicates(
        self,
        transactions: List[Transaction]
    ) -> dict:
        """
        Categorize all transactions into duplicates, transfers, and unique

        Returns:
            Dictionary with 'unique', 'duplicates', 'transfers', and 'all_clean'
        """
        # Find exact duplicates
        unique_after_dedup, duplicate_pairs = self.find_duplicates(transactions)

        # Find transfers
        transfer_pairs = self.find_transfers(unique_after_dedup)

        # Get transaction IDs involved in transfers
        transfer_ids = set()
        for txn1, txn2 in transfer_pairs:
            transfer_ids.add(txn1.transaction_id)
            transfer_ids.add(txn2.transaction_id)

        # Separate unique transactions (not duplicates, not transfers)
        truly_unique = [
            txn for txn in unique_after_dedup
            if txn.transaction_id not in transfer_ids
        ]

        return {
            'unique': truly_unique,
            'duplicates': duplicate_pairs,
            'transfers': transfer_pairs,
            'all_clean': unique_after_dedup,  # No exact duplicates, but includes transfers
            'stats': {
                'total_input': len(transactions),
                'exact_duplicates_removed': len(duplicate_pairs),
                'transfers_found': len(transfer_pairs),
                'final_unique_count': len(truly_unique)
            }
        }


def generate_deduplication_report(result: dict) -> str:
    """Generate a human-readable report of deduplication results"""
    report = []
    report.append("="*60)
    report.append("TRANSACTION DEDUPLICATION REPORT")
    report.append("="*60)
    report.append("")

    stats = result['stats']
    report.append(f"Total transactions processed: {stats['total_input']}")
    report.append(f"Exact duplicates removed: {stats['exact_duplicates_removed']}")
    report.append(f"Transfer pairs identified: {stats['transfers_found']}")
    report.append(f"Final unique transactions: {stats['final_unique_count']}")
    report.append("")

    if result['duplicates']:
        report.append("-"*60)
        report.append("DUPLICATE TRANSACTIONS FOUND:")
        report.append("-"*60)
        for txn1, txn2 in result['duplicates']:
            report.append(f"  {txn1.date} | {txn1.description[:40]:40} | ${txn1.amount:8.2f}")
            report.append(f"  {txn2.date} | {txn2.description[:40]:40} | ${txn2.amount:8.2f}")
            report.append("")

    if result['transfers']:
        report.append("-"*60)
        report.append("INTERNAL TRANSFERS IDENTIFIED:")
        report.append("-"*60)
        for txn1, txn2 in result['transfers']:
            report.append(f"  FROM: {txn1.account:20} | {txn1.date} | ${abs(txn1.amount):8.2f}")
            report.append(f"  TO:   {txn2.account:20} | {txn2.date} | ${abs(txn2.amount):8.2f}")
            report.append(f"        {txn1.description}")
            report.append("")

    report.append("="*60)
    return "\n".join(report)


# Example usage
if __name__ == '__main__':
    # Example transactions with duplicates and transfers
    sample_transactions = [
        Transaction('2025-04-03', 'Salary Deposit', 2701.40, account='ING Orange'),
        Transaction('2025-04-03', 'Internal Transfer to Savings', -2500.00, account='ING Orange'),
        Transaction('2025-04-03', 'From Orange Everyday', 2500.00, account='ING Savings'),
        Transaction('2025-04-05', 'Woolworths Belconnen', -49.66, account='AMEX'),
        Transaction('2025-04-05', 'Woolworths Belconnen', -49.66, account='AMEX'),  # Duplicate
        Transaction('2025-04-08', 'Payment to CommBank', -5839.13, account='uBank'),
        Transaction('2025-04-08', 'Payment from uBank', 5839.13, account='CommBank'),
    ]

    detector = DuplicateDetector()
    result = detector.categorize_duplicates(sample_transactions)

    print(generate_deduplication_report(result))

    print("\nFinal clean transactions (no duplicates):")
    for txn in result['all_clean']:
        print(f"{txn.date} | {txn.account:20} | {txn.description[:40]:40} | ${txn.amount:8.2f}")

    print("\nFor expense reporting (transfers removed):")
    for txn in result['unique']:
        print(f"{txn.date} | {txn.account:20} | {txn.description[:40]:40} | ${txn.amount:8.2f}")
