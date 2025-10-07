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
    transaction_id: Optional[str] = None  # Unique identifier

    def __post_init__(self):
        if self.transaction_id is None:
            self.transaction_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID based on transaction details"""
        import hashlib
        data = f"{self.date}_{self.description}_{abs(self.amount)}_{self.account}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

    def to_dict(self):
        return asdict(self)


class AmexParser:
    """Parser for American Express statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            # Extract year from statement date on first page
            year = '2025'
            first_page_text = pdf.pages[0].extract_text()
            if first_page_text:
                # Look for "Date\nMonth DD, YYYY" pattern
                year_match = re.search(r'Date\s+\w+\s+\d{1,2},\s+(\d{4})', first_page_text)
                if year_match:
                    year = year_match.group(1)

            # Process all pages starting from page 2 (index 2)
            for page_num in range(2, len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if not text:
                    continue

                lines = text.split('\n')
                i = 0

                while i < len(lines):
                    line = lines[i].strip()

                    # Skip empty lines and section headers
                    if not line or 'TRANSACTION DETAILS' in line or 'Card Number' in line:
                        i += 1
                        continue

                    # Match transaction line: "MonthDay DESCRIPTION AMOUNT"
                    # Date format: "February22", "March1", etc. (no space between month and day!)
                    date_match = re.match(r'^([A-Z][a-z]+)(\d{1,2})\s+(.+)$', line)

                    if date_match:
                        month_str = date_match.group(1)
                        day_str = date_match.group(2)
                        rest_of_line = date_match.group(3).strip()

                        # Extract amount from end of line
                        amount_match = re.search(r'([\d,]+\.\d{2})$', rest_of_line)

                        if amount_match:
                            amount_str = amount_match.group(1).replace(',', '')
                            amount = float(amount_str)

                            # Description is everything before the amount
                            description = rest_of_line[:amount_match.start()].strip()

                            # Check if next line has "CR" (for credits) or foreign currency info
                            is_credit = False
                            if i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                if next_line == 'CR' or 'PAYMENT RECEIVED' in description.upper() or 'CASHBACK' in description.upper():
                                    is_credit = True

                                # Skip foreign currency lines
                                if 'DOLLAR' in next_line or 'RUPEE' in next_line or 'EURO' in next_line:
                                    i += 1
                                    if i + 1 < len(lines) and 'includes conversion commission' in lines[i + 1]:
                                        i += 1

                            # Make debits negative
                            if not is_credit:
                                amount = -amount

                            # Parse date
                            try:
                                # Construct date string "DD Month YYYY"
                                date_str = f"{day_str} {month_str} {year}"
                                date_obj = datetime.strptime(date_str, '%d %B %Y')

                                transactions.append(Transaction(
                                    date=date_obj.strftime('%Y-%m-%d'),
                                    description=description,
                                    amount=amount,
                                    account='AMEX',
                                    transaction_type='credit' if is_credit else 'debit'
                                ))
                            except ValueError as e:
                                pass

                    i += 1

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

                # Find transaction section: "Date Details Money out $ Money in $ Balance $"
                in_transactions = False
                i = 0

                while i < len(lines):
                    line = lines[i].strip()

                    # Look for header with "Date Details"
                    if 'Date' in line and 'Details' in line and 'Money' in line:
                        in_transactions = True
                        i += 1
                        continue

                    # Stop at page footer or next section
                    if 'Page' in line and 'of' in line:
                        in_transactions = False

                    if in_transactions:
                        # Match date pattern: DD/MM/YYYY
                        date_match = re.match(r'^(\d{1,2}/\d{1,2}/\d{4})\s+(.+)$', line)

                        if date_match:
                            date_str = date_match.group(1)
                            rest_of_line = date_match.group(2).strip()

                            # Collect description from this line and possibly next lines
                            description_parts = []

                            # Extract amounts from end of line: Money out, Money in, Balance
                            # Pattern: "Description [amount] [amount] amount"
                            amount_pattern = r'([\d,]+\.\d{2})'
                            amounts = re.findall(amount_pattern, rest_of_line)

                            if len(amounts) >= 3:
                                # Has money out, money in, and balance
                                # Format: ... money_out money_in balance
                                first_amount_pos = rest_of_line.find(amounts[0])
                                description_parts.append(rest_of_line[:first_amount_pos].strip())
                                money_out = amounts[0]
                                money_in = amounts[1]
                            elif len(amounts) == 2:
                                # Has money in and balance (no money out)
                                # Format: ... money_in balance
                                first_amount_pos = rest_of_line.find(amounts[0])
                                description_parts.append(rest_of_line[:first_amount_pos].strip())
                                money_out = None
                                money_in = amounts[0]

                            elif len(amounts) == 1:
                                # Only balance shown - look at previous line for details
                                first_amount_pos = rest_of_line.find(amounts[0])
                                description_parts.append(rest_of_line[:first_amount_pos].strip())
                                money_out = None
                                money_in = amounts[0]
                            else:
                                # No amounts on this line, description continues
                                description_parts.append(rest_of_line)
                                money_out = None
                                money_in = None

                            # Check next lines for continuation (lines without dates)
                            j = i + 1
                            while j < len(lines) and money_out is None and money_in is None:
                                next_line = lines[j].strip()

                                # If next line starts with a date, stop
                                if re.match(r'^\d{1,2}/\d{1,2}/\d{4}', next_line):
                                    break

                                # If next line has amounts
                                amounts = re.findall(amount_pattern, next_line)
                                if len(amounts) >= 1:
                                    # Extract amounts
                                    if len(amounts) == 3:
                                        # money_out, money_in, balance
                                        money_out = amounts[0] if amounts[0] else None
                                        money_in = amounts[1]
                                        # Balance is amounts[2]
                                    elif len(amounts) == 2:
                                        # money_in, balance
                                        money_out = None
                                        money_in = amounts[0]
                                    else:
                                        money_in = amounts[0]

                                    # Description is before amounts
                                    first_amount_pos = next_line.find(amounts[0])
                                    desc_part = next_line[:first_amount_pos].strip()
                                    if desc_part:
                                        description_parts.append(desc_part)
                                    break
                                else:
                                    # More description
                                    description_parts.append(next_line)

                                j += 1
                                i = j

                            # Create transaction
                            if money_in or money_out:
                                description = ' '.join(description_parts).strip()

                                # Clean description: remove "Receipt XXXXXX"
                                description = re.sub(r'-\s*Receipt\s+\d+', '', description).strip()

                                # Determine amount
                                if money_out and money_out != '0.00':
                                    amount = -float(money_out.replace(',', ''))
                                elif money_in:
                                    amount = float(money_in.replace(',', ''))
                                else:
                                    i += 1
                                    continue

                                try:
                                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')

                                    transactions.append(Transaction(
                                        date=date_obj.strftime('%Y-%m-%d'),
                                        description=description,
                                        amount=amount,
                                        account='ING Savings Maximiser',
                                        transaction_type='credit' if amount > 0 else 'debit'
                                    ))
                                except ValueError:
                                    pass

                    i += 1

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
            # CommBank statements have transactions on pages 2-3 (indices 1-2)
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if not text:
                    continue

                lines = text.split('\n')

                # Look for transaction section
                in_transactions = False
                for line in lines:
                    # Start parsing when we see "Date" and "Transaction details"
                    if 'Date' in line and 'Transaction details' in line:
                        in_transactions = True
                        continue

                    # Stop at certain markers
                    if any(marker in line for marker in ['Interest charged', 'Please check your transactions']):
                        in_transactions = False
                        continue

                    if not in_transactions:
                        continue

                    # Match date pattern: DD MMM
                    date_match = re.match(r'^(\d{2}\s+\w{3})\s+(.+)', line)
                    if date_match:
                        date_str = date_match.group(1)
                        rest_of_line = date_match.group(2).strip()

                        # Find amount at end of line
                        # Format can be: "123.45" or "123.45-" (for credits)
                        amount_match = re.search(r'(\d+\.\d{2})(-?)\s*$', rest_of_line)

                        if amount_match:
                            amount = float(amount_match.group(1))
                            has_minus = amount_match.group(2) == '-'

                            # Extract description (everything before the amount)
                            desc_end = rest_of_line.rfind(amount_match.group(0))
                            description = rest_of_line[:desc_end].strip()

                            # Determine if it's a credit or debit
                            # Credits have minus sign after amount or contain "Payment" or "Thank You"
                            is_credit = has_minus or 'Payment' in description or 'Thank You' in description or 'Refund' in description

                            # For credits, amount stays positive; for debits, make negative
                            if not is_credit:
                                amount = -amount

                            # Parse date - determine year from statement
                            # Try to extract year from statement period
                            year = '2025'  # Default
                            for check_line in lines:
                                year_match = re.search(r'(\d{2}\s+\w{3}\s+(\d{4}))', check_line)
                                if year_match:
                                    year = year_match.group(2)
                                    break

                            try:
                                date_obj = datetime.strptime(f"{date_str} {year}", '%d %b %Y')

                                transactions.append(Transaction(
                                    date=date_obj.strftime('%Y-%m-%d'),
                                    description=description,
                                    amount=amount,
                                    account='CommBank Diamond',
                                    transaction_type='credit' if is_credit else 'debit'
                                ))
                            except ValueError:
                                # Skip if date parsing fails
                                continue

        return transactions


class CommBankHomeLoanParser:
    """Parser for Commonwealth Bank Home Loan statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            # Extract year from first page
            year = '2020'
            first_page_text = pdf.pages[0].extract_text()
            if first_page_text:
                # Look for statement period with year
                year_match = re.search(r'Statement period.*?(\d{4})', first_page_text)
                if year_match:
                    year = year_match.group(1)

            # Process all pages
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if not text:
                    continue

                lines = text.split('\n')

                # Find transaction section
                in_transactions = False
                i = 0

                while i < len(lines):
                    line = lines[i].strip()

                    # Look for transaction header: "Date Transaction description Debits Credits Balance"
                    if 'Date' in line and 'Transaction' in line and ('Debit' in line or 'Credit' in line) and 'Balance' in line:
                        in_transactions = True
                        i += 1
                        continue

                    # Skip interest rate lines and stop markers
                    if in_transactions and ('Interest rate' in line or 'Page' in line):
                        i += 1
                        continue

                    # Stop at closing balance
                    if 'Closing balance' in line:
                        in_transactions = False

                    if in_transactions:
                        # Match transaction line: "DD MMM Description..."
                        date_match = re.match(r'^(\d{1,2}\s+\w{3})\s+(.+)$', line)

                        if date_match:
                            date_str = date_match.group(1)
                            rest_of_line = date_match.group(2).strip()

                            # Skip opening balance
                            if 'Opening balance' in rest_of_line:
                                i += 1
                                continue

                            # Look for amounts: pattern is "Description -amount $balance" or "Description amount $balance"
                            # Debits have minus sign before amount
                            amount_match = re.search(r'(-?[\d,]+\.\d{2})\s+\$[\d,]+\.\d{2}\s+DR', rest_of_line)

                            if amount_match:
                                amount_str = amount_match.group(1).replace(',', '')
                                amount = float(amount_str)

                                # Description is everything before the amount
                                description = rest_of_line[:amount_match.start()].strip()

                                # Clean up description
                                description = re.sub(r'\s+', ' ', description)

                                # Skip if no description or amount is 0
                                if not description or abs(amount) < 0.01:
                                    i += 1
                                    continue

                                # Parse date
                                try:
                                    date_obj = datetime.strptime(f"{date_str} {year}", '%d %b %Y')

                                    transactions.append(Transaction(
                                        date=date_obj.strftime('%Y-%m-%d'),
                                        description=description,
                                        amount=amount,
                                        account='CommBank Home Loan',
                                        transaction_type='credit' if amount > 0 else 'debit'
                                    ))
                                except ValueError:
                                    pass

                    i += 1

        return transactions


class CommBankEverydayOffsetParser:
    """Parser for Commonwealth Bank Everyday Offset account statements"""

    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []

        with pdfplumber.open(pdf_path) as pdf:
            # Extract year from first page
            year = '2025'
            first_page_text = pdf.pages[0].extract_text()
            if first_page_text:
                # Look for statement period with year - use "Period" or "OPENING BALANCE" line
                year_match = re.search(r'(?:Period|OPENING BALANCE).*?(\d{1,2}\s+\w+\s+(\d{4}))', first_page_text)
                if year_match:
                    year = year_match.group(2)
                else:
                    # Fallback: look for any 4-digit year 2020-2099
                    year_match = re.search(r'\b(20\d{2})\b', first_page_text)
                    if year_match:
                        year = year_match.group(1)

            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if not text:
                    continue

                lines = text.split('\n')

                # Find the header line
                header_idx = -1
                for idx, line in enumerate(lines):
                    if 'Date' in line and 'Transaction' in line and 'Balance' in line:
                        header_idx = idx
                        break

                if header_idx == -1:
                    continue

                # Process transaction lines after header
                i = header_idx + 1
                while i < len(lines):
                    line = lines[i].strip()

                    # Skip empty lines
                    if not line:
                        i += 1
                        continue

                    # Stop at summary sections
                    if any(keyword in line for keyword in [
                        'Opening balance - Total debits',
                        'Transaction Summary',
                        'Your Account Changes Summary',
                        'Transaction Type'
                    ]):
                        break

                    # Skip OPENING BALANCE and CLOSING BALANCE
                    if 'OPENING BALANCE' in line or 'CLOSING BALANCE' in line:
                        i += 1
                        continue

                    # Match transaction line starting with date: "DD MMM" or "DD MMM YYYY"
                    date_match = re.match(r'^(\d{1,2}\s+\w{3}(?:\s+\d{4})?)\s+(.+)$', line)

                    if not date_match:
                        i += 1
                        continue

                    date_str = date_match.group(1).strip()
                    rest_of_line = date_match.group(2).strip()

                    # Collect description and amount from this and following lines
                    # Format: "DD MMM Description... Amount Balance"
                    # Description can span multiple lines
                    description_parts = []
                    amount_str = None

                    # Parse rest of current line
                    # Look for amounts at the end: pattern like "450.00 $" or "$450.00" or "450.00 (" for debits
                    amount_pattern = r'(?:(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*\(?\s*\$?\s*(?:\$?([\d,]+\.\d{2})CR)?)\s*$'

                    # Try to find amount on current line
                    amount_match = re.search(r'([\d,]+\.\d{2})\s*\(?\s*\$', rest_of_line)
                    if amount_match:
                        amount_str = amount_match.group(1)
                        # Everything before the amount is description
                        description_parts.append(rest_of_line[:amount_match.start()].strip())
                    else:
                        # No amount on this line, description continues
                        description_parts.append(rest_of_line)

                        # Check next lines for continuation
                        j = i + 1
                        while j < len(lines) and amount_str is None:
                            next_line = lines[j].strip()

                            # If next line starts with a date, we've gone too far
                            if re.match(r'^\d{1,2}\s+\w{3}', next_line):
                                break

                            # Check if this line has an amount
                            amount_match = re.search(r'([\d,]+\.\d{2})\s*\(?\s*\$', next_line)
                            if amount_match:
                                amount_str = amount_match.group(1)
                                # Add description part before amount
                                desc_part = next_line[:amount_match.start()].strip()
                                if desc_part:
                                    description_parts.append(desc_part)
                                i = j
                                break
                            else:
                                # More description
                                description_parts.append(next_line)
                                i = j

                            j += 1

                    if not amount_str:
                        # Couldn't find amount, skip this transaction
                        i += 1
                        continue

                    # Determine if debit or credit
                    # Debits have "(" after amount, credits don't
                    is_debit = '(' in rest_of_line or (i < len(lines) and '(' in lines[i])

                    # Parse amount
                    try:
                        amount = float(amount_str.replace(',', ''))
                        if is_debit:
                            amount = -amount
                    except ValueError:
                        i += 1
                        continue

                    # Skip zero amounts
                    if abs(amount) < 0.01:
                        i += 1
                        continue

                    # Join description parts
                    description = ' '.join(description_parts).strip()

                    # Clean up description: remove trailing $ and whitespace
                    description = re.sub(r'\s*\$\s*$', '', description).strip()

                    if not description:
                        i += 1
                        continue

                    # Parse date
                    try:
                        if len(date_str.split()) == 3:
                            date_obj = datetime.strptime(date_str, '%d %b %Y')
                        else:
                            date_obj = datetime.strptime(f"{date_str} {year}", '%d %b %Y')

                        transactions.append(Transaction(
                            date=date_obj.strftime('%Y-%m-%d'),
                            description=description,
                            amount=amount,
                            account='CommBank Everyday Offset',
                            transaction_type='credit' if amount > 0 else 'debit'
                        ))
                    except ValueError:
                        pass

                    i += 1

        return transactions


class StatementParser:
    """Main parser that routes to specific bank parsers"""

    def __init__(self):
        self.parsers = {
            'amex': AmexParser(),
            'ing_orange': INGOrangeParser(),
            'ing_savings': INGSavingsParser(),
            'ubank': UBankParser(),
            'commbank': CommBankParser(),
            'commbank_homeloan': CommBankHomeLoanParser(),
            'commbank_offset': CommBankEverydayOffsetParser()
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
