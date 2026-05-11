# AI Growth Labs — Complete Deployment Guide

## OPTION 1: cPanel / Shared Hosting (Frontend Website Only)

### Step 1: Download Code
```bash
# On your computer, download from GitHub:
git clone https://github.com/in43am-beep/ai-growth-labs.git
```
Or download ZIP from: https://github.com/in43am-beep/ai-growth-labs/archive/refs/heads/devin/1778433837-ai-seo-agency-website.zip

### Step 2: Login to cPanel
- Go to your hosting provider (Namecheap, Bluehost, GoDaddy, Hostinger, etc.)
- Login to cPanel (usually at yourdomain.com/cpanel or yourdomain.com:2083)

### Step 3: Upload Files
1. Open **File Manager** in cPanel
2. Navigate to `public_html/` folder
3. Upload ALL files from the `site/` folder:
   - `index.html` → goes directly into `public_html/`
   - `css/` folder → `public_html/css/`
   - `js/` folder → `public_html/js/`
   - `pages/` folder → `public_html/pages/`
   - `templates/` folder → `public_html/templates/`

### Step 4: Verify
- Visit your domain: `https://yourdomain.com`
- Check all pages work
- Test the chatbot (click "Chat With Us" button)
- Test mobile view

### Step 5: SSL Certificate
- In cPanel → **SSL/TLS** → Enable free Let's Encrypt SSL
- Or use **AutoSSL** if available

### cPanel File Structure:
```
public_html/
├── index.html          ← Homepage
├── css/
│   └── main.css        ← All styles
├── js/
│   └── main.js         ← Chatbot + interactions
├── pages/
│   ├── local-seo.html
│   ├── gbp-optimization.html
│   ├── reputation-management.html
│   ├── ai-seo.html
│   ├── paid-advertising.html
│   ├── social-media.html
│   ├── content-creation.html
│   ├── seo-for-dentists.html
│   ├── seo-for-lawyers.html
│   ├── seo-for-restaurants.html
│   ├── seo-for-plumbers.html
│   ├── seo-for-hvac.html
│   ├── seo-for-medical-spas.html
│   ├── about.html
│   ├── contact.html
│   ├── case-studies.html
│   ├── blog.html
│   ├── free-audit.html
│   ├── privacy-policy.html
│   ├── terms.html
│   └── disclaimer.html
└── templates/          ← Agency templates (optional)
```

---

## OPTION 2: VPS Deployment (Full System — Website + Dashboard)

### Recommended VPS Providers:
- **DigitalOcean** — $6/month (1GB RAM, 25GB SSD)
- **Vultr** — $6/month
- **AWS Lightsail** — $5/month
- **Hostinger VPS** — $5/month

### Step 1: Create VPS
- Choose **Ubuntu 22.04 LTS**
- Minimum: 1 CPU, 1GB RAM, 25GB SSD
- Get your server IP address

### Step 2: Connect to VPS
```bash
ssh root@YOUR_SERVER_IP
```

### Step 3: Install System Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.10+, pip, nginx, certbot
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Install Node.js (optional, for future features)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
```

### Step 4: Clone Repository
```bash
cd /var/www
git clone https://github.com/in43am-beep/ai-growth-labs.git
cd ai-growth-labs
```

### Step 5: Setup Backend Dashboard
```bash
# Create virtual environment
cd /var/www/ai-growth-labs/dashboard
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 database.py

# Test it works
python3 main.py &
curl http://localhost:8000/login
# Should show HTML. Press Ctrl+C to stop.
```

### Step 6: Create Systemd Service (Auto-start on boot)
```bash
cat > /etc/systemd/system/aigrowth-dashboard.service << 'EOF'
[Unit]
Description=AI Growth Labs Dashboard
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ai-growth-labs/dashboard
ExecStart=/var/www/ai-growth-labs/dashboard/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3
Environment=SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_STRING_64_CHARS

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R www-data:www-data /var/www/ai-growth-labs

# Enable and start
systemctl daemon-reload
systemctl enable aigrowth-dashboard
systemctl start aigrowth-dashboard
systemctl status aigrowth-dashboard
```

### Step 7: Configure Nginx
```bash
cat > /etc/nginx/sites-available/aigrowth-labs << 'EOF'
# Main website
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/ai-growth-labs/site;
    index index.html;

    # Cache static files
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression for speed
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    location / {
        try_files $uri $uri/ =404;
    }
}

# Dashboard (on subdomain)
server {
    listen 80;
    server_name dashboard.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/aigrowth-labs /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart
nginx -t
systemctl restart nginx
```

### Step 8: Point Domain to VPS
In your domain registrar (Namecheap, GoDaddy, etc.):
```
Type: A Record
Name: @
Value: YOUR_VPS_IP

Type: A Record
Name: www
Value: YOUR_VPS_IP

Type: A Record
Name: dashboard
Value: YOUR_VPS_IP
```

### Step 9: Setup SSL (Free HTTPS)
```bash
# Wait 5-10 min for DNS to propagate, then:
certbot --nginx -d yourdomain.com -d www.yourdomain.com -d dashboard.yourdomain.com
```

### Step 10: Verify Everything
```
Website:    https://yourdomain.com
Dashboard:  https://dashboard.yourdomain.com
Login:      admin / admin123
```

---

## IMPORTANT: First Things To Do After Deployment

### 1. Change Default Passwords
Login to dashboard → Super Admin creates new credentials for everyone.

### 2. Update SECRET_KEY
Edit `/etc/systemd/system/aigrowth-dashboard.service`:
```
Environment=SECRET_KEY=your_random_64_character_string_here
```
Then: `systemctl daemon-reload && systemctl restart aigrowth-dashboard`

### 3. Setup Firewall
```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

### 4. Auto-Updates
```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## TROUBLESHOOTING

### Website not loading?
```bash
# Check nginx status
systemctl status nginx
# Check nginx error log
tail -f /var/log/nginx/error.log
```

### Dashboard not loading?
```bash
# Check dashboard status
systemctl status aigrowth-dashboard
# Check dashboard logs
journalctl -u aigrowth-dashboard -f
```

### Permission issues?
```bash
chown -R www-data:www-data /var/www/ai-growth-labs
chmod -R 755 /var/www/ai-growth-labs
```

### SSL issues?
```bash
certbot renew --dry-run
```
