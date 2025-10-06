# Quick Start Guide

Get started with importing Australian bank statements in 5 minutes!

## Step 1: Install Dependencies

```bash
cd /home/gagneet/firefly/data-importer
pip install pdfplumber
```

## Step 2: Get Your Personal Access Token

1. Open https://firefly.gagneet.com
2. Login to your account
3. Go to **Options** → **Profile** → **OAuth**
4. Click **Create New Token**
5. Name it "Data Importer"
6. Copy the token

## Step 3: Configure the Importer

```bash
nano .importer.env
```

Find this line:
```
FIREFLY_III_ACCESS_TOKEN=
```

Paste your token:
```
FIREFLY_III_ACCESS_TOKEN=your_copied_token_here
```

Save and exit (Ctrl+X, Y, Enter)

Restart the importer:
```bash
docker compose restart
```

## Step 4: Convert Your Bank Statement

Choose your bank and run the converter:

**AMEX:**
```bash
python convert_to_firefly_csv.py amex ~/Downloads/amex_statement.pdf
```

**ING Orange:**
```bash
python convert_to_firefly_csv.py ing_orange ~/Downloads/ing_statement.pdf
```

**ING Savings:**
```bash
python convert_to_firefly_csv.py ing_savings ~/Downloads/ing_savings.pdf
```

**uBank:**
```bash
python convert_to_firefly_csv.py ubank ~/Downloads/ubank_statement.pdf
```

**CommBank:**
```bash
python convert_to_firefly_csv.py commbank ~/Downloads/commbank_statement.pdf
```

This creates `firefly_import.csv`

## Step 5: Import to Firefly III

**Option A: Web Interface (Easy)**

1. Open http://localhost:8081
2. Click **Start a new import**
3. Choose **Upload a CSV file**
4. Upload `firefly_import.csv`
5. Follow the wizard
6. Review and import!

**Option B: Copy to Import Folder**

```bash
cp firefly_import.csv import/
```

Then use the web interface to select it.

## That's It! 🎉

Your transactions are now in Firefly III.

## Tips

**Multiple statements?** Convert them all at once:
```bash
python convert_to_firefly_csv.py --batch ~/Downloads/statements/
```

**Check what's running:**
```bash
docker ps | grep firefly
```

**View importer logs:**
```bash
docker logs firefly_importer
```

**Stop the importer:**
```bash
docker compose down
```

**Start the importer:**
```bash
docker compose up -d
```

## Need Help?

See the full [README.md](README.md) for:
- Troubleshooting
- Advanced configuration
- Custom categorization rules
- Automated imports
- Security best practices
