"""
Updated Commonwealth Bank Parsers
Handles Home Loan and Everyday Offset account statements
"""

import re
from datetime import datetime
from typing import List
import pdfplumber


class CommBankHomeLoanParser:
    """Parser for Commonwealth Bank Home Loan statements"""
    
    def parse(self, pdf_path: str) -> List[Transaction]:
        transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            # Extract year from first page
            year = '2025'
            first_page_text = pdf.pages[0].extract_text()
            if first_page_text:
                # Look for statement period with year
                year_match = re.search(r'(\d{1,2}\s+\w+\s+(\d{4}))', first_page_text)
                if year_match:
                    year = year_match.group(2)
            
            # Start from page 2 (index 1) where transactions usually are
            for page_num in range(1, len(pdf.pages)):
                page = pdf.pages[page_num]
                
                # Try table extraction first
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    # Find header row
                    header_idx = -1
                    for idx, row in enumerate(table):
                        if row and 'Date' in str(row[0]) and 'Transaction' in str(row):
                            header_idx = idx
                            break
                    
                    if header_idx == -1:
                        continue
                    
                    # Process data rows
                    for row in table[header_idx + 1:]:
                        if not row or len(row) < 4:
                            continue
                        
                        date_str = str(row[0]).strip() if row[0] else ''
                        description = str(row[1]).strip() if row[1] else ''
                        debit_str = str(row[2]).strip() if len(row) > 2 and row[2] else ''
                        credit_str = str(row[3]).strip() if len(row) > 3 and row[3] else ''
                        
                        # Skip if date is not valid or is header
                        if not date_str or date_str == 'Date' or date_str.lower() in ['opening balance', 'closing balance']:
                            continue
                        
                        # Parse date - format is "DD MMM" 
                        date_match = re.match(r'(\d{1,2}\s+\w{3})', date_str)
                        if not date_match:
                            continue
                        
                        # Parse amount
                        amount = 0.0
                        is_credit = False
                        
                        if credit_str and credit_str not in ['', 'Credits', 'Credit']:
                            try:
                                # Remove $ and commas
                                amount = float(credit_str.replace('$', '').replace(',', '').replace('(', '').replace(')', ''))
                                is_credit = True
                            except:
                                continue
                        elif debit_str and debit_str not in ['', 'Debits', 'Debit']:
                            try:
                                amount = float(debit_str.replace('$', '').replace(',', '').replace('(', '').replace(')', ''))
                                is_credit = False
                            except:
                                continue
                        
                        if amount == 0.0:
                            continue
                        
                        # For debits, make negative
                        if not is_credit:
                            amount = -amount
                        
                        # Parse date with year
                        try:
                            date_obj = datetime.strptime(f"{date_str} {year}", '%d %b %Y')
                            
                            # Clean description
                            clean_desc = description.strip()
                            
                            transactions.append(Transaction(
                                date=date_obj.strftime('%Y-%m-%d'),
                                description=clean_desc,
                                amount=amount,
                                account='CommBank Home Loan',
                                transaction_type='credit' if is_credit else 'debit'
                            ))
                        except ValueError:
                            continue
        
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
                # Look for statement period with year
                year_match = re.search(r'(\d{1,2}\s+\w+\s+(\d{4}))', first_page_text)
                if year_match:
                    year = year_match.group(2)
            
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                
                # Try table extraction
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    # Find header row - looking for Date, Transaction, Debit, Credit, Balance
                    header_idx = -1
                    for idx, row in enumerate(table):
                        if row and 'Date' in str(row[0]) and 'Transaction' in str(row):
                            header_idx = idx
                            break
                    
                    if header_idx == -1:
                        continue
                    
                    # Process data rows
                    for row in table[header_idx + 1:]:
                        if not row or len(row) < 4:
                            continue
                        
                        date_str = str(row[0]).strip() if row[0] else ''
                        description = str(row[1]).strip() if row[1] else ''
                        debit_str = str(row[2]).strip() if len(row) > 2 and row[2] else ''
                        credit_str = str(row[3]).strip() if len(row) > 3 and row[3] else ''
                        
                        # Skip opening/closing balance or invalid dates
                        if not date_str or 'OPENING BALANCE' in date_str.upper() or 'CLOSING BALANCE' in date_str.upper():
                            continue
                        
                        # Parse date - can be "DD MMM" or "DD MMM YYYY"
                        date_match = re.match(r'(\d{1,2}\s+\w{3}(?:\s+\d{4})?)', date_str)
                        if not date_match:
                            continue
                        
                        date_parse = date_match.group(1).strip()
                        
                        # Parse amount
                        amount = 0.0
                        is_credit = False
                        
                        if credit_str and credit_str not in ['', 'Credit', 'Credits']:
                            try:
                                amount = float(credit_str.replace('$', '').replace(',', ''))
                                is_credit = True
                            except:
                                continue
                        elif debit_str and debit_str not in ['', 'Debit', 'Debits']:
                            try:
                                amount = float(debit_str.replace('$', '').replace(',', ''))
                                is_credit = False
                            except:
                                continue
                        
                        if amount == 0.0:
                            continue
                        
                        # For debits, make negative
                        if not is_credit:
                            amount = -amount
                        
                        # Parse date
                        try:
                            # Try with year first
                            if len(date_parse.split()) == 3:
                                date_obj = datetime.strptime(date_parse, '%d %b %Y')
                            else:
                                # Add year
                                date_obj = datetime.strptime(f"{date_parse} {year}", '%d %b %Y')
                            
                            # Clean description
                            clean_desc = description.strip()
                            
                            transactions.append(Transaction(
                                date=date_obj.strftime('%Y-%m-%d'),
                                description=clean_desc,
                                amount=amount,
                                account='CommBank Everyday Offset',
                                transaction_type='credit' if is_credit else 'debit'
                            ))
                        except ValueError:
                            continue
        
        return transactions


# Update the main StatementParser class to include these new parsers
class StatementParser:
    """Main parser that routes to specific bank parsers"""
    
    def __init__(self):
        self.parsers = {
            'amex': AmexParser(),
            'amex_business': AmexParser(),
            'amex_cashback': AmexParser(),
            'ing_orange': INGOrangeParser(),
            'ing_savings': INGSavingsParser(),
            'ubank': UBankParser(),
            'commbank': CommBankParser(),  # Credit card
            'commbank_homeloan': CommBankHomeLoanParser(),
            'commbank_offset': CommBankEverydayOffsetParser()
        }
    
    def parse_statement(self, pdf_path: str, bank_type: str) -> List[Transaction]:
        """
        Parse a bank statement
        
        Args:
            pdf_path: Path to PDF statement
            bank_type: One of the supported bank types
        
        Returns:
            List of Transaction objects
        """
        if bank_type not in self.parsers:
            raise ValueError(f"Unknown bank type: {bank_type}. Must be one of {list(self.parsers.keys())}")
        
        return self.parsers[bank_type].parse(pdf_path)
