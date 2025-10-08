#!/bin/bash
#
# Account Type Migration Script
# Migrates incorrectly typed accounts to correct Firefly III account types
#

set -e

DB_USER="fireflyuser"
DB_PASS="Gagneet\$5"
DB_NAME="firefly_db"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "======================================================================"
echo "Firefly III Account Type Migration"
echo "======================================================================"
echo ""

# Function to execute MySQL query
mysql_query() {
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$1" 2>/dev/null
}

# Create backup
echo "Creating backup..."
BACKUP_TABLE="accounts_backup_${BACKUP_TIMESTAMP}"
mysql_query "CREATE TABLE $BACKUP_TABLE LIKE accounts"
mysql_query "INSERT INTO $BACKUP_TABLE SELECT * FROM accounts"
echo "✓ Backup created: $BACKUP_TABLE"
echo ""

# Get accounts to migrate
echo "Scanning for accounts that need migration..."
ACCOUNTS=$(mysql_query "
SELECT
    a.id,
    a.name,
    at.type as current_type,
    (SELECT COUNT(*) FROM transactions t
     JOIN transaction_journals tj ON t.transaction_journal_id = tj.id
     WHERE t.account_id = a.id) as txn_count
FROM accounts a
JOIN account_types at ON a.account_type_id = at.id
WHERE at.type = 'Asset account'
  AND (a.name LIKE '%AMEX%'
       OR a.name LIKE '%Diamond%'
       OR a.name LIKE '%Platinum%'
       OR a.name LIKE '%Cashback%'
       OR a.name LIKE '%Business%'
       OR a.name LIKE '%Home Loan%'
       OR a.name LIKE '%Personal Loan%')
ORDER BY a.name
" | tail -n +2)

if [ -z "$ACCOUNTS" ]; then
    echo "✓ No accounts need migration!"
    exit 0
fi

echo "Found accounts to migrate:"
echo "----------------------------------------------------------------------"
echo "$ACCOUNTS"
echo "----------------------------------------------------------------------"
echo ""

# Display summary
echo "$ACCOUNTS" | while IFS=$'\t' read -r id name current_type txn_count; do
    # Detect target type
    target_type="Credit card (4)"
    if [[ "$name" =~ "Home Loan" ]]; then
        target_type="Mortgage (12)"
    elif [[ "$name" =~ "Personal Loan" ]] || [[ "$name" =~ " Loan" ]]; then
        target_type="Loan (11)"
    fi

    echo "Account: $name (ID: $id)"
    echo "  Current: $current_type"
    echo "  Target: $target_type"
    echo "  Transactions: $txn_count"
    echo ""
done

# Confirm
read -p "Proceed with migration? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Migration cancelled."
    exit 0
fi

echo ""
echo "Migrating accounts..."
echo "----------------------------------------------------------------------"

# Migrate each account
SUCCESS_COUNT=0
FAIL_COUNT=0

echo "$ACCOUNTS" | while IFS=$'\t' read -r id name current_type txn_count; do
    # Detect target type ID
    target_type_id=4  # Credit card by default
    target_type_name="Credit card"

    if [[ "$name" =~ "Home Loan" ]]; then
        target_type_id=12
        target_type_name="Mortgage"
    elif [[ "$name" =~ "Personal Loan" ]] || ( [[ "$name" =~ " Loan" ]] && ! [[ "$name" =~ "Home Loan" ]] ); then
        target_type_id=11
        target_type_name="Loan"
    fi

    # Perform migration
    mysql_query "UPDATE accounts SET account_type_id = $target_type_id, updated_at = NOW() WHERE id = $id" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✓ Migrated: $name (ID: $id) → $target_type_name"
        ((SUCCESS_COUNT++))
    else
        echo "✗ Failed: $name (ID: $id)"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "======================================================================"
echo "Migration Complete!"
echo "======================================================================"
echo "Backup table: $BACKUP_TABLE"
echo ""
echo "Next steps:"
echo "1. Check your accounts in Firefly III"
echo "2. Credit card balances should now show as negative liabilities"
echo "3. All transactions have been preserved"
echo ""
echo "To restore from backup if needed:"
echo "  mysql -u $DB_USER -p$DB_PASS $DB_NAME -e 'UPDATE accounts a JOIN $BACKUP_TABLE b ON a.id = b.id SET a.account_type_id = b.account_type_id'"
