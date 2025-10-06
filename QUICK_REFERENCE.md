# Quick Reference Card - Bank Statement Import

## 🚀 Quick Start

```bash
# 1. Run setup (one time only)
cd /home/gagneet/firefly
./setup_statement_import.sh

# 2. Access the feature
# Go to: https://firefly.gagneet.com
# Click: "Import Bank Statement" in sidebar
```

## 📍 URLs

| What | URL |
|------|-----|
| **Web UI** | https://firefly.gagneet.com/import/statement |
| **Direct link** | Sidebar → "Import Bank Statement" |

## 🏦 Supported Banks

- ✅ American Express (AMEX)
- ✅ ING Orange Everyday
- ✅ ING Savings Maximiser
- ✅ uBank Spend Account
- ✅ Commonwealth Bank

## 🔧 Setup Commands

```bash
# Install Python dependencies
pip install pdfplumber

# Build frontend
cd /home/gagneet/firefly/resources/assets/v1
npm run production

# Clear caches
cd /home/gagneet/firefly
php artisan route:clear
php artisan view:clear
php artisan config:clear

# Restart
sudo systemctl restart php8.4-fpm
```

## 🎯 Usage Steps

1. **Select bank** from dropdown
2. **Upload PDF** (max 10MB)
3. **Configure options**:
   - ✅ Detect duplicates
   - ✅ Detect transfers
4. **Click "Import Statement"**
5. **Review results**

## 📊 What It Does

✅ **Extracts** all transactions from PDF
✅ **Categorizes** automatically
✅ **Creates accounts** if missing
✅ **Skips duplicates** (same transaction twice)
✅ **Detects transfers** (between your accounts)
✅ **Imports** to Firefly III via API

## 🔍 Duplicate Detection

**Exact Duplicates:**
- Same account + dates ±2 days + amount ±$0.01 + 85%+ description match
- → Second one skipped

**Transfers:**
- Different accounts + opposite amounts + close dates + "transfer" keywords
- → Combined into single transfer

## 📁 Key Files

```
Frontend:
  /resources/assets/v1/src/components/imports/StatementImport.vue

Backend:
  /app/Http/Controllers/StatementImportController.php

Python:
  /home/gagneet/firefly/data-importer/firefly_service.py
  /home/gagneet/firefly/data-importer/duplicate_detector.py
```

## 🐛 Troubleshooting

**Menu not showing?**
```bash
php artisan view:clear
sudo systemctl restart php8.4-fpm
```

**Upload fails?**
```bash
tail -f storage/logs/laravel.log
```

**Python error?**
```bash
cd data-importer
pip install pdfplumber
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| `STATEMENT_IMPORT_FEATURE.md` | Full feature docs |
| `FLASK_VS_INTEGRATED_COMPARISON.md` | Flask app comparison |
| `FINAL_IMPLEMENTATION_SUMMARY.md` | Complete summary |
| `data-importer/QUICKSTART.md` | 5-min getting started |
| `data-importer/README.md` | Detailed docs |

## 🔐 Security

**Access Token (Optional):**
```bash
# Get from: Options → Profile → OAuth → Create Token
nano .env
# Add: FIREFLY_IMPORT_ACCESS_TOKEN=your_token
sudo systemctl restart php8.4-fpm
```

Or let the system auto-generate tokens for authenticated users.

## 📝 Command Line Options

```bash
cd /home/gagneet/firefly/data-importer

# Test single statement
./test_import.sh amex ~/Downloads/statement.pdf

# Convert to CSV only
python convert_to_firefly_csv.py amex statement.pdf

# Direct import
python firefly_service.py amex statement.pdf https://firefly.gagneet.com token

# Batch import multiple PDFs
python convert_to_firefly_csv.py --batch ~/statements/
```

## ✅ Verification

**Check routes:**
```bash
php artisan route:list | grep statement
```

Expected output:
```
GET  /import/statement
GET  /api/v1/statement-import/banks
POST /api/v1/statement-import/upload
GET  /api/v1/statement-import/history
```

**Test parser:**
```bash
cd data-importer
python test_parser.py amex test.pdf
```

## 🎯 Expected Results

**Successful Import:**
```
✅ Total transactions: 127
✅ Successfully imported: 116
✅ Transfers detected: 4
✅ Duplicates skipped: 3
✅ Errors: 0
```

## 🆘 Quick Help

**Issue**: Can't find menu item
**Fix**: Clear view cache, restart PHP-FPM

**Issue**: Upload fails
**Fix**: Check logs, verify token, test Python script

**Issue**: No transactions imported
**Fix**: Verify bank type, check PDF format, test parser directly

**Issue**: Too many duplicates
**Fix**: Adjust tolerances in `duplicate_detector.py`

## 📞 Support

1. Check documentation first
2. Review Laravel logs: `storage/logs/laravel.log`
3. Test Python scripts directly
4. Check Firefly III API logs

---

**Quick Setup**: `./setup_statement_import.sh`
**Quick Access**: https://firefly.gagneet.com → Import Bank Statement
**Quick Test**: Upload a PDF and see the magic! ✨
