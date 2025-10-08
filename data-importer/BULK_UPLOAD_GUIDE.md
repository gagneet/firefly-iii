# Bulk Statement Upload Guide

## Overview

This guide covers how to upload multiple bank statements to Firefly III with proper handling of transfer transactions between accounts.

## Prerequisites

1. **Firefly III installed and running**
2. **Python 3 environment**
3. **Firefly III API access token**
4. **PDF bank statements** organized by account

## Step-by-Step Process

### Step 1: Get Your Firefly III Access Token

#### Option A: Via Environment Variable
```bash
# Check if token is already configured
echo $FIREFLY_TOKEN
```

#### Option B: Generate New Token
1. Log into Firefly III
2. Go to Options → Profile → OAuth
3. Click "Create New Token"
4. Copy the token

### Step 2: Pre-Create All Accounts

**Important:** Run this BEFORE uploading any statements to ensure transfers work correctly.

```bash
cd data-importer

# Set your credentials
export FIREFLY_URL="http://your-firefly-url:8080"
export FIREFLY_TOKEN="your_access_token_here"

# Run the pre-creation script
python3 pre_create_accounts.py $FIREFLY_URL $FIREFLY_TOKEN
```

**Expected Output:**
```
================================================================================
FIREFLY III ACCOUNT PRE-CREATION
================================================================================

Firefly URL: http://localhost:8080
Total accounts to process: 22

✓ Connection successful

Credit Cards (3 accounts)
--------------------------------------------------------------------------------
  ✓ CREATED: AMEX-BusinessPlatinum-43006 (ID: 12, Type: liability (debt))
  ✓ CREATED: AMEX-CashBack-71006 (ID: 13, Type: liability (debt))
  ✓ CREATED: CBA-MasterCard-6233 (ID: 14, Type: liability (debt))

Home Loans (3 accounts)
--------------------------------------------------------------------------------
  ✓ CREATED: CBA-HomeLoan-466297723 (ID: 15, Type: liability (mortgage))
  ✓ CREATED: CBA-HomeLoan-466297731 (ID: 16, Type: liability (mortgage))
  ✓ CREATED: CBA-HomeLoan-470379959 (ID: 17, Type: liability (mortgage))

...

================================================================================
SUMMARY
================================================================================
Total accounts:    22
Created:           22
Already existed:   0
Failed:            0

✓ All accounts ready for bulk import!
```

**What This Does:**
- Creates all 22 accounts with correct types:
  - 3 Credit Cards (liability/debt)
  - 3 Home Loans (liability/mortgage)
  - 1 Personal Loan (liability/loan)
  - 11 Everyday Savings accounts (asset)
  - 4 India Savings accounts (asset)
- Checks if accounts already exist (safe to re-run)
- Reports any failures

### Step 3: Upload Bank Statements

Now you can upload statements in **any order** without worrying about transfer failures.

#### Via Web Interface

1. Go to Firefly III
2. Navigate to Import → Statement Import
3. Select bank type
4. Upload PDF
5. Enable "Detect transfers" ✓
6. Enable "Detect duplicates" ✓
7. Click Upload

#### Via Command Line (Bulk Upload)

```bash
cd data-importer

# Upload single statement
python3 firefly_service.py \
    amex \
    /path/to/statement.pdf \
    $FIREFLY_URL \
    $FIREFLY_TOKEN \
    1 \  # detect duplicates
    1    # detect transfers

# Upload all statements in a directory
for pdf in /path/to/statements/AMEX-BusinessPlatinum-43006/*.pdf; do
    echo "Processing: $pdf"
    python3 firefly_service.py amex "$pdf" $FIREFLY_URL $FIREFLY_TOKEN 1 1
    sleep 2  # Be nice to the API
done
```

**With the new transfer handling, you'll see:**
```
[ACCOUNT PRE-CREATION] Found 3 unique accounts in transfers
  ✓ Pre-created account: AMEX-CashBack-71006
  ✓ Pre-created account: ING-Everyday-64015854
  ✓ Pre-created account: ING-Saver-45070850

  [TRANSFER] 2023-10-15 |  $1000.00 | ING-Everyday-64015854 → ING-Saver-45070850
  [TRANSFER] 2023-10-20 |   $500.00 | ING-Saver-45070850 → AMEX-CashBack-71006
```

### Step 4: Verify Results

Check your Firefly III instance:

1. **Accounts page** - All accounts should be visible
2. **Transactions** - Check for transfers between accounts
3. **Reports** - Verify balances match statement closing balances

## Account List

### Accounts Pre-Created

**Credit Cards (3):**
- AMEX-BusinessPlatinum-43006 (84 statements)
- AMEX-CashBack-71006 (50 statements)
- CBA-MasterCard-6233 (56 statements)

**Home Loans (3):**
- CBA-HomeLoan-466297723 (15 statements)
- CBA-HomeLoan-466297731 (16 statements)
- CBA-HomeLoan-470379959 (4 statements)

**Personal Loans (1):**
- CBA-PL-466953719 (8 statements)

**Everyday Savings (11):**
- CBA-87Hoolihan-9331 (20 statements)
- CBA-EveryDayOffset-7964 (15 statements)
- ING-Everyday-64015854 (26 statements)
- ING-Saver-45070850 (13 statements)
- ING-Saver-817278720 (3 statements)
- uBank-86400-Gagneet1 (1 statement)
- uBank-86400-Gagneet2 (0 statements)
- uBank-86400-Gagneet3 (0 statements)
- uBank-86400-Gagneet4 (0 statements)
- uBank-86400-Avneet1 (0 statements)
- uBank-86400-Avneet2 (0 statements)

**India Savings (4):**
- India-ICICI-Bank
- India-SBI-Account1
- India-SBI-Account2
- India-ING-Account

**Total: 22 accounts**

## What's Fixed

### Before (Without Pre-Creation)

❌ **Problem:**
```
Upload: ING-Everyday-64015854.pdf
  Transaction: Transfer $1000 to ING-Saver-45070850
  ERROR: Cannot create asset account "ING-Saver-45070850"
  Result: Transfer fails ❌
```

### After (With Pre-Creation)

✅ **Solution:**
```
Step 1: Pre-create all accounts
  ✓ ING-Everyday-64015854 created
  ✓ ING-Saver-45070850 created

Step 2: Upload ING-Everyday-64015854.pdf
  Transaction: Transfer $1000 to ING-Saver-45070850
  [ACCOUNT PRE-CREATION] Found 2 unique accounts in transfers
    ✓ Pre-created account: ING-Everyday-64015854 (already exists)
    ✓ Pre-created account: ING-Saver-45070850 (already exists)
  [TRANSFER] 2023-10-15 | $1000.00 | ING-Everyday-64015854 → ING-Saver-45070850
  Result: Transfer succeeds ✅
```

## Technical Details

### Code Changes

**1. Pre-Creation Script (`pre_create_accounts.py`)**
- Creates all accounts before bulk upload
- Checks for existing accounts
- Reports detailed status

**2. Transfer Account Pre-Creation (`firefly_service.py` lines 508-526)**
```python
# Pre-create all accounts that appear in transfers to avoid creation failures
if detect_transfers and len(result['transfers']) > 0:
    transfer_accounts = set()
    for txn1, txn2 in result['transfers']:
        transfer_accounts.add(txn1.account)
        transfer_accounts.add(txn2.account)

    if transfer_accounts:
        print(f"\n[ACCOUNT PRE-CREATION] Found {len(transfer_accounts)} unique accounts in transfers")
        for account_name in sorted(transfer_accounts):
            if account_name not in stats['accounts_created']:
                account_id = self.get_or_create_account(account_name)
```

**Key Points:**
1. Extracts all unique account names from detected transfers
2. Pre-creates accounts before creating transfer transactions
3. Checks against already-created accounts to avoid duplicates
4. Reports status for each account

### Why This Works

**Firefly III's Account Creation Rules:**
- ✅ Can auto-create: Expense, Revenue accounts
- ❌ Cannot auto-create: Asset, Liability accounts

**Transfer Requirements:**
- Source: Must be Asset or Liability account
- Destination: Must be Asset or Liability account

**Problem:** Transfers require account types that can't be auto-created

**Solution:** Pre-create all accounts via API before attempting transfers

## Troubleshooting

### Issue: "Connection failed"
```bash
# Check Firefly III is running
curl http://localhost:8080/api/v1/about

# Check token is valid
curl -H "Authorization: Bearer $FIREFLY_TOKEN" \
     http://localhost:8080/api/v1/accounts
```

### Issue: "Failed to create account"
- Check account name doesn't contain invalid characters
- Verify token has write permissions
- Check Firefly III logs: `docker logs firefly_iii_app`

### Issue: Transfers still failing
- Ensure you ran `pre_create_accounts.py` first
- Check both accounts exist in Firefly III UI
- Look for error messages in console output
- Check Firefly III logs

### Issue: Duplicate transfers
- Firefly III detects duplicates via hash
- If seeing duplicates, check if running same statement twice
- Verify "Detect duplicates" is enabled

## Best Practices

1. **Always run pre-creation script first**
2. **Keep statements organized by account**
3. **Upload chronologically (oldest first)** for better balance tracking
4. **Enable both duplicate and transfer detection**
5. **Check results after each batch**
6. **Keep backups** of Firefly III database before large imports

## Support

For issues or questions:
1. Check `TRANSFER_ACCOUNT_HANDLING.md` for technical details
2. Review Firefly III logs
3. Check Python script output for error messages
4. Verify API token and permissions

## References

- **Main documentation:** `TRANSFER_ACCOUNT_HANDLING.md`
- **Firefly III API docs:** https://api-docs.firefly-iii.org/
- **Statement parser:** `statement_parser.py`
- **Firefly service:** `firefly_service.py`
