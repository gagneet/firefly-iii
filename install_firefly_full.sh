#!/usr/bin/env bash
set -e

# ==========================================================
# Firefly III + Data Importer + Exchange Rates + Backup Setup
# With HTTPS + NGINX Virtual Host for firefly.gagneet.com
# Tested on Ubuntu 24.04 LTS
# ==========================================================

# ---------- CONFIGURATION ----------
DOMAIN="firefly.gagneet.com"
EMAIL="your-email@example.com"    # Let's Encrypt notifications
FF_DIR="/var/www/firefly-iii"
FF_IMPORTER_DIR="/var/www/firefly-importer"
FF_EXCH_DIR="/var/www/firefly-exchanger"
BACKUP_DIR="/var/backups/firefly"
DB_NAME="firefly"
DB_USER="firefly"
DB_PASS="$(openssl rand -hex 12)"
PHP_VERSION="8.3"
# ----------------------------------

echo "=== Updating packages and installing dependencies ==="
apt update && apt upgrade -y
apt install -y git unzip nginx mysql-server certbot python3-certbot-nginx \
    php${PHP_VERSION}-fpm php${PHP_VERSION}-cli php${PHP_VERSION}-mbstring \
    php${PHP_VERSION}-xml php${PHP_VERSION}-bcmath php${PHP_VERSION}-tokenizer \
    php${PHP_VERSION}-curl php${PHP_VERSION}-zip php${PHP_VERSION}-gd \
    php${PHP_VERSION}-mysql composer

# ---------------------------------------------------
# 1️⃣ Database Setup
# ---------------------------------------------------
echo "=== Creating MySQL database and user ==="
mysql -u root <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

# ---------------------------------------------------
# 2️⃣ Firefly III Core
# ---------------------------------------------------
echo "=== Installing Firefly III ==="
git clone https://github.com/firefly-iii/firefly-iii.git $FF_DIR
cd $FF_DIR
git checkout main
composer install --no-dev --optimize-autoloader
cp .env.example .env
php artisan key:generate

# Configure .env
sed -i "s|APP_URL=.*|APP_URL=https://${DOMAIN}|" .env
sed -i "s|DB_CONNECTION=.*|DB_CONNECTION=mysql|" .env
sed -i "s|DB_HOST=.*|DB_HOST=localhost|" .env
sed -i "s|DB_DATABASE=.*|DB_DATABASE=${DB_NAME}|" .env
sed -i "s|DB_USERNAME=.*|DB_USERNAME=${DB_USER}|" .env
sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=${DB_PASS}|" .env

php artisan migrate --seed
chown -R www-data:www-data $FF_DIR
chmod -R 775 $FF_DIR/storage

# ---------------------------------------------------
# 3️⃣ Data Importer
# ---------------------------------------------------
echo "=== Installing Firefly Data Importer ==="
git clone https://github.com/firefly-iii/data-importer.git $FF_IMPORTER_DIR
cd $FF_IMPORTER_DIR
git checkout main
composer install --no-dev --optimize-autoloader
cp .env.example .env
php artisan key:generate
sed -i "s|FIREFLY_III_URL=.*|FIREFLY_III_URL=https://${DOMAIN}|" .env
chown -R www-data:www-data $FF_IMPORTER_DIR
chmod -R 775 $FF_IMPORTER_DIR/storage

# ---------------------------------------------------
# 4️⃣ Exchange Rates
# ---------------------------------------------------
echo "=== Installing Firefly Exchange Rates ==="
git clone https://github.com/firefly-iii/exchange-rates.git $FF_EXCH_DIR
cd $FF_EXCH_DIR
git checkout main
composer install --no-dev --optimize-autoloader
cp .env.example .env
php artisan key:generate
sed -i "s|FIREFLY_III_URL=.*|FIREFLY_III_URL=https://${DOMAIN}|" .env
chown -R www-data:www-data $FF_EXCH_DIR
chmod -R 775 $FF_EXCH_DIR/storage

# ---------------------------------------------------
# 5️⃣ NGINX VHost for Firefly (non-destructive)
# ---------------------------------------------------
echo "=== Configuring NGINX for ${DOMAIN} ==="
cat > /etc/nginx/sites-available/${DOMAIN}.conf <<NGINXCONF
server {
    listen 80;
    server_name ${DOMAIN};

    root ${FF_DIR}/public;
    index index.php;

    location / {
        try_files \$uri /index.php?\$query_string;
    }

    location ~ \.php\$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php${PHP_VERSION}-fpm.sock;
    }

    location ~ /\.ht {
        deny all;
    }
}
NGINXCONF

ln -sf /etc/nginx/sites-available/${DOMAIN}.conf /etc/nginx/sites-enabled/${DOMAIN}.conf
nginx -t && systemctl reload nginx

# ---------------------------------------------------
# 6️⃣ Enable HTTPS (Let's Encrypt)
# ---------------------------------------------------
echo "=== Requesting SSL certificate for ${DOMAIN} ==="
certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos -m ${EMAIL} --redirect
systemctl enable certbot.timer

# ---------------------------------------------------
# 7️⃣ Exchange Rate Updater (Systemd Timer)
# ---------------------------------------------------
cat > /etc/systemd/system/firefly-exchanger.service <<SYSTEMD_SERVICE
[Unit]
Description=Update Firefly Exchange Rates

[Service]
Type=oneshot
WorkingDirectory=${FF_EXCH_DIR}
ExecStart=/usr/bin/php artisan firefly-iii:exchange-rates:update
User=www-data
SYSTEMD_SERVICE

cat > /etc/systemd/system/firefly-exchanger.timer <<SYSTEMD_TIMER
[Unit]
Description=Run Firefly Exchange Rate Updater Hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
SYSTEMD_TIMER

systemctl daemon-reload
systemctl enable --now firefly-exchanger.timer

# ---------------------------------------------------
# 8️⃣ Nightly Backup Routine (MySQL + Storage)
# ---------------------------------------------------
echo "=== Setting up nightly backups ==="
mkdir -p ${BACKUP_DIR}

cat > /usr/local/bin/firefly-backup.sh <<BACKUP_SCRIPT
#!/usr/bin/env bash
set -e
DATE=\$(date +%Y-%m-%d)
BACKUP_PATH=${BACKUP_DIR}/firefly-\$DATE
mkdir -p \$BACKUP_PATH

# MySQL Dump
mysqldump -u ${DB_USER} -p${DB_PASS} ${DB_NAME} > \$BACKUP_PATH/firefly.sql

# Storage Backup
tar -czf \$BACKUP_PATH/storage.tar.gz -C ${FF_DIR} storage

# Rotate backups older than 7 days
find ${BACKUP_DIR} -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: \$BACKUP_PATH"
BACKUP_SCRIPT

chmod +x /usr/local/bin/firefly-backup.sh

# Add cron job
cat > /etc/cron.d/firefly-backup <<CRONJOB
0 2 * * * root /usr/local/bin/firefly-backup.sh >> /var/log/firefly-backup.log 2>&1
CRONJOB

echo "=== Backup routine scheduled for 2:00 AM daily ==="

# ---------------------------------------------------
# ✅ Summary
# ---------------------------------------------------
echo "=== ✅ Firefly III Installation Complete ==="
echo "--------------------------------------------------"
echo " Firefly URL:     https://${DOMAIN}"
echo " MySQL DB:        ${DB_NAME}"
echo " DB User:         ${DB_USER}"
echo " DB Pass:         ${DB_PASS}"
echo " Backup Dir:      ${BACKUP_DIR}"
echo " Cron Job:        2:00 AM daily (7-day retention)"
echo "--------------------------------------------------"
echo "You can now open Firefly III in your browser!"

