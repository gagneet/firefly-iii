# Firefly III Data Importer with Australian Bank PDF Parser

This setup includes the official Firefly III Data Importer with custom Python parsers for Australian bank statement PDFs.

## Overview

**What's Included:**
- 🐳 Dockerized Firefly III Data Importer
- 🇦🇺 Australian bank statement parsers (AMEX, ING, uBank, CommBank)
- 📄 PDF to CSV conversion tool
- 🏷️ Auto-categorization of transactions
- 📊 Firefly III compatible CSV format

**Supported Banks:**
- American Express (AMEX)
- ING Orange Everyday
- ING Savings Maximiser
- uBank Spend Account
- Commonwealth Bank

## Installation

### 1. Install Python Dependencies

```bash
cd /home/gagneet/firefly/data-importer
pip install -r requirements.txt
```

### 2. Start the Data Importer

The Data Importer is already running via Docker:

```bash
docker ps | grep firefly_importer
```

**Access the Data Importer:**
- URL: http://localhost:8081
- Alternative: http://firefly.gagneet.com:8081 (if configured)

### 3. Configure Authentication

You need to create a Personal Access Token in Firefly III:

1. Log into Firefly III at https://firefly.gagneet.com
2. Go to **Options > Profile > OAuth**
3. Click **Create New Token**
4. Give it a name like "Data Importer"
5. Copy the generated token
6. Edit `.importer.env` and set:
   ```
   FIREFLY_III_ACCESS_TOKEN=your_token_here
   ```
7. Restart the importer:
   ```bash
   cd /home/gagneet/firefly/data-importer
   docker compose restart
   ```

## Usage

### Converting Bank Statements to CSV

#### Single Statement Conversion

```bash
cd /home/gagneet/firefly/data-importer
python convert_to_firefly_csv.py <bank_type> <pdf_file> [output_csv]
```

**Examples:**

```bash
# AMEX statement
python convert_to_firefly_csv.py amex ~/Downloads/amex_april_2025.pdf

# ING Orange Everyday
python convert_to_firefly_csv.py ing_orange ~/Downloads/ing_statement.pdf

# ING Savings Maximiser
python convert_to_firefly_csv.py ing_savings ~/Downloads/ing_savings.pdf

# uBank
python convert_to_firefly_csv.py ubank ~/Downloads/ubank_statement.pdf

# CommBank
python convert_to_firefly_csv.py commbank ~/Downloads/commbank_statement.pdf
```

This will create `firefly_import.csv` in the current directory.

#### Batch Conversion

To convert multiple PDFs at once:

```bash
# Place all PDFs in a directory
python convert_to_firefly_csv.py --batch ~/Downloads/statements/
```

**Note:** For batch conversion, the script tries to detect the bank type from the filename. Make sure your PDF filenames contain bank identifiers like:
- `amex_april_2025.pdf`
- `ing_orange_statement.pdf`
- `ubank_january_2025.pdf`

### Importing to Firefly III

#### Method 1: Web Interface (Recommended)

1. Convert your PDF to CSV (see above)
2. Copy the CSV to the import directory:
   ```bash
   cp firefly_import.csv /home/gagneet/firefly/data-importer/import/
   ```
3. Open the Data Importer: http://localhost:8081
4. Click **Start a new import**
5. Select **Upload a CSV file**
6. Upload your `firefly_import.csv`
7. Configure import settings:
   - Map columns (should auto-detect)
   - Choose your source account
   - Set import rules
8. Review transactions and click **Import**

#### Method 2: Automated Import (Advanced)

For automated imports via cron or API:

```bash
# Set up auto-import configuration
curl -X POST http://localhost:8081/autoimport \
  -H "Authorization: Bearer 9cd7fe796b5a35c6717eb1c014ae69180e3e4c71c4b7c73b6e28843fa8b7b34f" \
  -F "file=@firefly_import.csv"
```

## Auto-Categorization

The parser includes built-in categorization rules:

| Category | Keywords |
|----------|----------|
| Groceries | woolworths, coles, aldi, iga, costco, supermarket |
| Dining Out | restaurant, cafe, pizza, sushi, chicken, indian, chinese |
| Utilities | origin energy, electricity, gas, water, internet |
| Transport | petrol, fuel, parking, uber, toll |
| Shopping | ikea, kmart, target, myer, temu |
| Income | salary, wage, pay, deposit (positive amounts) |
| Transfer | transfer, payment to, payment from |

**Customize Categories:**

Edit `statement_parser.py` and modify the `categorize_transaction()` method to add your own rules.

## CSV Format

The converter creates Firefly III compatible CSV files with these columns:

```csv
date,description,amount,source-name,destination-name,currency-code,category-name,budget-name,bill-name,tags,notes,internal-reference,external-id
```

**Transaction Logic:**
- **Expenses** (negative amounts): `source = your account`, `destination = merchant`
- **Income** (positive amounts): `source = payer`, `destination = your account`
- **Transfers**: Both source and destination are your accounts

## File Structure

```
data-importer/
├── docker-compose.yml          # Docker Compose configuration
├── .importer.env               # Data Importer environment variables
├── statement_parser.py         # Bank statement PDF parsers
├── convert_to_firefly_csv.py   # CSV converter for Firefly III
├── requirements.txt            # Python dependencies
├── import/                     # Place CSV files here for import
├── configurations/             # Import configurations (auto-saved)
└── README.md                   # This file
```

## Troubleshooting

### Data Importer Won't Start

Check logs:
```bash
docker logs firefly_importer
```

Restart the container:
```bash
cd /home/gagneet/firefly/data-importer
docker compose down
docker compose up -d
```

### Authentication Errors

Make sure you've set the Personal Access Token in `.importer.env`:
```bash
FIREFLY_III_ACCESS_TOKEN=your_token_here
```

### PDF Parsing Issues

If the parser can't extract transactions:
1. Open the PDF in a viewer and check the format
2. The parser uses regex patterns specific to each bank
3. You may need to adjust the patterns in `statement_parser.py`
4. Run the parser in debug mode:
   ```bash
   python -c "from statement_parser import StatementParser; parser = StatementParser(); print(parser.parse_statement('statement.pdf', 'amex'))"
   ```

### Duplicate Transactions

Firefly III has built-in duplicate detection, but you can:
1. Set `IGNORE_DUPLICATE_ERRORS=true` in `.importer.env`
2. Use transaction external IDs for better tracking
3. Check date ranges before importing

## Advanced Configuration

### Custom Import Rules

Create import configurations in the Data Importer UI and save them. These are stored in `configurations/` and can be reused.

### Webhook Integration

Set up webhooks in Firefly III to trigger actions after imports:
1. Enable webhooks: `ALLOW_WEBHOOKS=true` in Firefly III `.env`
2. Create webhook triggers in Firefly III
3. Configure webhook URLs in Data Importer

### Scheduled Imports

Create a cron job for automated imports:

```bash
# Add to crontab
0 9 * * * cd /home/gagneet/firefly/data-importer && python convert_to_firefly_csv.py --batch /path/to/statements/ && docker exec firefly_importer php artisan importer:auto-import
```

## Security Notes

🔒 **Important Security Considerations:**

1. **Tokens**: The `AUTO_IMPORT_SECRET` and `FIREFLY_III_ACCESS_TOKEN` are sensitive. Keep `.importer.env` secure.
2. **PDF Files**: Statement PDFs contain sensitive financial data. Delete them after import.
3. **Network**: The Data Importer runs on port 8081. Consider using a reverse proxy with HTTPS.
4. **Access**: Restrict access to the import directory to authorized users only.

## Australian Banking Notes

### Direct Bank Connections

❌ **Not Supported:**
- GoCardless: Limited Australian bank support
- SaltEdge: Free tier discontinued (Oct 2025)

✅ **Alternatives:**
- Use this PDF parser for offline imports
- Check if your bank works with SimpleFIN
- Use Up Bank's third-party importers if applicable

### Open Banking (CDR)

Australia has the Consumer Data Right (CDR) framework, but integration requires:
- Accredited Data Recipient status
- Direct agreement with banks
- Not currently available for personal use via GoCardless/SaltEdge

### Best Practice

Download statements monthly and batch import using the `--batch` flag.

## Support

For issues with:
- **Data Importer**: https://github.com/firefly-iii/data-importer/issues
- **Firefly III**: https://github.com/firefly-iii/firefly-iii/issues
- **This Parser**: Contact your system administrator

## License

- Firefly III: AGPL-3.0
- Data Importer: AGPL-3.0
- Custom parsers: Use at your own risk

---

**Last Updated**: October 2025
**Data Importer Version**: latest
**Firefly III**: https://firefly.gagneet.com
