#!/bin/bash
# Deployment script for Appraise.ai

set -e

echo "=== Appraise.ai Deployment Script ==="

# Configuration
APP_DIR="/path/to/Appraise.ai"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/var/log/appraise_ai"
NGINX_CONF="/etc/nginx/sites-available/appraise_ai"
SERVICE_FILE="/etc/systemd/system/appraise_ai.service"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Update this script's APP_DIR variable to match your actual path
read -p "Enter the full path to Appraise.ai directory (current: $APP_DIR): " USER_APP_DIR
if [ -n "$USER_APP_DIR" ]; then
    APP_DIR="$USER_APP_DIR"
    VENV_DIR="$APP_DIR/venv"
fi

echo "Using application directory: $APP_DIR"

# Create log directory
echo "Creating log directory..."
mkdir -p "$LOG_DIR"
chown www-data:www-data "$LOG_DIR"

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx

# Create virtual environment
echo "Creating virtual environment..."
cd "$APP_DIR"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv venv
fi

# Activate virtual environment and install Python dependencies
echo "Installing Python dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# Update service file with correct paths
echo "Setting up systemd service..."
sed -i "s|/path/to/Appraise.ai|$APP_DIR|g" "$APP_DIR/appraise_ai.service"
cp "$APP_DIR/appraise_ai.service" "$SERVICE_FILE"
systemctl daemon-reload

# Update nginx configuration with correct paths
echo "Setting up nginx..."
sed -i "s|/path/to/Appraise.ai|$APP_DIR|g" "$APP_DIR/nginx.conf"
cp "$APP_DIR/nginx.conf" "$NGINX_CONF"

# Create symlink if it doesn't exist
if [ ! -L "/etc/nginx/sites-enabled/appraise_ai" ]; then
    ln -s "$NGINX_CONF" /etc/nginx/sites-enabled/appraise_ai
fi

# Test nginx configuration
nginx -t

# Set up environment file if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env file..."
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    echo "Please edit $APP_DIR/.env with your configuration"
    read -p "Press enter to continue after editing .env file..."
fi

# Set correct permissions
echo "Setting permissions..."
chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"

# Start services
echo "Starting services..."
systemctl enable appraise_ai
systemctl start appraise_ai
systemctl restart nginx

# Check status
echo ""
echo "=== Service Status ==="
systemctl status appraise_ai --no-pager

echo ""
echo "=== Deployment Complete ==="
echo "Application is running at: http://your-server-ip"
echo ""
echo "Next steps:"
echo "1. Configure DNS to point appraiseai.com to your server IP"
echo "2. Set up SSL with: sudo certbot --nginx -d appraiseai.com -d www.appraiseai.com"
echo "3. Monitor logs: sudo journalctl -u appraise_ai -f"
