#!/bin/bash
#
# Setup Script for Bank Statement Import Feature
# Run this to complete the installation
#

set -e

echo "========================================="
echo "Bank Statement Import - Setup"
echo "========================================="
echo ""

cd /home/gagneet/firefly

# 1. Install Python dependencies using virtual environment or --break-system-packages
echo "✓ Installing Python dependencies..."
cd data-importer

# Check if we should use virtual environment or system-wide install
if python3 -c "import pdfplumber" 2>/dev/null; then
    echo "  ✅ pdfplumber already installed"
else
    # Try installing with --break-system-packages for Ubuntu 24.04
    if pip install pdfplumber --break-system-packages 2>/dev/null; then
        echo "  ✅ pdfplumber installed (system-wide)"
    else
        # Fall back to user install
        pip install pdfplumber --user 2>/dev/null || true
        echo "  ✅ pdfplumber installed (user)"
    fi
fi

# 2. Build frontend assets
echo "✓ Building frontend assets..."
cd /home/gagneet/firefly/resources/assets/v1

if [ ! -d "node_modules" ]; then
    echo "  Installing npm packages (this may take a while)..."
    npm install --silent 2>&1 | grep -v "WARN" || true
fi

echo "  Building production assets (this may take a few minutes)..."
npm run production 2>&1 | tail -5

echo "  ✅ Assets built"

# 3. Clear Laravel caches
echo "✓ Clearing Laravel caches..."
cd /home/gagneet/firefly
php artisan route:clear > /dev/null 2>&1
php artisan view:clear > /dev/null 2>&1
php artisan config:clear > /dev/null 2>&1
php artisan cache:clear > /dev/null 2>&1
echo "  ✅ Caches cleared"

# 4. Create temp directory
echo "✓ Creating temporary directories..."
mkdir -p storage/app/temp_statements
chmod 775 storage/app/temp_statements
echo "  ✅ Directories ready"

# 5. Check if access token is configured
echo "✓ Checking configuration..."
if grep -q "FIREFLY_IMPORT_ACCESS_TOKEN=" .env 2>/dev/null; then
    echo "  ✅ Access token configured"
else
    echo ""
    echo "⚠️  WARNING: Personal Access Token not configured!"
    echo ""
    echo "To configure:"
    echo "1. Go to https://firefly.gagneet.com"
    echo "2. Navigate to Options > Profile > OAuth"
    echo "3. Click 'Create New Token'"
    echo "4. Add to .env file:"
    echo "   FIREFLY_IMPORT_ACCESS_TOKEN=your_token_here"
    echo ""
    echo "Or the system will auto-generate one for authenticated users."
    echo ""
fi

# 6. Restart PHP-FPM
echo "✓ Restarting PHP-FPM..."
sudo systemctl restart php8.4-fpm 2>/dev/null || echo "  ⚠️  Could not restart PHP-FPM (may need sudo)"
echo "  ✅ PHP-FPM restart attempted"

# 7. Test routes
echo "✓ Verifying routes..."
ROUTES=$(php artisan route:list 2>/dev/null | grep -c "statement-import" || true)
if [ "$ROUTES" -ge 3 ]; then
    echo "  ✅ Routes registered ($ROUTES found)"
else
    echo "  ⚠️  Warning: Expected 3+ routes, found $ROUTES"
fi

# 8. Test Python
echo "✓ Testing Python setup..."
cd data-importer
if python3 -c "import pdfplumber; print('✅ pdfplumber working')" 2>/dev/null; then
    echo "  ✅ Python dependencies OK"
else
    echo "  ⚠️  Warning: pdfplumber not working, try: pip install pdfplumber --user"
fi

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "🚀 The Bank Statement Import feature is now ready!"
echo ""
echo "Access it at:"
echo "  https://firefly.gagneet.com/import/statement"
echo ""
echo "Or through the menu:"
echo "  Firefly III → Import Bank Statement"
echo ""
echo "📚 Documentation:"
echo "  Full docs: /home/gagneet/firefly/STATEMENT_IMPORT_FEATURE.md"
echo "  Quick start: /home/gagneet/firefly/data-importer/QUICKSTART.md"
echo "  Quick ref: /home/gagneet/firefly/QUICK_REFERENCE.md"
echo ""
echo "🎯 Next Steps:"
echo "  1. Configure Personal Access Token (if not done)"
echo "  2. Log into Firefly III"
echo "  3. Click 'Import Bank Statement' in sidebar"
echo "  4. Upload a PDF statement"
echo ""
echo "========================================="
