# Australian Bank Statement Import Feature

## 🎉 Feature Complete

I've built a complete PDF bank statement import system with duplicate detection, directly integrated into your Firefly III installation at `https://firefly.gagneet.com`.

## ✨ Features

### 1. **Web UI for PDF Upload**
- Upload bank statements directly through Firefly III's web interface
- No need to use command line or external tools
- Real-time progress tracking and results display

### 2. **Supported Australian Banks**
- American Express (AMEX)
- ING Orange Everyday
- ING Savings Maximiser
- uBank Spend Account
- Commonwealth Bank

### 3. **Intelligent Duplicate Detection**
- **Exact Duplicates**: Detects the same transaction appearing multiple times
  - Matches on: same account, similar dates (±2 days), same amount, similar descriptions (85%+ match)

- **Transfer Detection**: Identifies money moving between YOUR accounts
  - Detects opposite amounts, different accounts, close dates, "transfer" keywords
  - Example: $2,500 debit from ING Orange → $2,500 credit to ING Savings

- **Customizable Tolerances**:
  - Date tolerance (default 2 days) - handles processing delays
  - Amount tolerance ($0.01) - handles rounding differences
  - Description similarity (85%) - handles slight variations

### 4. **Automatic Features**
- **Auto-categorization**: Groceries, Dining, Utilities, Transport, Shopping, etc.
- **Account creation**: Creates accounts if they don't exist
- **Transaction creation**: Directly creates transactions via Firefly III API
- **Duplicate skipping**: Automatically skips transactions that already exist

## 📍 Location

### New Menu Item
**Firefly III → Import Bank Statement**

Located in the sidebar menu, just below "Export Data" (if visible) and above "Options".

### Direct URL
```
https://firefly.gagneet.com/import/statement
```

## 🚀 How to Use

### Step 1: Access the Import Page
1. Log into Firefly III at https://firefly.gagneet.com
2. Click **"Import Bank Statement"** in the left sidebar menu
3. You'll see the upload interface

### Step 2: Upload Your Statement
1. **Select Your Bank** from the dropdown
   - Choose: AMEX, ING Orange, ING Savings, uBank, or CommBank

2. **Choose Your PDF File**
   - Click "Browse" or drag and drop
   - Max file size: 10MB
   - Only PDF format accepted

3. **Configure Options** (both enabled by default):
   - ✅ **Detect and skip duplicate transactions**
   - ✅ **Detect transfers between your accounts**

4. **Click "Import Statement"**

### Step 3: Review Results
The system will show you:
- Total transactions found
- Successfully imported
- Duplicates skipped
- Transfers detected
- Any errors encountered

## 🔧 Technical Architecture

### Frontend
- **Location**: `/resources/assets/v1/src/components/imports/StatementImport.vue`
- **Technology**: Vue.js 2 component
- **Features**:
  - File upload with validation
  - Real-time progress tracking
  - Results display with statistics
  - Error handling

### Backend
- **Controller**: `/app/Http/Controllers/StatementImportController.php`
- **Routes**:
  - Web: `/import/statement` (view)
  - API: `/api/v1/statement-import/upload` (upload endpoint)
  - API: `/api/v1/statement-import/banks` (get supported banks)

### Python Processing
- **Parser**: `/home/gagneet/firefly/data-importer/statement_parser.py`
  - Extracts transactions from PDF statements
  - Bank-specific parsing logic for each supported bank

- **Duplicate Detector**: `/home/gagneet/firefly/data-importer/duplicate_detector.py`
  - Detects exact duplicates
  - Identifies transfers between accounts
  - Configurable matching tolerances

- **Firefly Service**: `/home/gagneet/firefly/data-importer/firefly_service.py`
  - Interfaces with Firefly III API
  - Creates transactions and accounts
  - Handles authentication

### Integration Flow
```
User uploads PDF
    ↓
Laravel Controller receives file
    ↓
Calls Python service
    ↓
Python parses PDF → Extracts transactions
    ↓
Duplicate Detector analyzes transactions
    ↓
Firefly Service creates transactions via API
    ↓
Results returned to user
```

## 📊 Duplicate Detection Details

### How It Works

**1. Exact Duplicate Detection**
```python
# Matches on all these criteria:
- Same account
- Dates within 2 days
- Same amount (±$0.01)
- Description 85%+ similar
```

**Example:**
```
Transaction 1: 2025-04-05 | Woolworths Belconnen | -$49.66 | AMEX
Transaction 2: 2025-04-05 | Woolworths Belconnen | -$49.66 | AMEX
→ DUPLICATE - Second one skipped
```

**2. Transfer Detection**
```python
# Identifies transfers when:
- Different accounts
- Opposite amounts (one negative, one positive)
- Dates within 2 days
- Description mentions "transfer" or references account names
```

**Example:**
```
Transaction 1: 2025-04-03 | Transfer to Savings | -$2500.00 | ING Orange
Transaction 2: 2025-04-03 | From Orange Everyday | +$2500.00 | ING Savings
→ TRANSFER DETECTED - Created as single transfer transaction
```

### Customizing Detection

Edit `/home/gagneet/firefly/data-importer/duplicate_detector.py`:

```python
# Stricter detection (must match exactly)
detector = DuplicateDetector(
    date_tolerance_days=0,      # Same day only
    amount_tolerance=0.00,      # Exact amount
    description_similarity_threshold=0.95  # 95% match required
)

# Looser detection (more forgiving)
detector = DuplicateDetector(
    date_tolerance_days=5,      # Within 5 days
    amount_tolerance=0.50,      # ±$0.50
    description_similarity_threshold=0.70  # 70% match is enough
)
```

## 🔐 Security & Authentication

### Access Token Required

The system needs a Personal Access Token to create transactions via the Firefly III API.

**To Configure:**

1. Go to https://firefly.gagneet.com
2. Navigate to **Options → Profile → OAuth**
3. Click **"Create New Token"**
4. Name it "Statement Import"
5. Copy the token

**Option A: Add to environment (recommended):**
```bash
nano /home/gagneet/firefly/.env
```
Add this line:
```
FIREFLY_IMPORT_ACCESS_TOKEN=your_token_here
```
Restart PHP-FPM:
```bash
sudo systemctl restart php8.4-fpm
```

**Option B: Auto-generation:**
The system will automatically create a token for authenticated users if none exists.

### Security Features
- File upload validation (PDF only, max 10MB)
- User authentication required
- API token validation
- Temporary file cleanup after processing
- No sensitive data stored in logs

## 📁 File Locations

### Frontend Files
```
/home/gagneet/firefly/
├── resources/assets/v1/src/components/imports/
│   └── StatementImport.vue              # Vue.js upload component
├── resources/views/import/
│   └── statement.blade.php              # Blade view template
└── resources/views/partials/
    └── menu-sidebar.twig                 # Menu (added import link)
```

### Backend Files
```
/home/gagneet/firefly/
├── app/Http/Controllers/
│   └── StatementImportController.php    # Laravel controller
├── routes/
│   ├── web.php                          # Added web routes
│   └── api.php                          # Added API routes
└── storage/app/temp_statements/         # Temporary upload directory
```

### Python Processing Files
```
/home/gagneet/firefly/data-importer/
├── statement_parser.py                  # PDF parsing
├── duplicate_detector.py                # Duplicate detection
├── firefly_service.py                   # Firefly III API integration
├── convert_to_firefly_csv.py            # CSV converter (CLI tool)
├── requirements.txt                      # Python dependencies
└── README.md                            # Full documentation
```

## 🎯 Next Steps

### 1. Install Python Dependencies (Required)
```bash
cd /home/gagneet/firefly/data-importer
pip install pdfplumber
```

### 2. Configure Access Token
Follow the instructions in the **Security & Authentication** section above.

### 3. Build Frontend Assets
```bash
cd /home/gagneet/firefly/resources/assets/v1
npm install
npm run production
```

### 4. Clear Laravel Caches
```bash
cd /home/gagneet/firefly
php artisan route:clear
php artisan view:clear
php artisan config:clear
php artisan cache:clear
```

### 5. Test the Feature
1. Go to https://firefly.gagneet.com
2. Look for "Import Bank Statement" in the sidebar
3. Try uploading a test PDF statement

## 🐛 Troubleshooting

### Menu Item Not Showing
```bash
cd /home/gagneet/firefly
php artisan view:clear
php artisan route:clear
```

### Python Module Not Found
```bash
cd /home/gagneet/firefly/data-importer
pip install -r requirements.txt
```

### Upload Fails with 500 Error
Check Laravel logs:
```bash
tail -f /home/gagneet/firefly/storage/logs/laravel.log
```

Check Python script:
```bash
cd /home/gagneet/firefly/data-importer
python3 firefly_service.py amex /path/to/test.pdf https://firefly.gagneet.com your_token
```

### Access Token Issues
1. Check if token is configured in `.env`
2. Verify token is valid in Firefly III (Options → Profile → OAuth)
3. Check controller can access the token

### PDF Parsing Errors
Test the parser directly:
```bash
cd /home/gagneet/firefly/data-importer
python3 test_parser.py amex /path/to/statement.pdf
```

## 📚 Additional Documentation

- **Quick Start**: `/home/gagneet/firefly/data-importer/QUICKSTART.md`
- **Full Documentation**: `/home/gagneet/firefly/data-importer/README.md`
- **Installation Summary**: `/home/gagneet/firefly/data-importer/INSTALLATION_SUMMARY.md`

## 🔄 Alternative: Command Line Import

If you prefer command-line tools, you can still use:

```bash
cd /home/gagneet/firefly/data-importer

# Single statement
python convert_to_firefly_csv.py amex statement.pdf

# Batch import
python convert_to_firefly_csv.py --batch ~/statements/

# Direct API import
python firefly_service.py amex statement.pdf https://firefly.gagneet.com your_token
```

## 🎨 Customization

### Add More Banks
Edit `/home/gagneet/firefly/data-importer/statement_parser.py` and add a new parser class.

### Customize Categories
Edit the `categorize_transaction()` method in `statement_parser.py`.

### Adjust Duplicate Detection
Modify parameters in `duplicate_detector.py`.

### Change UI Styling
Edit `/home/gagneet/firefly/resources/assets/v1/src/components/imports/StatementImport.vue`.

## 📊 Statistics & Reporting

After import, the system shows:
- **Total transactions**: Count from PDF
- **Successfully imported**: New transactions created
- **Transfers detected**: Internal transfers identified
- **Duplicates skipped**: Transactions already in system
- **Errors**: Any failures during import

## 🌟 Benefits

1. **Time Saving**: Import months of transactions in seconds
2. **Accuracy**: Automatic parsing reduces manual entry errors
3. **Intelligence**: Duplicate detection prevents double-counting
4. **Convenience**: No need to export/import CSV files manually
5. **Integration**: Seamlessly integrated into Firefly III UI

---

**Created**: October 2025
**System**: Firefly III at https://firefly.gagneet.com
**Location**: /home/gagneet/firefly/
**Python Scripts**: /home/gagneet/firefly/data-importer/
