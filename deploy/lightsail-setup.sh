#!/bin/bash
# AWS Lightsail Deployment Script for arnetrice.com
# This script sets up your Ubuntu instance on AWS Lightsail

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.12 and required packages
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
sudo apt-get install -y postgresql-client nginx certbot python3-certbot-nginx git

# Clone your repository (you'll need to set this up)
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/arnetrice.git
cd arnetrice

# Create Python virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file for the app
sudo tee /etc/systemd/system/arnetrice.service > /dev/null <<EOF
[Unit]
Description=Arnetrice.com FastAPI Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/arnetrice
Environment="PATH=/home/ubuntu/arnetrice/venv/bin"
ExecStart=/home/ubuntu/arnetrice/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx as reverse proxy
sudo tee /etc/nginx/sites-available/arnetrice > /dev/null <<'EOF'
server {
    listen 80;
    server_name arnetrice.com www.arnetrice.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    client_max_body_size 10M;
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/arnetrice /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Start and enable the application
sudo systemctl daemon-reload
sudo systemctl start arnetrice
sudo systemctl enable arnetrice

# Set up SSL with Let's Encrypt (run after DNS is pointed)
# sudo certbot --nginx -d arnetrice.com -d www.arnetrice.com

echo "Deployment complete! Next steps:"
echo "1. Update your .env.prod file with database credentials"
echo "2. Point your domain DNS to this server's IP"
echo "3. Run SSL setup: sudo certbot --nginx -d arnetrice.com -d www.arnetrice.com"