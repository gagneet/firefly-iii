# Quick Start - Bulk Statement Upload

## 🚀 5-Minute Setup

### Step 1: Set Credentials (30 seconds)
```bash
export FIREFLY_URL="http://localhost:8080"
export FIREFLY_TOKEN="your_access_token_here"
```

### Step 2: Pre-Create Accounts (2 minutes)
```bash
cd data-importer
python3 pre_create_accounts.py $FIREFLY_URL $FIREFLY_TOKEN
```

**Expected Output:**
```
✓ All accounts ready for bulk import!
```

### Step 3: Verify (30 seconds)
```bash
python3 verify_accounts.py $FIREFLY_URL $FIREFLY_TOKEN
```

**Expected Output:**
```
✓ All required accounts exist!
```

### Step 4: Upload Statements (ongoing)

**Via Web UI:**
1. Go to Import → Statement Import
2. Select bank type + Upload PDF
3. ✓ Enable "Detect transfers"
4. ✓ Enable "Detect duplicates"
5. Click Upload

**Via Command Line:**
```bash
python3 firefly_service.py \
    amex \
    /path/to/statement.pdf \
    $FIREFLY_URL \
    $FIREFLY_TOKEN \
    1 1  # duplicates + transfers
```

---

## ✅ What's Working Now

| Before | After |
|--------|-------|
| ❌ Upload order matters | ✅ Upload in any order |
| ❌ Transfers fail | ✅ Transfers work automatically |
| ❌ Manual fixes needed | ✅ Fully automated |

---

## 📋 Accounts Created (22 total)

**Credit Cards (3):**
- AMEX-BusinessPlatinum-43006
- AMEX-CashBack-71006
- CBA-MasterCard-6233

**Loans (4):**
- CBA-HomeLoan-466297723
- CBA-HomeLoan-466297731
- CBA-HomeLoan-470379959
- CBA-PL-466953719

**Everyday Savings (11):**
- CBA-87Hoolihan-9331, CBA-EveryDayOffset-7964
- ING-Everyday-64015854, ING-Saver-45070850, ING-Saver-817278720
- uBank-86400-Gagneet1/2/3/4, uBank-86400-Avneet1/2

**India Savings (4):**
- India-ICICI-Bank, India-SBI-Account1/2, India-ING-Account

---

## 🔧 Troubleshooting

**Connection Failed:**
```bash
curl http://localhost:8080/api/v1/about
# Check if Firefly is running
```

**Token Invalid:**
```bash
curl -H "Authorization: Bearer $FIREFLY_TOKEN" \
     http://localhost:8080/api/v1/accounts
# Should return account list
```

**Transfers Still Failing:**
1. Run `verify_accounts.py` - check all accounts exist
2. Check console output during upload
3. Look for `[ACCOUNT PRE-CREATION]` messages
4. Check Firefly logs: `docker logs firefly_iii_app`

---

## 📚 Full Documentation

- **User Guide:** `data-importer/BULK_UPLOAD_GUIDE.md`
- **Technical Details:** `TRANSFER_ACCOUNT_HANDLING.md`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`

---

## 💡 Pro Tips

1. ✅ Run `pre_create_accounts.py` once before bulk upload
2. ✅ Use `verify_accounts.py` to check status anytime
3. ✅ Upload oldest statements first for better balance tracking
4. ✅ Enable both duplicate and transfer detection
5. ✅ Backup Firefly database before large imports

---

## 🎯 Success Indicators

**Look for these in console output:**

✅ Good:
```
[ACCOUNT PRE-CREATION] Found 2 unique accounts in transfers
  ✓ Pre-created account: ING-Everyday-64015854
  ✓ Pre-created account: ING-Saver-45070850
  [TRANSFER] 2023-10-15 | $1000.00 | ING-Everyday-64015854 → ING-Saver-45070850
```

❌ Bad:
```
[ERROR TRANSFER] Failed: 2023-10-15 | $1000.00 | Account1 → Account2
```

If you see errors:
1. Check account names match exactly
2. Run `verify_accounts.py`
3. Check Firefly logs for details
