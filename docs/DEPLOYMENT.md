# Deployment Guide - Making Schema Accessible via Web Domain

This guide will walk you through deploying Schema to make it accessible via a web domain (e.g., `schema.yourdomain.com`).

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Deployment Options Comparison](#deployment-options-comparison)
3. [Option 1: Render.com (Easiest - Free Tier)](#option-1-rendercom-easiest---free-tier)
4. [Option 2: Railway.app (Easy - Free Trial)](#option-2-railwayapp-easy---free-trial)
5. [Option 3: AWS/DigitalOcean (Most Control)](#option-3-awsdigitalocean-most-control)
6. [Domain Setup](#domain-setup)
7. [SSL Certificate Setup](#ssl-certificate-setup)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ A GitHub account (to host your code)
- ✅ A domain name (or willing to purchase one)
- ✅ All GIS data files ready (they're large - may need special handling)
- ✅ Python requirements file updated

### Step 0: Prepare Your Repository

1. **Create a GitHub repository:**
   ```bash
   # Initialize git if not already done
   cd "X:\Projects\A_Valuation\_Apps\Appraise.ai"
   git init

   # Create .gitignore
   echo "__pycache__/
   *.pyc
   *.pyo
   .env
   *.log
   .DS_Store
   venv/
   env/
   *.sqlite3" > .gitignore

   # Add all files
   git add .
   git commit -m "Initial commit - Appraise.ai reorganized structure"
   ```

2. **Push to GitHub:**
   - Go to github.com and create a new repository called `appraise-ai`
   - Follow GitHub's instructions to push your local repo:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/appraise-ai.git
   git branch -M main
   git push -u origin main
   ```

3. **Important: Handle Large GIS Files**

   Your GIS data files are very large. You have two options:

   **Option A: Use Git LFS (Large File Storage)**
   ```bash
   git lfs install
   git lfs track "*.gpkg"
   git lfs track "*.gdb"
   git add .gitattributes
   git commit -m "Add Git LFS for large GIS files"
   ```

   **Option B: Store GIS data separately (Recommended)**
   - Upload GIS files to cloud storage (AWS S3, DigitalOcean Spaces, Google Cloud Storage)
   - Modify your code to download/mount these files at runtime
   - Cheaper and faster than including in git repo

---

## Deployment Options Comparison

| Option | Difficulty | Cost | Best For | Deploy Time |
|--------|-----------|------|----------|-------------|
| **Render.com** | ⭐ Easy | Free tier available | Quick deployment, testing | 10 mins |
| **Railway.app** | ⭐⭐ Easy | $5/month (500 hours free trial) | Small teams, dev/staging | 10 mins |
| **Heroku** | ⭐⭐ Medium | $7/month minimum | Established apps | 15 mins |
| **DigitalOcean App Platform** | ⭐⭐ Medium | $5/month | Growing apps | 20 mins |
| **AWS/DigitalOcean VM** | ⭐⭐⭐⭐ Hard | $5-20/month | Full control, large scale | 1-2 hours |

**Recommendation: Start with Render.com for testing, then move to DigitalOcean VM for production.**

---

## Option 1: Render.com (Easiest - Free Tier)

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 2: Prepare Configuration Files

You already have these files! Let's verify they're correct:

**`requirements.txt`** - Already exists, verify it has:
```txt
Flask==3.0.0
flask-caching==2.1.0
geopandas==0.14.0
pandas==2.1.1
numpy==1.26.0
plotly==5.17.0
shapely==2.0.2
python-dateutil==2.8.2
numpy-financial==1.0.0
gunicorn==21.2.0
```

**`render.yaml`** - Already exists! Render will use this automatically.

**`Procfile`** - Already exists with:
```
web: gunicorn wsgi:app
```

### Step 3: Deploy to Render

1. **In Render Dashboard:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository `appraise-ai`
   - Render will auto-detect your `render.yaml`

2. **Configure the service:**
   - **Name:** `appraise-ai`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Plan:** Free (or Starter for $7/month)

3. **Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - Add: `SECRET_KEY` = `your-secret-key-here-make-it-long-and-random`
   - Add: `FLASK_ENV` = `production`

4. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy (takes 5-10 minutes)
   - You'll get a URL like: `https://appraise-ai.onrender.com`

### Step 4: Handle Large GIS Files on Render

**Problem:** Free tier has limited storage (512 MB).

**Solution:** Use persistent disk or external storage:

1. **Add Persistent Disk (Render):**
   - In your service settings → "Disks"
   - Add disk: `/opt/render/project/src/app/atlas/gis/Layers` (20 GB)
   - Upload GIS files manually via SFTP or mount script

2. **Or use S3/Cloud Storage:**
   - Upload GIS files to AWS S3 or similar
   - Modify `config.py` to download files on first run

---

## Option 2: Railway.app (Easy - Free Trial)

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. You get $5 free credit + 500 hours free trial

### Step 2: Deploy from GitHub

1. **New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `appraise-ai` repository

2. **Railway auto-detects Python:**
   - It will find your `requirements.txt`
   - Build command: `pip install -r requirements.txt`
   - Start command: Railway auto-detects from `Procfile`

3. **Add Environment Variables:**
   - Click your service → "Variables"
   - Add `SECRET_KEY` = `random-secret-key`
   - Add `PORT` = `8080` (Railway provides this automatically)

4. **Deploy:**
   - Click "Deploy"
   - You'll get a URL like: `https://appraise-ai-production.up.railway.app`

### Step 3: Custom Domain on Railway

1. **Generate Domain:**
   - In service settings → "Settings" → "Domains"
   - Click "Generate Domain"

2. **Add Custom Domain:**
   - Click "Custom Domain"
   - Enter: `appraise.yourdomain.com`
   - Railway will provide DNS records to add to your domain registrar

---

## Option 3: AWS/DigitalOcean (Most Control)

This is the recommended option for production with large GIS files.

### Step-by-Step: DigitalOcean Droplet Deployment

#### Step 1: Create DigitalOcean Account

1. Go to [digitalocean.com](https://digitalocean.com)
2. Sign up (get $200 free credit with GitHub Student or promo codes)

#### Step 2: Create a Droplet (VM)

1. **Create Droplet:**
   - Click "Create" → "Droplets"
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic
   - **CPU Options:** Regular Intel ($6/month = 1GB RAM, 25GB SSD)
   - **Datacenter:** Choose closest to your users (Sydney for AU)
   - **Authentication:** SSH Key (create one if needed)
   - **Hostname:** `appraise-ai-prod`

2. **Wait for creation** (takes 1 minute)
3. **Note your Droplet's IP address** (e.g., `165.22.123.45`)

#### Step 3: Connect to Your Server

```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP
```

#### Step 4: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and required packages
apt install python3-pip python3-venv nginx git -y

# Install GDAL and geospatial libraries (for GIS)
apt install gdal-bin libgdal-dev python3-gdal -y
apt install libspatialindex-dev -y
```

#### Step 5: Clone Your Application

```bash
# Create application directory
mkdir -p /var/www/appraise-ai
cd /var/www/appraise-ai

# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/appraise-ai.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 6: Upload GIS Data Files

**Option A: Use SCP (from your local machine):**
```bash
# From your Windows machine (use Git Bash or PowerShell)
scp -r "X:\Projects\A_Valuation\_Apps\Appraise.ai\app\atlas\gis\Layers" root@YOUR_DROPLET_IP:/var/www/appraise-ai/app/atlas/gis/
```

**Option B: Use rsync (faster for large files):**
```bash
rsync -avz -e ssh "X:\Projects\A_Valuation\_Apps\Appraise.ai\app\atlas\gis\Layers" root@YOUR_DROPLET_IP:/var/www/appraise-ai/app/atlas/gis/
```

**Option C: Download from cloud storage:**
```bash
# If you uploaded to S3/DigitalOcean Spaces
cd /var/www/appraise-ai/app/atlas/gis/
wget https://your-bucket.s3.amazonaws.com/gis-data.tar.gz
tar -xzf gis-data.tar.gz
```

#### Step 7: Configure Gunicorn Service

```bash
# Create systemd service file
nano /etc/systemd/system/appraise-ai.service
```

**Paste this configuration:**
```ini
[Unit]
Description=Appraise.ai Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/appraise-ai
Environment="PATH=/var/www/appraise-ai/venv/bin"
Environment="SECRET_KEY=your-super-secret-key-change-this"
ExecStart=/var/www/appraise-ai/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

**Save and exit** (Ctrl+X, Y, Enter)

```bash
# Set correct permissions
chown -R www-data:www-data /var/www/appraise-ai

# Enable and start service
systemctl daemon-reload
systemctl enable appraise-ai
systemctl start appraise-ai

# Check status
systemctl status appraise-ai
```

#### Step 8: Configure Nginx as Reverse Proxy

```bash
# Create Nginx configuration
nano /etc/nginx/sites-available/appraise-ai
```

**Paste this configuration:**
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/appraise-ai/app/static;
    }
}
```

**Save and exit**, then:

```bash
# Enable site
ln -s /etc/nginx/sites-available/appraise-ai /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

#### Step 9: Point Your Domain to the Server

1. **Get your Droplet's IP address** from DigitalOcean dashboard

2. **Add DNS Records at your domain registrar:**
   - **A Record:** `@` → `YOUR_DROPLET_IP`
   - **A Record:** `www` → `YOUR_DROPLET_IP`

   Or if using subdomain:
   - **A Record:** `appraise` → `YOUR_DROPLET_IP`

3. **Wait for DNS propagation** (5 minutes to 48 hours)

#### Step 10: Add SSL Certificate (HTTPS)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)

# Certbot will auto-renew. Test renewal:
certbot renew --dry-run
```

**Done! Your site is now live at `https://yourdomain.com`**

---

## Domain Setup

### Where to Buy Domains

- **Namecheap** - $10-15/year (.com)
- **Google Domains** - $12/year
- **Cloudflare** - $9/year (cheapest)
- **GoDaddy** - $15-20/year

### Setting Up DNS

Once you have a domain, add these DNS records:

**For root domain (`appraise.com`):**
```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 3600
```

**For www subdomain:**
```
Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 3600
```

**For subdomain (`app.appraise.com`):**
```
Type: A
Name: app
Value: YOUR_SERVER_IP
TTL: 3600
```

---

## SSL Certificate Setup

### Option 1: Let's Encrypt (Free)

Already covered in Step 10 above using Certbot.

### Option 2: Cloudflare (Free + CDN)

1. **Add site to Cloudflare:**
   - Sign up at cloudflare.com
   - Click "Add Site"
   - Enter your domain

2. **Update nameservers:**
   - Cloudflare will give you 2 nameservers
   - Update these at your domain registrar

3. **Enable SSL:**
   - In Cloudflare → SSL/TLS → "Full" or "Full (strict)"
   - Cloudflare automatically provides SSL

4. **Benefits:**
   - Free SSL
   - CDN (faster global access)
   - DDoS protection
   - Caching

---

## Monitoring & Maintenance

### Check Application Status

```bash
# Check if app is running
systemctl status appraise-ai

# View logs
journalctl -u appraise-ai -f

# Restart app
systemctl restart appraise-ai
```

### Update Application

```bash
cd /var/www/appraise-ai
git pull origin main
systemctl restart appraise-ai
```

### Monitor Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check running processes
htop
```

---

## Troubleshooting

### Site Not Loading

1. **Check Nginx:**
   ```bash
   systemctl status nginx
   nginx -t
   ```

2. **Check Gunicorn:**
   ```bash
   systemctl status appraise-ai
   journalctl -u appraise-ai -n 50
   ```

3. **Check Firewall:**
   ```bash
   ufw status
   ufw allow 80
   ufw allow 443
   ```

### GIS Data Not Loading

1. **Check file permissions:**
   ```bash
   ls -la /var/www/appraise-ai/app/atlas/gis/Layers
   chown -R www-data:www-data /var/www/appraise-ai
   ```

2. **Check paths in config:**
   ```bash
   nano /var/www/appraise-ai/app/atlas/gis/config.py
   # Ensure paths are correct
   ```

### 500 Internal Server Error

```bash
# Check Python errors
journalctl -u appraise-ai -n 100

# Check Nginx error log
tail -f /var/log/nginx/error.log
```

---

## Cost Estimate

### Cheap Option (Render/Railway)
- **Free tier:** $0/month (limited resources)
- **Paid tier:** $7/month

### Recommended Option (DigitalOcean)
- **Droplet:** $6-12/month
- **Domain:** $10-15/year
- **SSL:** Free (Let's Encrypt)
- **Storage for GIS:** $1/month per 10GB (DigitalOcean Spaces)
- **Total:** ~$10-15/month

### Enterprise Option (AWS)
- **EC2 instance:** $10-50/month
- **RDS database:** $15/month (if you add database)
- **S3 storage:** $0.023/GB per month
- **Load balancer:** $16/month
- **Total:** $40-100/month

---

## Recommended Path

**For testing/demo:**
1. Deploy to Render.com (10 minutes)
2. Use free tier
3. Share the `.onrender.com` URL

**For production:**
1. Buy domain ($10/year)
2. Deploy to DigitalOcean Droplet ($6/month)
3. Upload GIS files to DigitalOcean Spaces ($1/month)
4. Set up SSL with Let's Encrypt (free)
5. **Total cost: ~$10/month**

---

## Need Help?

If you get stuck:
1. Check logs: `journalctl -u appraise-ai -f`
2. Test locally first: `python run.py`
3. Check file permissions: `ls -la`
4. Verify environment variables are set
5. Ensure all GIS files uploaded correctly

**Your app will be live at: `https://yourdomain.com`**
