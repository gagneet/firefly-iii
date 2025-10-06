"""
Bank Statement Transaction Parser
Extracts and normalizes transactions from multiple Australian bank statements
"""

import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import pdfplumber


@dataclass
class Transaction:
    """Normalized transaction structure"""
    date: str  # ISO format YYYY-MM-DD
    description: str
    amount: float  # Positive for income, negative for expenses
    category: Optional[str] = None
    account: str = ""
    transaction_type: str = ""  # debit/credit/transfer

    def to_dict(self):
        return asdict(self)


class AmexParser:
    """Parser for American Express statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num in [2, 3]:  # Transaction pages
                if page_num >= len(pdf.pages):
                    continue

                page = pdf.pages[page_num]
                text = page.extract_text()

                # Parse transaction lines
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    # Match date pattern: DD MMM or DD/MM/YYYY
                    date_match = re.match(r'(\d{2}\s+\w{3}|\d{2}/\d{2}/\d{4})', line)
                    if date_match:
                        parts = line.split()
                        if len(parts) >= 2:
                            date_str = parts[0] + ' ' + parts[1] if ' ' in date_match.group() else parts[0]

                            # Extract description and amount
                            amount_match = re.search(r'(\d+\.\d{2})', line)
                            if amount_match:
                                amount = float(amount_match.group(1))
                                desc_end = line.rfind(amount_match.group(1))
                                description = line[len(date_str):desc_end].strip()

                                # Determine if credit or debit
                                is_credit = 'CR' in line or 'Payment' in description or 'Cashback' in description
                                amount = amount if is_credit else -amount

                                # Parse date
                                try:
                                    if '/' in date_str:
                                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                                    else:
                                        # Assume current/previous year
                                        date_obj = datetime.strptime(date_str + ' 2025', '%d %b %Y')

                                    transactions.append(Transaction(
                                        date=date_obj.strftime('%Y-%m-%d'),
                                        description=description,
                                        amount=amount,
                                        account='AMEX',
                                        transaction_type='credit' if is_credit else 'debit'
                                    ))
                                except ValueError:
                                    continue

        return transactions


class INGOrangeParser:
    """Parser for ING Orange Everyday statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')

                for line in lines:
                    # Match date pattern DD/MM/YYYY
                    date_match = re.match(r'(\d{2}/\d{2}/\d{4})', line)
                    if date_match:
                        parts = line.split()
                        date_str = parts[0]

                        # Find amount (last number before balance)
                        amounts = re.findall(r'-?\d+,?\d*\.\d{2}', line)
                        if len(amounts) >= 2:
                            amount_str = amounts[-2]  # Second to last is transaction amount
                            amount = float(amount_str.replace(',', ''))

                            # Description is between date and amount
                            desc_start = len(date_str)
                            desc_end = line.rfind(amount_str)
                            description = line[desc_start:desc_end].strip()

                            # Remove Receipt numbers
                            description = re.sub(r'- Receipt \d+', '', description).strip()

                            date_obj = datetime.strptime(date_str, '%d/%m/%Y')

                            transactions.append(Transaction(
                                date=date_obj.strftime('%Y-%m-%d'),
                                description=description,
                                amount=amount,
                                account='ING Orange Everyday',
                                transaction_type='credit' if amount > 0 else 'debit'
                            ))

        return transactions


class INGSavingsParser:
    """Parser for ING Savings Maximiser statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')

                in_transactions = False
                for line in lines:
                    if 'Date' in line and 'Description' in line:
                        in_transactions = True
                        continue

                    if in_transactions and 'Closing Balance' in line:
                        break

                    if in_transactions:
                        # Match date pattern DD MMM YYYY
                        date_match = re.match(r'(\d{2}\s+\w{3}\s+\d{4})', line)
                        if date_match:
                            date_str = date_match.group(1)

                            # Extract description and amounts
                            parts = re.split(r'\s{2,}', line)
                            if len(parts) >= 3:
                                description = parts[1] if len(parts) > 1 else ''

                                # Get deposit and withdrawal
                                amounts = re.findall(r'-?\$?(\d+,?\d*\.\d{2})', line)
                                if amounts:
                                    # Check if withdrawal or deposit
                                    if 'Withdrawal' in line or line.count('(') >= 2:
                                        amount = -float(amounts[1].replace(',', '')) if len(amounts) > 1 else float(amounts[0].replace(',', ''))
                                    else:
                                        amount = float(amounts[0].replace(',', ''))

                                    date_obj = datetime.strptime(date_str, '%d %b %Y')

                                    transactions.append(Transaction(
                                        date=date_obj.strftime('%Y-%m-%d'),
                                        description=description,
                                        amount=amount,
                                        account='ING Savings Maximiser',
                                        transaction_type='credit' if amount > 0 else 'debit'
                                    ))

        return transactions


class UBankParser:
    """Parser for uBank Spend Account statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')

                for line in lines:
                    # Match date pattern DD MMM YYYY
                    date_match = re.match(r'(\d{2}\s+\w{3}\s+\d{4})', line)
                    if date_match:
                        date_str = date_match.group(1)

                        # Extract amounts
                        amounts = re.findall(r'-?\$?(\d+,?\d*\.\d{2})', line)
                        if amounts:
                            # Description is between date and first amount
                            desc_start = len(date_str)
                            first_amount_pos = line.find(amounts[0])
                            description = line[desc_start:first_amount_pos].strip()
                            description = description.replace('$', '').strip()

                            # Determine amount (debit or credit)
                            if len(amounts) == 2:
                                # Has both debit and credit columns
                                debit = amounts[0] if '-' not in line.split()[0] else None
                                credit = amounts[1] if len(amounts) > 1 else None
                                amount = float(credit.replace(',', '')) if credit else -float(debit.replace(',', ''))
                            else:
                                amount_str = amounts[0].replace(',', '')
                                amount = float(amount_str)
                                if '-' in line.split(description)[1].split()[0]:
                                    amount = -amount

                            date_obj = datetime.strptime(date_str, '%d %b %Y')

                            transactions.append(Transaction(
                                date=date_obj.strftime('%Y-%m-%d'),
                                description=description,
                                amount=amount,
                                account='uBank Spend',
                                transaction_type='credit' if amount > 0 else 'debit'
                            ))

        return transactions


class CommBankParser:
    """Parser for Commonwealth Bank statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num in [1, 2]:  # Transaction pages
                if page_num >= len(pdf.pages):
                    continue

                page = pdf.pages[page_num]
                text = page.extract_text()
                lines = text.split('\n')

                for line in lines:
                    # Match date pattern DD MMM
                    date_match = re.match(r'(\d{2}\s+\w{3})', line)
                    if date_match:
                        date_str = date_match.group(1)

                        # Extract amount (last number on line)
                        amount_match = re.search(r'(\d+\.\d{2})(?:\s|$)', line)
                        if amount_match:
                            amount = float(amount_match.group(1))

                            # Description is between date and amount
                            desc_start = len(date_str)
                            desc_end = line.rfind(amount_match.group(1))
                            description = line[desc_start:desc_end].strip()

                            # Check if it's a credit (payment/refund)
                            is_credit = 'Payment' in line or 'Refund' in line or line.endswith('-')
                            amount = amount if is_credit else -amount

                            # Parse date (assume 2025)
                            date_obj = datetime.strptime(date_str + ' 2025', '%d %b %Y')

                            transactions.append(Transaction(
                                date=date_obj.strftime('%Y-%m-%d'),
                                description=description,
                                amount=amount,
                                account='CommBank Diamond',
                                transaction_type='credit' if is_credit else 'debit'
                            ))

        return transactions


class StatementParser:
    """Main parser that routes to specific bank parsers"""

    def __init__(self):
        self.parsers = {
            'amex': AmexParser(),
            'ing_orange': INGOrangeParser(),
            'ing_savings': INGSavingsParser(),
            'ubank': UBankParser(),
            'commbank': CommBankParser()
        }

    def parse_statement(self, pdf_path: str, bank_type: str) -> List[Transaction]:
        """
        Parse a bank statement

        Args:
            pdf_path: Path to PDF statement
            bank_type: One of 'amex', 'ing_orange', 'ing_savings', 'ubank', 'commbank'

        Returns:
            List of Transaction objects
        """
        if bank_type not in self.parsers:
            raise ValueError(f"Unknown bank type: {bank_type}. Must be one of {list(self.parsers.keys())}")

        return self.parsers[bank_type].parse(pdf_path)

    def categorize_transaction(self, transaction: Transaction) -> str:
        """
        Auto-categorize transaction based on description
        You can expand this with your own rules
        """
        desc = transaction.description.lower()

        # Groceries
        if any(word in desc for word in ['woolworths', 'coles', 'aldi', 'iga', 'costco', 'supermarket']):
            return 'Groceries'

        # Dining
        if any(word in desc for word in ['restaurant', 'cafe', 'pizza', 'sushi', 'chicken', 'indian', 'chinese']):
            return 'Dining Out'

        # Utilities
        if any(word in desc for word in ['origin energy', 'electricity', 'gas', 'water', 'internet']):
            return 'Utilities'

        # Transport
        if any(word in desc for word in ['petrol', 'fuel', 'parking', 'uber', 'toll']):
            return 'Transport'

        # Shopping
        if any(word in desc for word in ['ikea', 'kmart', 'target', 'myer', 'temu']):
            return 'Shopping'

        # Income
        if any(word in desc for word in ['salary', 'wage', 'pay', 'deposit']) and transaction.amount > 0:
            return 'Income'

        # Transfers
        if any(word in desc for word in ['transfer', 'payment to', 'payment from']):
            return 'Transfer'

        return 'Uncategorized'


# Example usage
if __name__ == '__main__':
    parser = StatementParser()

    # Parse different bank statements
    # transactions = parser.parse_statement('amex_statement.pdf', 'amex')
    # transactions = parser.parse_statement('ing_statement.pdf', 'ing_orange')

    # Auto-categorize
    # for txn in transactions:
    #     txn.category = parser.categorize_transaction(txn)
    #     print(f"{txn.date} | {txn.description[:30]:30} | ${txn.amount:8.2f} | {txn.category}")

    # Export to CSV
    # import csv
    # with open('transactions.csv', 'w', newline='') as f:
    #     writer = csv.DictWriter(f, fieldnames=['date', 'description', 'amount', 'category', 'account', 'transaction_type'])
    #     writer.writeheader()
    #     writer.writerows([t.to_dict() for t in transactions])

    print("Parser ready. Uncomment example code to use.")
