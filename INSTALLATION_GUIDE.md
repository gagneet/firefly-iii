# Firefly III Complete Installation Guide

**Production Server Installation Guide for Ubuntu 24.04**

This guide documents the complete installation and configuration of Firefly III v6.4.0 on Ubuntu 24.04, served at https://firefly.gagneet.com.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Prerequisites

- Ubuntu 24.04 LTS server
- Root or sudo access
- Domain name configured (firefly.gagneet.com)
- SSL certificate (Let's Encrypt recommended)
- MySQL/MariaDB database
- Basic knowledge of Linux command line

---

## System Requirements

### Required Software Versions
- **PHP**: 8.4+ (Firefly III v6.4.0 requirement)
- **Composer**: 2.x
- **Node.js**: 18+ (20+ recommended)
- **MySQL**: 8.0+ or MariaDB 10.5+
- **Nginx**: 1.24+ or Apache 2.4+
- **Redis**: Latest stable (for caching)

---

## Installation Steps

### Step 1: Remove Old PHP Version

If you have an older PHP version installed (e.g., PHP 7.4):

```bash
# List installed PHP packages
dpkg -l | grep php

# Remove PHP 7.4 (adjust version as needed)
sudo apt remove --purge php7.4* php-common -y
sudo apt autoremove -y
sudo apt autoclean
```

### Step 2: Install PHP 8.4

```bash
# Add PHP repository
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update

# Install PHP 8.4 with required extensions
sudo apt install -y php8.4 \
    php8.4-cli \
    php8.4-fpm \
    php8.4-mysql \
    php8.4-pgsql \
    php8.4-sqlite3 \
    php8.4-curl \
    php8.4-gd \
    php8.4-mbstring \
    php8.4-xml \
    php8.4-bcmath \
    php8.4-zip \
    php8.4-intl \
    php8.4-ldap \
    php8.4-opcache

# Verify installation
php -v
# Should show: PHP 8.4.13 or newer

# Verify extensions
php -m | grep -E "(bcmath|curl|gd|intl|mbstring|mysql|xml|zip)"
```

### Step 3: Install Composer

If not already installed:

```bash
# Download and install Composer
php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
php composer-setup.php
php -r "unlink('composer-setup.php');"
sudo mv composer.phar /usr/local/bin/composer

# Verify installation
composer --version
# Should show: Composer version 2.8.x
```

### Step 4: Clone Repository and Configure

```bash
# Navigate to your home directory
cd /home/gagneet

# Clone your Firefly III repository
git clone git@github.com:gagneet/firefly-iii.git firefly
cd firefly

# Or if cloning from original repo, update remote:
git remote set-url origin git@github.com:gagneet/firefly-iii.git
```

### Step 5: Configure Environment Files

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Key .env Configuration:**

```bash
# Application
APP_ENV=production
APP_DEBUG=false
APP_KEY=                          # Will be generated in next step
APP_URL=https://firefly.gagneet.com

# Site Owner
SITE_OWNER=your-email@example.com

# Timezone and Language
TZ=America/Los_Angeles
DEFAULT_LANGUAGE=en_US
DEFAULT_LOCALE=equal

# Database
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=firefly_db
DB_USERNAME=fireflyuser
DB_PASSWORD=YourSecurePassword

# Cache and Session (Redis - configured later)
CACHE_DRIVER=redis
SESSION_DRIVER=redis

# Redis Settings
REDIS_SCHEME=tcp
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB="0"
REDIS_CACHE_DB="1"

# Security
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
TRUSTED_PROXIES=**

# Audit Logging
AUDIT_LOG_LEVEL=info
AUDIT_LOG_CHANNEL=audit_daily

# Features
USE_RUNNING_BALANCE=true
ENABLE_EXCHANGE_RATES=true
ENABLE_EXTERNAL_RATES=true
ALLOW_WEBHOOKS=true

# Static Cron Token (will be generated)
STATIC_CRON_TOKEN=
```

### Step 6: Install PHP Dependencies

```bash
cd /home/gagneet/firefly

# Install Composer dependencies (production, optimized)
composer install --no-dev --no-interaction --optimize-autoloader
```

### Step 7: Generate Application Keys

```bash
# Generate application encryption key
php artisan key:generate --force

# Generate Passport OAuth2 keys
php artisan firefly-iii:laravel-passport-keys

# Generate static cron token (save this for cron setup)
openssl rand -base64 24 | head -c 32
# Copy the output and add it to .env as STATIC_CRON_TOKEN
```

### Step 8: Setup Database

Make sure MySQL/MariaDB is installed and running:

```bash
# Check MySQL status
sudo systemctl status mysql

# Create database and user (if not already done)
sudo mysql -u root -p
```

```sql
CREATE DATABASE firefly_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fireflyuser'@'localhost' IDENTIFIED BY 'YourSecurePassword';
GRANT ALL PRIVILEGES ON firefly_db.* TO 'fireflyuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Test database connection:

```bash
php artisan db:show
```

### Step 9: Run Database Migrations

```bash
# Run migrations and seeders
php artisan migrate --seed --force
```

### Step 10: Install Redis

```bash
# Install Redis server
sudo apt install redis-server -y

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Step 11: Build Frontend Assets

Firefly III has two frontend versions. We need to build v1 (legacy) and v2 (modern).

**Build v2 (Alpine.js + Vite):**

```bash
cd /home/gagneet/firefly/resources/assets/v2

# Install dependencies
npm install

# Build for production
npm run build
```

**Build v1 (Vue 2 + Laravel Mix):**

```bash
cd /home/gagneet/firefly/resources/assets/v1

# Install dependencies
npm install

# Build for production
npm run production
```

### Step 12: Set File Permissions

```bash
cd /home/gagneet/firefly

# Add www-data to your user group
sudo usermod -a -G gagneet www-data

# Set ownership and permissions for storage directories
sudo chown -R www-data:gagneet storage
sudo chown -R www-data:gagneet bootstrap/cache
sudo chmod -R 775 storage
sudo chmod -R 775 bootstrap/cache
```

### Step 13: Configure Nginx

Create Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/firefly
```

**Nginx Configuration:**

```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name firefly.gagneet.com;

    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        try_files $uri $uri/ =404;
    }

    # Redirect all other HTTP requests to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name firefly.gagneet.com;

    # SSL Configuration (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/firefly.gagneet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/firefly.gagneet.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Document root - Firefly III public directory
    root /home/gagneet/firefly/public;
    index index.html index.htm index.php;

    # Main location
    location / {
        try_files $uri /index.php$is_args$args;
        autoindex on;
        sendfile off;
    }

    # PHP-FPM configuration
    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.4-fpm.sock;
        fastcgi_index index.php;
        fastcgi_read_timeout 240;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }

    # Logging
    access_log /var/log/nginx/firefly_access.log;
    error_log /var/log/nginx/firefly_error.log;
}
```

**Enable site and test configuration:**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/firefly /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If test is successful, reload Nginx
sudo systemctl reload nginx
```

### Step 14: Start and Enable PHP-FPM

```bash
# Start PHP 8.4-FPM
sudo systemctl start php8.4-fpm
sudo systemctl enable php8.4-fpm

# Verify it's running
sudo systemctl status php8.4-fpm

# Restart to apply all changes
sudo systemctl restart php8.4-fpm
```

### Step 15: Clear and Cache Laravel Configuration

```bash
cd /home/gagneet/firefly

# Clear all caches
php artisan config:clear
php artisan route:clear
php artisan view:clear
php artisan cache:clear
php artisan twig:clean

# Cache for production
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

---

## Configuration

### Enable Running Balance

Running balance improves financial tracking:

```bash
cd /home/gagneet/firefly

# This command will take some time on first run
php artisan firefly-iii:correct-database
```

### Setup Automatic Backups

Create backup script:

```bash
# Create directories
mkdir -p /home/gagneet/firefly/scripts
mkdir -p /home/gagneet/firefly/backups

# Create backup script
nano /home/gagneet/firefly/scripts/backup-firefly.sh
```

**Backup Script Content:**

```bash
#!/bin/bash
# Firefly III Database Backup Script

BACKUP_DIR="/home/gagneet/firefly/backups"
DB_NAME="firefly_db"
DB_USER="fireflyuser"
DB_PASS="YourSecurePassword"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/firefly_$TIMESTAMP.sql"

# Create backup
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE" 2>&1

# Compress backup
gzip "$BACKUP_FILE"

# Delete backups older than 7 days
find "$BACKUP_DIR" -name "firefly_*.sql.gz" -mtime +7 -delete

# Log result
if [ $? -eq 0 ]; then
    echo "$(date): Backup completed successfully - $BACKUP_FILE.gz" >> "$BACKUP_DIR/backup.log"
else
    echo "$(date): Backup failed" >> "$BACKUP_DIR/backup.log"
fi
```

Make script executable:

```bash
chmod +x /home/gagneet/firefly/scripts/backup-firefly.sh

# Test backup script
/home/gagneet/firefly/scripts/backup-firefly.sh
```

### Setup Cron Jobs

```bash
# Edit crontab
crontab -e

# Add these lines:
# Run Firefly III recurring transactions and maintenance (daily at midnight)
0 0 * * * cd /home/gagneet/firefly && php artisan schedule:run >> /dev/null 2>&1

# Backup database (daily at 2 AM)
0 2 * * * /home/gagneet/firefly/scripts/backup-firefly.sh >> /dev/null 2>&1
```

Verify cron jobs:

```bash
crontab -l | grep firefly
```

---

## Advanced Features

### Email Notifications (Optional)

To enable email notifications, configure in `.env`:

```bash
MAIL_MAILER=smtp
MAIL_HOST=smtp.your-provider.com
MAIL_PORT=587
MAIL_FROM=your-email@example.com
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
MAIL_ENCRYPTION=tls
```

Then clear cache:

```bash
php artisan config:cache
```

### 2FA (Two-Factor Authentication)

2FA is built-in. Users can enable it from their profile:
1. Login to Firefly III
2. Go to Profile → Two-factor authentication
3. Scan QR code with authenticator app

### API Access

API is enabled by default. Users can generate Personal Access Tokens:
1. Go to Profile → OAuth
2. Create Personal Access Token
3. Use token in API requests

API Documentation: https://docs.firefly-iii.org/api/

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Check logs:**

```bash
# Check Laravel logs
tail -100 /home/gagneet/firefly/storage/logs/ff3-fpm-fcgi-$(date +%Y-%m-%d).log

# Check Nginx error log
sudo tail -50 /var/log/nginx/firefly_error.log

# Check PHP-FPM log
sudo journalctl -u php8.4-fpm -n 50
```

**Common fixes:**

```bash
# Clear all caches
cd /home/gagneet/firefly
php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan twig:clean

# Fix permissions
sudo chown -R www-data:gagneet storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache

# Restart PHP-FPM
sudo systemctl restart php8.4-fpm
```

### Issue: Logout Returns 405 Error

This was fixed by adding JavaScript to handle logout properly. If you encounter this:

**Verify the fix in `/home/gagneet/firefly/resources/views/layout/default.twig`:**

Should contain at the end (before `</body>`):

```html
<form id="logout-form" action="{{ route('logout') }}" method="POST" style="display: none;">
    <input type="hidden" name="_token" value="{{ csrf_token() }}"/>
</form>

<script nonce="{{ JS_NONCE }}">
    document.addEventListener('DOMContentLoaded', function() {
        const logoutLinks = document.querySelectorAll('.logout-link');
        logoutLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                document.getElementById('logout-form').submit();
            });
        });
    });
</script>
```

Then clear Twig cache:

```bash
sudo rm -rf /home/gagneet/firefly/storage/framework/views/twig/*
sudo systemctl restart php8.4-fpm
```

### Issue: Missing JavaScript Files (app.js not found)

**Rebuild frontend assets:**

```bash
# V1 (legacy)
cd /home/gagneet/firefly/resources/assets/v1
npm install
npm run production

# V2 (modern)
cd /home/gagneet/firefly/resources/assets/v2
npm install
npm run build
```

### Issue: Permission Denied Errors

```bash
# Fix storage permissions
sudo chown -R www-data:gagneet /home/gagneet/firefly/storage
sudo chown -R www-data:gagneet /home/gagneet/firefly/bootstrap/cache
sudo chmod -R 775 /home/gagneet/firefly/storage
sudo chmod -R 775 /home/gagneet/firefly/bootstrap/cache

# Restart PHP-FPM
sudo systemctl restart php8.4-fpm
```

### Issue: Database Connection Failed

**Test database connection:**

```bash
cd /home/gagneet/firefly
php artisan db:show
```

**Verify credentials:**

```bash
# Test MySQL connection manually
mysql -u fireflyuser -p -h 127.0.0.1 firefly_db

# Check .env file
grep DB_ .env
```

### Issue: Redis Connection Failed

```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Restart Redis
sudo systemctl restart redis-server

# Clear Laravel cache
php artisan cache:clear
php artisan config:cache
```

---

## Maintenance

### Regular Updates

**Update Firefly III:**

```bash
cd /home/gagneet/firefly

# Backup first!
/home/gagneet/firefly/scripts/backup-firefly.sh

# Put in maintenance mode
php artisan down

# Pull latest changes
git pull origin main

# Update dependencies
composer install --no-dev --no-interaction --optimize-autoloader

# Run migrations
php artisan migrate --force

# Rebuild frontend
cd resources/assets/v1 && npm run production
cd ../v2 && npm run build

# Clear and cache
cd /home/gagneet/firefly
php artisan config:clear
php artisan cache:clear
php artisan view:clear
php artisan twig:clean
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Restart services
sudo systemctl restart php8.4-fpm

# Take out of maintenance mode
php artisan up
```

### Monitor Disk Space

```bash
# Check disk usage
df -h /home/gagneet/firefly

# Check backup directory size
du -sh /home/gagneet/firefly/backups

# Check log file sizes
du -sh /home/gagneet/firefly/storage/logs
```

### Clean Up Old Logs

```bash
# Remove logs older than 30 days
find /home/gagneet/firefly/storage/logs -name "*.log" -mtime +30 -delete

# Remove old backups (older than 30 days)
find /home/gagneet/firefly/backups -name "*.sql.gz" -mtime +30 -delete
```

### Performance Optimization

**Check cache status:**

```bash
cd /home/gagneet/firefly
php artisan about | grep Cache
```

**Optimize for production:**

```bash
# Clear and recache everything
php artisan optimize:clear
php artisan optimize

# Restart PHP-FPM
sudo systemctl restart php8.4-fpm
```

---

## Security Best Practices

1. **Keep software updated:**
   - Regularly update PHP, Nginx, MySQL, Redis
   - Keep Firefly III updated

2. **Strong passwords:**
   - Use strong database passwords
   - Require strong user passwords
   - Enable 2FA for all users

3. **Firewall:**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

4. **SSL/TLS:**
   - Keep SSL certificates up to date
   - Use Let's Encrypt for free certificates
   - Enable HSTS (already in Nginx config)

5. **Regular backups:**
   - Daily database backups
   - Store backups offsite
   - Test restore procedures

6. **Monitor logs:**
   ```bash
   # Check for suspicious activity
   sudo tail -f /var/log/nginx/firefly_access.log
   sudo tail -f /var/log/nginx/firefly_error.log
   ```

---

## Key Files and Directories

```
/home/gagneet/firefly/
├── .env                          # Main configuration file
├── public/                       # Web root (nginx points here)
├── storage/
│   ├── logs/                     # Application logs
│   └── framework/
│       ├── cache/                # Cache files
│       └── views/                # Compiled views
├── bootstrap/cache/              # Bootstrap cache
├── resources/
│   ├── assets/v1/                # Vue 2 frontend source
│   ├── assets/v2/                # Alpine.js frontend source
│   └── views/                    # Blade/Twig templates
├── scripts/                      # Custom scripts
│   └── backup-firefly.sh         # Backup script
└── backups/                      # Database backups

/etc/nginx/sites-available/firefly  # Nginx configuration
/var/log/nginx/                     # Nginx logs
/run/php/php8.4-fpm.sock           # PHP-FPM socket
```

---

## Useful Commands

```bash
# Application status
php artisan about

# Database status
php artisan db:show

# Clear all caches
php artisan optimize:clear

# View routes
php artisan route:list

# Check queue status
php artisan queue:work

# Run cron manually
php artisan schedule:run

# Check Firefly version
php artisan firefly-iii:output-version

# Test email configuration
php artisan tinker
>>> Mail::raw('Test email', function($msg) { $msg->to('your-email@example.com')->subject('Test'); });
```

---

## References

- **Firefly III Documentation:** https://docs.firefly-iii.org/
- **GitHub Repository:** https://github.com/firefly-iii/firefly-iii
- **API Documentation:** https://docs.firefly-iii.org/api/
- **Community Support:** https://github.com/firefly-iii/firefly-iii/discussions

---

## Installation Summary

This installation configured:

- ✅ PHP 8.4.13 with all required extensions
- ✅ Composer 2.8.12
- ✅ MySQL database with proper credentials
- ✅ Redis for caching and sessions
- ✅ Nginx with SSL/TLS (Let's Encrypt)
- ✅ Frontend assets built (v1 and v2)
- ✅ Production-optimized Laravel configuration
- ✅ Automated backups (daily at 2 AM)
- ✅ Cron jobs for recurring transactions
- ✅ Security headers and hardening
- ✅ Audit logging enabled
- ✅ Exchange rates enabled
- ✅ Webhooks enabled
- ✅ Running balance enabled

**Installation Date:** October 5, 2025
**Firefly III Version:** 6.4.0
**Server:** Ubuntu 24.04 LTS
**URL:** https://firefly.gagneet.com

---

## Support

For issues specific to this installation, check:
1. This guide's troubleshooting section
2. Firefly III official documentation
3. GitHub issues and discussions
4. Server logs

**Created by:** Claude Code Assistant
**Last Updated:** October 5, 2025
