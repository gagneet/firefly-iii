# Bank Statement Import Feature - User Guide

**Last Updated:** October 6, 2025
**Version:** 1.0
**Firefly III Version:** 6.4.0

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Supported Banks](#supported-banks)
4. [How to Use](#how-to-use)
5. [Technical Details](#technical-details)
6. [Troubleshooting](#troubleshooting)
7. [Files Modified/Created](#files-modifiedcreated)

---

## Overview

The Bank Statement Import feature allows you to automatically import transactions from Australian bank PDF statements directly into Firefly III. The system parses PDF statements, extracts transactions, detects duplicates and transfers, and creates them in your Firefly III instance.

**Access the feature at:**
```
https://firefly.gagneet.com/import/statement
```

Or through the Firefly III sidebar menu: **Import Bank Statement**

---

## Features

### 🏦 Supported Banks
- American Express (AMEX) - Credit card statements
- ING Orange Everyday - Transaction account
- ING Savings Maximiser - Savings account
- uBank - Transaction and savings accounts
- CommBank - Transaction accounts

### ✨ Key Capabilities

**Intelligent Duplicate Detection**
- Detects exact duplicate transactions across multiple imports
- Configurable tolerance: ±2 days, ±$0.01, 85% description similarity
- Prevents the same transaction from being imported twice

**Transfer Detection**
- Automatically identifies transfers between your own accounts
- Prevents double-counting of money moved between accounts
- Matches opposite amounts on similar dates

**Automatic Processing**
- Extracts all transactions from PDF statements
- Creates accounts automatically if they don't exist
- Applies transaction rules automatically
- Generates CSV export of imported transactions

**Error Handling**
- Detailed error messages for failed imports
- CSV download of successfully imported transactions
- Import history tracking

---

## Supported Banks

### 1. American Express (AMEX)
- **Type:** Credit Card
- **Format:** PDF Statement
- **Transactions:** Credit card purchases and payments

### 2. ING Orange Everyday
- **Type:** Transaction Account
- **Format:** PDF Statement
- **Transactions:** Debit card purchases, ATM withdrawals, direct debits, transfers

### 3. ING Savings Maximiser
- **Type:** Savings Account
- **Format:** PDF Statement
- **Transactions:** Interest payments, transfers

### 4. uBank
- **Type:** Transaction & Savings Accounts
- **Format:** PDF Statement
- **Transactions:** All transaction types

### 5. CommBank (Commonwealth Bank)
- **Type:** Transaction Account
- **Format:** PDF Statement
- **Transactions:** All transaction types

---

## How to Use

### Step 1: Access the Import Page

Navigate to:
```
https://firefly.gagneet.com/import/statement
```

Or click **"Import Bank Statement"** in the Firefly III sidebar menu.

### Step 2: Select Your Bank

Choose your bank from the dropdown menu:
- American Express (AMEX)
- ING Orange Everyday
- ING Savings Maximiser
- uBank
- CommBank

### Step 3: Upload Your PDF Statement

1. Click the file upload button
2. Select your PDF bank statement (max 10MB)
3. Only PDF files are accepted

### Step 4: Configure Options

**Detect Duplicates** (enabled by default)
- Automatically skips transactions that already exist in Firefly III
- Uses date, amount, and description matching

**Detect Transfers** (enabled by default)
- Identifies transfers between your own accounts
- Prevents double-counting of internal transfers

### Step 5: Import

Click **"Import Statement"** button

The system will:
1. Upload and parse the PDF
2. Extract all transactions
3. Check for duplicates across all accounts
4. Identify transfers between accounts
5. Create transactions in Firefly III
6. Create accounts if they don't exist
7. Apply transaction rules

### Step 6: Review Results

After import completes:
- **Success Count:** Number of transactions imported
- **Duplicate Count:** Number of duplicates skipped
- **Transfer Count:** Number of transfers detected
- **Error Count:** Number of failed transactions

**Download CSV:** Click to download a CSV file of imported transactions for your records

---

## Technical Details

### Architecture

**Frontend:**
- Vue.js 2 component
- Located in: `/resources/assets/v1/src/components/imports/StatementImport.vue`
- Compiled into: `/public/v1/js/app_vue.js`

**Backend:**
- Laravel Controller: `/app/Http/Controllers/StatementImportController.php`
- Routes:
  - `GET /import/statement` - Display import page
  - `GET /api/v1/statement-import/banks` - Get supported banks
  - `POST /api/v1/statement-import/upload` - Upload and process PDF
  - `GET /api/v1/statement-import/history` - Import history

**PDF Processing:**
- Python script: `/data-importer/parse_statements.py`
- Uses `pdfplumber` library for PDF parsing
- Bank-specific parsers for each supported bank

**Duplicate Detection:**
- Python module: `/data-importer/duplicate_detector.py`
- Algorithm parameters:
  - Date tolerance: ±2 days
  - Amount tolerance: ±$0.01
  - Description similarity: 85% threshold

**API Integration:**
- Python service: `/data-importer/firefly_service.py`
- Uses Firefly III REST API v1
- Authentication via Personal Access Token

### File Upload Limits

- Maximum file size: 10MB
- Accepted formats: PDF only
- Temporary storage: `/storage/app/temp_statements/`

### Duplicate Detection Algorithm

```
Transaction is considered duplicate if:
1. Same account
2. Date within ±2 days
3. Amount within ±$0.01
4. Description similarity ≥ 85%
```

### Transfer Detection Algorithm

```
Transfer detected if:
1. Different accounts (both owned by user)
2. Date within ±2 days
3. Opposite amounts (one positive, one negative)
4. Amount difference ≤ $0.01
```

---

## Troubleshooting

### Issue: Import button is disabled

**Cause:** Bank not selected or no file uploaded
**Solution:**
1. Select a bank from the dropdown
2. Upload a PDF file

### Issue: "Failed to load supported banks"

**Cause:** API endpoint not accessible
**Solution:**
```bash
# Check routes are registered
php artisan route:list | grep statement

# Should show:
# GET|HEAD  api/v1/statement-import/banks
# POST      api/v1/statement-import/upload
# GET|HEAD  api/v1/statement-import/history
# GET|HEAD  import/statement
```

### Issue: "Python dependencies not installed"

**Cause:** `pdfplumber` library not installed
**Solution:**
```bash
cd /home/gagneet/firefly/data-importer
pip install pdfplumber --break-system-packages
# Or
pip install pdfplumber --user
```

### Issue: Vue component not rendering

**Cause:** JavaScript not compiled or cached
**Solution:**
```bash
cd /home/gagneet/firefly/resources/assets/v1
npm run production
# Then hard refresh browser (Ctrl+Shift+R)
```

### Issue: PDF parsing fails

**Cause:** Unsupported PDF format or bank statement structure changed
**Solution:**
1. Verify PDF is from a supported bank
2. Ensure PDF is a genuine bank statement (not scanned image)
3. Check `/storage/logs/laravel.log` for detailed errors
4. Contact support with PDF sample (redact sensitive info)

### Issue: All transactions showing as duplicates

**Cause:** Transactions already exist in Firefly III
**Solution:**
- This is expected behavior if you've already imported these transactions
- Check transaction date range in Firefly III
- If truly not duplicates, check duplicate detection settings

### Check Logs

**Laravel Logs:**
```bash
tail -f /home/gagneet/firefly/storage/logs/laravel.log
```

**PHP-FPM Logs:**
```bash
tail -f /home/gagneet/firefly/storage/logs/ff3-fpm-fcgi-$(date +%Y-%m-%d).log
```

**Nginx Logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

---

## Files Modified/Created

### Created Files

**Frontend:**
```
/resources/assets/v1/src/components/imports/StatementImport.vue
/resources/views/import/statement.twig
```

**Backend:**
```
/app/Http/Controllers/StatementImportController.php
/data-importer/parse_statements.py
/data-importer/duplicate_detector.py
/data-importer/firefly_service.py
/data-importer/bank_parsers/amex_parser.py
/data-importer/bank_parsers/ing_orange_parser.py
/data-importer/bank_parsers/ing_savings_parser.py
/data-importer/bank_parsers/ubank_parser.py
/data-importer/bank_parsers/commbank_parser.py
```

**Configuration:**
```
/setup_statement_import.sh
```

**Documentation:**
```
/BANK_STATEMENT_IMPORT_GUIDE.md (this file)
```

### Modified Files

**Routes:**
```
/routes/web.php - Added import.statement.index route
/routes/api.php - Added statement-import API routes
/routes/breadcrumbs.php - Added import.statement.index breadcrumb
```

**Frontend Build:**
```
/resources/assets/v1/src/app_vue.js - Registered StatementImport component
/resources/assets/v1/webpack.mix.js - Changed Vue build to full version
```

**Menu:**
```
/resources/views/partials/menu-sidebar.twig - Added "Import Bank Statement" menu item
```

---

## Installation Summary

The feature was installed on **October 6, 2025** with the following steps:

1. ✅ Created Vue.js component for file upload
2. ✅ Created Laravel controller for handling uploads
3. ✅ Created Python PDF parser scripts
4. ✅ Implemented duplicate detection algorithm
5. ✅ Implemented transfer detection algorithm
6. ✅ Integrated with Firefly III API
7. ✅ Added routes and breadcrumbs
8. ✅ Added menu item in sidebar
9. ✅ Fixed Twig template rendering
10. ✅ Fixed Python installation (Ubuntu 24.04)
11. ✅ Fixed file permissions
12. ✅ Fixed Vue component registration
13. ✅ Fixed Vue build configuration
14. ✅ Built frontend assets
15. ✅ Cleared all caches
16. ✅ Tested end-to-end functionality

---

## Configuration

### Personal Access Token (Optional)

For enhanced security, configure a Personal Access Token:

1. Go to https://firefly.gagneet.com
2. Navigate to **Options > Profile > OAuth**
3. Click **"Create New Token"**
4. Copy the token
5. Add to `.env` file:
   ```
   FIREFLY_IMPORT_ACCESS_TOKEN=your_token_here
   ```

If not configured, the system uses the authenticated user's session.

### Duplicate Detection Tuning

To adjust duplicate detection sensitivity, modify `/data-importer/duplicate_detector.py`:

```python
detector = DuplicateDetector(
    date_tolerance_days=2,      # ±2 days (default)
    amount_tolerance=0.01,      # ±$0.01 (default)
    description_similarity_threshold=0.85  # 85% similarity (default)
)
```

---

## Future Enhancements

Potential improvements for future versions:

- [ ] Support for more Australian banks (ANZ, Westpac, NAB, etc.)
- [ ] Support for CSV file imports
- [ ] Batch import multiple PDFs at once
- [ ] Scheduled automatic imports
- [ ] Import from email attachments
- [ ] Machine learning for better duplicate detection
- [ ] Transaction categorization improvements
- [ ] Import history and statistics dashboard

---

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Firefly III Documentation](https://docs.firefly-iii.org/)
3. Check Laravel logs for detailed errors
4. Open an issue on GitHub (if applicable)

---

## Credits

**Developed for Firefly III**
**Implementation Date:** October 6, 2025
**Python Libraries:** pdfplumber, requests
**Frontend:** Vue.js 2, Bootstrap, AdminLTE
**Backend:** Laravel 12, PHP 8.4

---

## License

This feature follows Firefly III's license:
GNU Affero General Public License v3.0

---

**End of Document**
