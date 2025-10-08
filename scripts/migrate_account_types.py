#!/usr/bin/env python3
"""
Account Type Migration Script
Converts incorrectly typed accounts (Asset) to correct types (Liability/Loan/Mortgage)
All transactions are preserved automatically by Firefly III
"""

import mysql.connector
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'fireflyuser',
    'password': 'Gagneet$5',
    'database': 'firefly_db'
}

# Account type mappings
ACCOUNT_TYPE_MAP = {
    'Asset account': 1,
    'Credit card': 4,
    'Loan': 11,
    'Mortgage': 12,
    'Liability credit account': 10
}

def detect_correct_type(account_name):
    """Detect what account type an account should be"""
    name_lower = account_name.lower()

    # Credit cards
    if any(keyword in name_lower for keyword in [
        'amex', 'american express', 'mastercard', 'visa',
        'credit card', 'diamond', 'platinum', 'cashback'
    ]):
        return 'Credit card'

    # Mortgages
    if any(keyword in name_lower for keyword in ['home loan', 'mortgage']):
        return 'Mortgage'

    # Loans
    if any(keyword in name_lower for keyword in ['personal loan', 'loan', 'car loan']):
        # Exclude home loans
        if 'home' not in name_lower:
            return 'Loan'

    return 'Asset account'

def get_accounts_to_migrate(conn):
    """Get list of accounts that need type migration"""
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        a.id,
        a.name,
        a.account_type_id as current_type_id,
        at.type as current_type,
        (SELECT COUNT(*) FROM transactions t
         JOIN transaction_journals tj ON t.transaction_journal_id = tj.id
         WHERE t.account_id = a.id) as transaction_count
    FROM accounts a
    JOIN account_types at ON a.account_type_id = at.id
    WHERE at.type = 'Asset account'
    """

    cursor.execute(query)
    accounts = cursor.fetchall()

    # Filter accounts that need migration
    accounts_to_migrate = []
    for account in accounts:
        correct_type = detect_correct_type(account['name'])
        if correct_type != account['current_type']:
            account['should_be_type'] = correct_type
            account['should_be_type_id'] = ACCOUNT_TYPE_MAP[correct_type]
            accounts_to_migrate.append(account)

    cursor.close()
    return accounts_to_migrate

def migrate_account(conn, account_id, new_type_id, account_name, old_type, new_type):
    """Migrate an account to a new type"""
    cursor = conn.cursor()

    try:
        # Update the account type
        update_query = """
        UPDATE accounts
        SET account_type_id = %s,
            updated_at = NOW()
        WHERE id = %s
        """

        cursor.execute(update_query, (new_type_id, account_id))
        conn.commit()

        print(f"✓ Migrated account #{account_id} '{account_name}'")
        print(f"  From: {old_type} → To: {new_type}")

        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Error migrating account #{account_id}: {e}")
        return False
    finally:
        cursor.close()

def create_backup(conn):
    """Create a backup of accounts table"""
    cursor = conn.cursor()

    backup_table = f"accounts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        cursor.execute(f"CREATE TABLE {backup_table} LIKE accounts")
        cursor.execute(f"INSERT INTO {backup_table} SELECT * FROM accounts")
        conn.commit()
        print(f"✓ Created backup table: {backup_table}")
        cursor.close()
        return backup_table
    except Exception as e:
        print(f"✗ Error creating backup: {e}")
        cursor.close()
        return None

def main():
    """Main migration function"""
    print("="*70)
    print("Firefly III Account Type Migration")
    print("="*70)
    print()

    # Connect to database
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✓ Connected to database")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)

    # Get accounts that need migration
    print("\nScanning for accounts that need migration...")
    accounts = get_accounts_to_migrate(conn)

    if not accounts:
        print("✓ No accounts need migration. All accounts are correctly typed!")
        conn.close()
        return

    # Display accounts to migrate
    print(f"\nFound {len(accounts)} account(s) to migrate:")
    print("-" * 70)
    for account in accounts:
        print(f"Account ID: {account['id']}")
        print(f"  Name: {account['name']}")
        print(f"  Current Type: {account['current_type']}")
        print(f"  Should Be: {account['should_be_type']}")
        print(f"  Transactions: {account['transaction_count']}")
        print()

    # Confirm migration
    response = input("Proceed with migration? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Migration cancelled.")
        conn.close()
        return

    # Create backup
    print("\nCreating backup...")
    backup_table = create_backup(conn)
    if not backup_table:
        print("✗ Backup failed. Migration cancelled for safety.")
        conn.close()
        return

    # Perform migrations
    print("\nMigrating accounts...")
    print("-" * 70)

    success_count = 0
    fail_count = 0

    for account in accounts:
        success = migrate_account(
            conn,
            account['id'],
            account['should_be_type_id'],
            account['name'],
            account['current_type'],
            account['should_be_type']
        )

        if success:
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print("\n" + "="*70)
    print("Migration Summary")
    print("="*70)
    print(f"Total accounts: {len(accounts)}")
    print(f"Successfully migrated: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Backup table: {backup_table}")
    print()

    if fail_count == 0:
        print("✓ All accounts migrated successfully!")
        print("\nIMPORTANT: Your transactions are preserved automatically.")
        print("The account balances will now show correctly as liabilities.")
    else:
        print("⚠ Some migrations failed. Check error messages above.")
        print(f"You can restore from backup table: {backup_table}")

    conn.close()

if __name__ == '__main__':
    main()
