#!/usr/bin/env bash
set -e

# ==========================================================
# Firefly III + Data Importer + Exchange Rates Installer
# With HTTPS + NGINX Virtual Host for firefly.gagneet.com
# Tested on Ubuntu 24.04 LTS
# ==========================================================

# ---------- CONFIGURATION ----------
DOMAIN="firefly.gagneet.com"
EMAIL="gagneet@silverfoxtechnologies.com.au"    # for Let's Encrypt notifications
FF_DIR="/var/www/firefly-iii"
FF_IMPORTER_DIR="/var/www/firefly-importer"
FF_EXCH_DIR="/var/www/firefly-exchanger"
DB_NAME="firefly_db"
DB_USER="fireflyuser"
DB_PASS="$(openssl rand -hex 12)"
PHP_VERSION="8.4"
# ----------------------------------

echo "=== Updating packages and installing dependencies ==="
apt update && apt upgrade -y
apt install -y git unzip nginx mysql-server certbot python3-certbot-nginx \
    php${PHP_VERSION}-fpm php${PHP_VERSION}-cli php${PHP_VERSION}-mbstring \
    php${PHP_VERSION}-xml php${PHP_VERSION}-bcmath php${PHP_VERSION}-tokenizer \
    php${PHP_VERSION}-curl php${PHP_VERSION}-zip php${PHP_VERSION}-gd \
    php${PHP_VERSION}-mysql composer

# ---------------------------------------------------
# 1️⃣ Create Database
# ---------------------------------------------------
echo "=== Creating MySQL database and user ==="
mysql -u root <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

# ---------------------------------------------------
# 2️⃣ Install Firefly III
# ---------------------------------------------------
echo "=== Installing Firefly III ==="
git clone https://github.com/firefly-iii/firefly-iii.git $FF_DIR
cd $FF_DIR
git checkout main
composer install --no-dev --optimize-autoloader
cp .env.example .env

php artisan key:generate
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
echo "=== Installing Data Importer ==="
git clone https://github.com/firefly-iii/data-importer.git $FF_IMPORTER_DIR
cd $FF_IMPORTER_DIR
git checkout main
composer install --no-dev
cp .env.example .env
php artisan key:generate
sed -i "s|FIREFLY_III_URL=.*|FIREFLY_III_URL=https://${DOMAIN}|" .env
chown -R www-data:www-data $FF_IMPORTER_DIR
chmod -R 775 $FF_IMPORTER_DIR/storage

# ---------------------------------------------------
# 4️⃣ Exchange Rates
# ---------------------------------------------------
echo "=== Installing Exchange Rates ==="
git clone https://github.com/firefly-iii/exchange-rates.git $FF_EXCH_DIR
cd $FF_EXCH_DIR
git checkout main
composer install --no-dev
cp .env.example .env
php artisan key:generate
sed -i "s|FIREFLY_III_URL=.*|FIREFLY_III_URL=https://${DOMAIN}|" .env
chown -R www-data:www-data $FF_EXCH_DIR
chmod -R 775 $FF_EXCH_DIR/storage

# ---------------------------------------------------
# 5️⃣ NGINX VHost (no conflict with existing sites)
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
# 6️⃣ Enable HTTPS with Let's Encrypt
# ---------------------------------------------------
echo "=== Requesting SSL certificate for ${DOMAIN} ==="
certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos -m ${EMAIL} --redirect

# ---------------------------------------------------
# 7️⃣ Systemd Timer for Exchange Rates
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
# ✅ Done
# ---------------------------------------------------
echo "=== ✅ Installation Complete! ==="
echo "--------------------------------------------------"
echo " Site:       https://${DOMAIN}"
echo " DB Name:    ${DB_NAME}"
echo " DB User:    ${DB_USER}"
echo " DB Pass:    ${DB_PASS}"
echo "--------------------------------------------------"
echo " Firefly III path:   ${FF_DIR}"
echo " Data Importer path: ${FF_IMPORTER_DIR}"
echo " Exchange Rates path:${FF_EXCH_DIR}"
echo "--------------------------------------------------"
echo "You can now visit https://${DOMAIN} to complete setup!"
