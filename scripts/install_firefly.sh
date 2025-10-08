#!/usr/bin/env bash
set -e

# ==========================================================
# Firefly III + Data Importer + Exchange Rates Installer
# Tested on Ubuntu 24.04 LTS
# ==========================================================

# ---------- CONFIGURABLE VARIABLES ----------
FF_DIR="/var/www/firefly-iii"
FF_IMPORTER_DIR="/var/www/firefly-importer"
FF_EXCH_DIR="/var/www/firefly-exchanger"
DB_NAME="firefly"
DB_USER="firefly"
DB_PASS="fireflypass"
APP_URL="http://localhost"
PHP_VERSION="8.3" # Adjust if you installed a different PHP version
# -------------------------------------------

echo "=== Updating and installing dependencies ==="
apt update && apt upgrade -y
apt install -y git unzip nginx mysql-server \
    php${PHP_VERSION}-fpm php${PHP_VERSION}-cli php${PHP_VERSION}-mbstring \
    php${PHP_VERSION}-xml php${PHP_VERSION}-bcmath php${PHP_VERSION}-tokenizer \
    php${PHP_VERSION}-curl php${PHP_VERSION}-zip php${PHP_VERSION}-gd \
    php${PHP_VERSION}-mysql composer

echo "=== Creating MySQL database and user ==="
mysql -u root <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

# ---------------------------------------------------
# 1️⃣ Install Firefly III Core
# ---------------------------------------------------
echo "=== Installing Firefly III ==="
mkdir -p $FF_DIR
cd /var/www
git clone https://github.com/firefly-iii/firefly-iii.git $FF_DIR
cd $FF_DIR
git checkout main
composer install --no-dev --optimize-autoloader
cp .env.example .env

# Generate key and setup environment
php artisan key:generate
sed -i "s|APP_URL=.*|APP_URL=${APP_URL}|" .env
sed -i "s|DB_CONNECTION=.*|DB_CONNECTION=mysql|" .env
sed -i "s|DB_HOST=.*|DB_HOST=localhost|" .env
sed -i "s|DB_DATABASE=.*|DB_DATABASE=${DB_NAME}|" .env
sed -i "s|DB_USERNAME=.*|DB_USERNAME=${DB_USER}|" .env
sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=${DB_PASS}|" .env

php artisan migrate --seed

chown -R www-data:www-data $FF_DIR
chmod -R 775 $FF_DIR/storage

# ---------------------------------------------------
# 2️⃣ Install Firefly Data Importer
# ---------------------------------------------------
echo "=== Installing Firefly Data Importer ==="
git clone https://github.com/firefly-iii/data-importer.git $FF_IMPORTER_DIR
cd $FF_IMPORTER_DIR
git checkout main
composer install --no-dev --optimize-autoloader
cp .env.example .env
php artisan key:generate

sed -i "s|FIREFLY_III_URL=.*|FIREFLY_III_URL=${APP_URL}|" .env

chown -R www-data:www-data $FF_IMPORTER_DIR
chmod -R 775 $FF_IMPORTER_DIR/storage

# ---------------------------------------------------
# 3️⃣ Install Firefly Exchange Rates
# ---------------------------------------------------
echo "=== Installing Firefly Exchange Rates ==="
git clone https://github.com/firefly-iii/exchange-rates.git $FF_EXCH_DIR
cd $FF_EXCH_DIR
git checkout main
composer install --no-dev --optimize-autoloader
cp .env.example .env
php artisan key:generate

sed -i "s|FIREFLY_III_URL=.*|FIREFLY_III_URL=${APP_URL}|" .env

chown -R www-data:www-data $FF_EXCH_DIR
chmod -R 775 $FF_EXCH_DIR/storage

# ---------------------------------------------------
# 4️⃣ NGINX Configuration
# ---------------------------------------------------
echo "=== Configuring NGINX ==="
cat > /etc/nginx/sites-available/firefly.conf <<NGINXCONF
server {
    listen 80;
    server_name _;

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

ln -sf /etc/nginx/sites-available/firefly.conf /etc/nginx/sites-enabled/firefly.conf
nginx -t && systemctl reload nginx

# ---------------------------------------------------
# 5️⃣ Systemd Services
# ---------------------------------------------------
echo "=== Creating systemd timers for Exchange Rates ==="
cat > /etc/systemd/system/firefly-exchanger.timer <<SYSTEMD_TIMER
[Unit]
Description=Run Firefly Exchange Rates hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
SYSTEMD_TIMER

cat > /etc/systemd/system/firefly-exchanger.service <<SYSTEMD_SERVICE
[Unit]
Description=Run Firefly Exchange Rates Update

[Service]
Type=oneshot
WorkingDirectory=${FF_EXCH_DIR}
ExecStart=/usr/bin/php artisan firefly-iii:exchange-rates:update
User=www-data
SYSTEMD_SERVICE

systemctl daemon-reload
systemctl enable --now firefly-exchanger.timer

echo "=== ✅ Installation Complete! ==="
echo "--------------------------------------------------"
echo "Firefly III URL: ${APP_URL}"
echo "MySQL DB: ${DB_NAME}, User: ${DB_USER}, Pass: ${DB_PASS}"
echo "Data Importer path: ${FF_IMPORTER_DIR}"
echo "Exchange Rates path: ${FF_EXCH_DIR}"
echo "--------------------------------------------------"
echo "You can now open Firefly III in your browser!"

