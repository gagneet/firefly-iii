#!/usr/bin/env python3
"""
Bulk Import Script for All Bank Statements
Imports all PDFs from /home/gagneet/home-expenses/uploads/
"""

import sys
import os
from pathlib import Path
from datetime import datetime
sys.path.insert(0, '/home/gagneet/firefly/data-importer')

from firefly_service import FireflyService, process_pdf_and_import

# Configuration
FIREFLY_URL = 'https://firefly.gagneet.com'
UPLOADS_DIR = Path('/home/gagneet/home-expenses/uploads')

# Bank type mapping
BANK_MAPPING = {
    'AMEX-BusinessPlatinum-43006': 'amex',
    'AMEX-CashBack-71006': 'amex',
    'CBA-87Hoolihan-9331': 'commbank_offset',
    'CBA-EveryDayOffset-7964': 'commbank_offset',
    'CBA-HomeLoan-466297723': 'commbank_homeloan',
    'CBA-HomeLoan-466297731': 'commbank_homeloan',
    'CBA-HomeLoan-470379959': 'commbank_homeloan',
    'CBA-MasterCard-6233': 'commbank',
    'CBA-PL-466953719': 'commbank_homeloan',
    'ING-Everyday-64015854': 'ing_orange',
    'ING-Saver-45070850': 'ing_savings',
    'ING-Saver-817278720': 'ing_savings',
    'uBank-86400-Gagneet': 'ubank',
}

def get_access_token():
    """Get Firefly III access token from user environment"""
    # Try to get from environment variable or config file
    token_file = Path.home() / '.firefly_token'
    if token_file.exists():
        return token_file.read_text().strip()
    
    # Fallback: get from user
    token = input("Enter your Firefly III Personal Access Token: ").strip()
    return token

def main():
    print("="*80)
    print("FIREFLY III BULK IMPORT - ALL STATEMENTS")
    print("="*80)
    print()
    
    # Get access token
    token = get_access_token()
    if not token:
        print("ERROR: No access token provided")
        sys.exit(1)
    
    # Test connection
    service = FireflyService(FIREFLY_URL, token)
    print("Testing connection to Firefly III...")
    if not service.test_connection():
        print("ERROR: Cannot connect to Firefly III")
        sys.exit(1)
    print("✓ Connected successfully\n")
    
    # Collect all PDFs
    all_files = []
    for subdir_name, bank_type in BANK_MAPPING.items():
        subdir = UPLOADS_DIR / subdir_name
        if subdir.exists():
            pdf_files = sorted(subdir.glob('*.pdf'))
            for pdf_file in pdf_files:
                all_files.append((pdf_file, bank_type, subdir_name))
    
    print(f"Found {len(all_files)} PDF files to import\n")
    
    # Summary statistics
    stats = {
        'total_files': len(all_files),
        'processed': 0,
        'success': 0,
        'failed': 0,
        'total_transactions': 0,
        'total_created': 0,
        'total_duplicates': 0,
        'total_transfers': 0,
        'total_errors': 0,
        'accounts_created': set(),
        'failed_files': []
    }
    
    # Process each file
    start_time = datetime.now()
    
    for idx, (pdf_file, bank_type, account_dir) in enumerate(all_files, 1):
        print(f"\n[{idx}/{len(all_files)}] Processing: {account_dir}/{pdf_file.name}")
        print(f"  Bank type: {bank_type}")
        
        try:
            result = process_pdf_and_import(
                str(pdf_file),
                bank_type,
                FIREFLY_URL,
                token,
                detect_duplicates=True,
                detect_transfers=True
            )
            
            stats['processed'] += 1
            
            if 'error' in result:
                print(f"  ✗ ERROR: {result['error']}")
                stats['failed'] += 1
                stats['failed_files'].append(str(pdf_file))
            else:
                stats['success'] += 1
                stats['total_transactions'] += result.get('total', 0)
                stats['total_created'] += result.get('created', 0)
                stats['total_duplicates'] += result.get('duplicates', 0)
                stats['total_transfers'] += result.get('transfers', 0)
                stats['total_errors'] += result.get('errors', 0)
                
                for account in result.get('accounts_created', []):
                    stats['accounts_created'].add(account)
                
                print(f"  ✓ Success: {result['created']} created, {result['duplicates']} duplicates, {result['errors']} errors")
        
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            stats['failed'] += 1
            stats['failed_files'].append(str(pdf_file))
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*80)
    print("IMPORT COMPLETE")
    print("="*80)
    print(f"Duration: {duration}")
    print()
    print("FILES:")
    print(f"  Total: {stats['total_files']}")
    print(f"  Processed: {stats['processed']}")
    print(f"  Success: {stats['success']}")
    print(f"  Failed: {stats['failed']}")
    print()
    print("TRANSACTIONS:")
    print(f"  Total found: {stats['total_transactions']}")
    print(f"  Created: {stats['total_created']}")
    print(f"  Duplicates: {stats['total_duplicates']}")
    print(f"  Transfers: {stats['total_transfers']}")
    print(f"  Errors: {stats['total_errors']}")
    print()
    print(f"ACCOUNTS CREATED: {len(stats['accounts_created'])}")
    for account in sorted(stats['accounts_created']):
        print(f"  - {account}")
    
    if stats['failed_files']:
        print()
        print(f"FAILED FILES ({len(stats['failed_files'])}):")
        for failed_file in stats['failed_files'][:10]:  # Show first 10
            print(f"  - {failed_file}")
        if len(stats['failed_files']) > 10:
            print(f"  ... and {len(stats['failed_files']) - 10} more")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
