# Deployment Guide for arnetrice.com on AWS Lightsail

## Total Monthly Cost: ~$25
- Lightsail Instance (1GB): $10/month
- Lightsail PostgreSQL Database: $15/month

## Step-by-Step Deployment

### 1. Create AWS Account
- Go to https://aws.amazon.com
- Sign up (you'll need a credit card)
- You get some free credits for new accounts

### 2. Create Lightsail Instance
1. Go to AWS Lightsail Console: https://lightsail.aws.amazon.com/
2. Click "Create instance"
3. Select:
   - Region: Choose closest to your customers (e.g., Virginia for East Coast)
   - Platform: Linux/Unix
   - Blueprint: "OS Only" → Ubuntu 22.04 LTS
   - Instance Plan: $10/month (1 GB RAM, 1 vCPU, 40 GB SSD)
   - Name it: "arnetrice-app"
4. Click "Create instance"

### 3. Create Lightsail Database
1. In Lightsail Console, click "Databases" tab
2. Click "Create database"
3. Select:
   - PostgreSQL
   - Standard plan: $15/month
   - Name it: "arnetrice-db"
4. Click "Create database"
5. Wait 10-15 minutes for it to be ready
6. Note down:
   - Endpoint (hostname)
   - Port (5432)
   - Username (postgres)
   - Password (you set this)

### 4. Connect to Your Instance
1. In Lightsail Console, click on your instance
2. Click "Connect using SSH" (opens in browser)
3. Run these commands:
```bash
# Download and run the setup script
wget https://raw.githubusercontent.com/YOUR_USERNAME/arnetrice/main/deploy/lightsail-setup.sh
chmod +x lightsail-setup.sh
./lightsail-setup.sh
```

### 5. Configure Environment
1. SSH into your instance
2. Edit the production environment file:
```bash
cd /home/ubuntu/arnetrice
nano .env.prod
```
3. Update these values:
```
DB_HOST=your-database-endpoint.region.rds.amazonaws.com
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=your-database-password
DB_NAME=arnetrice_db
BASE_URL=https://arnetrice.com
```

### 6. Point Your Domain (Namecheap to AWS)
1. In Lightsail Console, go to your instance
2. Go to "Networking" tab
3. Create a Static IP (free while attached)
4. Note the IP address (e.g., 54.123.45.67)

5. Go to Namecheap.com:
   - Login to your account
   - Go to Domain List → Manage (next to arnetrice.com)
   - Click "Advanced DNS"
   - Add/Edit these records:
   ```
   Type: A Record    Host: @       Value: 54.123.45.67
   Type: A Record    Host: www     Value: 54.123.45.67
   ```
6. Save changes (DNS updates take 15-30 minutes)

### 7. Set Up SSL Certificate (HTTPS)
After DNS propagates (check with: `ping arnetrice.com`):
```bash
sudo certbot --nginx -d arnetrice.com -d www.arnetrice.com
```
Enter your email when prompted and agree to terms.

### 8. Verify Everything Works
1. Visit https://arnetrice.com
2. Test the checkout flow
3. Check that Stripe redirects work properly

## Monitoring Your Site

### Check application logs:
```bash
sudo journalctl -u arnetrice -f
```

### Restart application after changes:
```bash
sudo systemctl restart arnetrice
```

### Update code from Git:
```bash
cd /home/ubuntu/arnetrice
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart arnetrice
```

## Backup Strategy
- Database: Lightsail automatically backs up daily (7-day retention)
- Code: Keep everything in Git

## Support
- AWS Lightsail Support: https://lightsail.aws.amazon.com/ls/docs/
- Check logs if something goes wrong
- The setup is portable - you can move to any Linux server