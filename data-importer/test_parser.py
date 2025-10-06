#!/usr/bin/env python3
"""
Test script for bank statement parser
Verifies that the parser can extract transactions from a PDF
"""

import sys
from statement_parser import StatementParser, Transaction


def test_parser(pdf_path: str, bank_type: str):
    """Test parsing a bank statement"""

    print(f"\n{'='*70}")
    print(f"Testing {bank_type.upper()} Parser")
    print(f"{'='*70}\n")

    parser = StatementParser()

    try:
        # Parse the PDF
        print(f"📄 Parsing: {pdf_path}")
        transactions = parser.parse_statement(pdf_path, bank_type)

        if not transactions:
            print("❌ No transactions found!")
            return False

        print(f"✅ Extracted {len(transactions)} transactions\n")

        # Display summary
        print(f"{'Date':<12} {'Description':<40} {'Amount':>12} {'Type':<8}")
        print("-" * 70)

        total_income = 0
        total_expenses = 0

        for txn in transactions[:10]:  # Show first 10
            amount_str = f"${abs(txn.amount):,.2f}"
            if txn.amount < 0:
                amount_str = f"-{amount_str}"
                total_expenses += abs(txn.amount)
            else:
                amount_str = f"+{amount_str}"
                total_income += txn.amount

            # Truncate description
            desc = txn.description[:38] + ".." if len(txn.description) > 40 else txn.description

            print(f"{txn.date:<12} {desc:<40} {amount_str:>12} {txn.transaction_type:<8}")

        if len(transactions) > 10:
            print(f"... and {len(transactions) - 10} more transactions")

        # Summary
        print("\n" + "-" * 70)
        print(f"Total Income:   ${total_income:>10,.2f}")
        print(f"Total Expenses: ${total_expenses:>10,.2f}")
        print(f"Net:            ${(total_income - total_expenses):>10,.2f}")

        # Test categorization
        print("\n" + "=" * 70)
        print("Testing Auto-Categorization")
        print("=" * 70 + "\n")

        category_counts = {}
        for txn in transactions:
            txn.category = parser.categorize_transaction(txn)
            category_counts[txn.category] = category_counts.get(txn.category, 0) + 1

        print(f"{'Category':<20} {'Count':>10}")
        print("-" * 30)
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            print(f"{category:<20} {count:>10}")

        print("\n✅ Parser test successful!\n")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python test_parser.py <bank_type> <pdf_file>")
        print("\nSupported bank types:")
        print("  - amex")
        print("  - ing_orange")
        print("  - ing_savings")
        print("  - ubank")
        print("  - commbank")
        print("\nExample:")
        print("  python test_parser.py amex statement.pdf")
        sys.exit(1)

    bank_type = sys.argv[1]
    pdf_path = sys.argv[2]

    success = test_parser(pdf_path, bank_type)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
