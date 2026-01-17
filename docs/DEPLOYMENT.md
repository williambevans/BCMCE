# BCMCE Platform Deployment Guide

## Overview

This guide covers deploying the BCMCE platform for development, staging, and production environments.

## Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.11+, PostgreSQL 16+, Redis 7+
- Git
- Domain name (for production)
- SSL certificate (for production)

## Quick Start with Docker

### 1. Clone Repository

```bash
git clone https://github.com/williambevans/BCMCE.git
cd BCMCE
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

**Important variables to set:**
```bash
POSTGRES_PASSWORD=your_secure_password
API_SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 3. Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI backend (port 8000)

### 4. Initialize Database

```bash
docker-compose exec postgres psql -U bcmce_user -d bcmce -f /docker-entrypoint-initdb.d/001_create_tables.sql
```

### 5. Seed Data (Optional)

```bash
# Load sample materials and suppliers
docker-compose exec api python -c "
from data.seed import load_materials, load_suppliers
load_materials()
load_suppliers()
"
```

### 6. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/api/docs
```

## Manual Installation (Without Docker)

### 1. Install Dependencies

```bash
# Install PostgreSQL 16
sudo apt-get install postgresql-16

# Install Redis
sudo apt-get install redis-server

# Install Python dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configure PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE bcmce;
CREATE USER bcmce_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bcmce TO bcmce_user;
\q
```

### 3. Initialize Database

```bash
psql -U bcmce_user -d bcmce -f data/migrations/001_create_tables.sql
```

### 4. Start Services

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start API
cd backend
uvicorn main:app --reload
```

## GitHub Pages Deployment (Frontend Only)

The landing page is automatically deployed to GitHub Pages when you push to the main branch.

### Enable GitHub Pages

1. Go to repository settings
2. Navigate to Pages section
3. Set source to "Deploy from branch"
4. Select branch: `main` or `claude/bcmce-platform-build-nmObJ`
5. Select folder: `/ (root)`
6. Save

Your site will be available at: `https://williambevans.github.io/BCMCE/`

### Custom Domain (Optional)

1. Add a `CNAME` file in the repository root:
```bash
echo "bcmce.com" > CNAME
git add CNAME
git commit -m "Add custom domain"
git push
```

2. Configure DNS:
```
Type: CNAME
Name: www
Value: williambevans.github.io
```

## Production Deployment

### Recommended: DigitalOcean/AWS/Azure

#### 1. Provision Server

- 2 vCPU, 4GB RAM minimum
- Ubuntu 22.04 LTS
- PostgreSQL managed database (recommended)
- Redis managed cache (recommended)

#### 2. Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 3. Configure Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

#### 4. Deploy with Docker Compose

```bash
# Clone repository
git clone https://github.com/williambevans/BCMCE.git
cd BCMCE

# Configure production environment
cp .env.example .env
nano .env

# Set production values
API_DEBUG=False
CORS_ORIGINS=https://bcmce.com,https://www.bcmce.com

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### 5. Configure Nginx Reverse Proxy

```bash
sudo apt-get install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/bcmce
```

```nginx
server {
    listen 80;
    server_name bcmce.com www.bcmce.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/bcmce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Configure SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d bcmce.com -d www.bcmce.com
```

## Monitoring & Logging

### View Logs

```bash
# API logs
docker-compose logs -f api

# Database logs
docker-compose logs -f postgres

# All services
docker-compose logs -f
```

### Health Checks

```bash
# API health
curl https://bcmce.com/health

# Database connection
docker-compose exec postgres pg_isready -U bcmce_user

# Redis connection
docker-compose exec redis redis-cli ping
```

## Backup & Restore

### Database Backup

```bash
# Automated daily backup
docker-compose exec postgres pg_dump -U bcmce_user bcmce > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U bcmce_user bcmce < backup_20260117.sql
```

### Automated Backups with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /home/user/BCMCE && docker-compose exec -T postgres pg_dump -U bcmce_user bcmce > /backups/bcmce_$(date +\%Y\%m\%d).sql
```

## Scaling Considerations

### Database Scaling
- Use PostgreSQL replication for read replicas
- Consider TimescaleDB for time-series pricing data
- Implement connection pooling (PgBouncer)

### Application Scaling
- Deploy multiple API instances behind load balancer
- Use Redis for session management and caching
- Implement CDN for static assets

### Monitoring
- Set up Sentry for error tracking
- Use Prometheus + Grafana for metrics
- Configure uptime monitoring (UptimeRobot)

## Troubleshooting

### API Won't Start

```bash
# Check logs
docker-compose logs api

# Verify database connection
docker-compose exec postgres psql -U bcmce_user -d bcmce -c "SELECT 1;"

# Rebuild container
docker-compose build api
docker-compose up -d api
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
docker-compose exec api python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
print(engine.connect())
"
```

### GitHub Pages Not Updating

- Check Actions tab for deployment errors
- Ensure `index.html` is in repository root
- Verify Pages is enabled in settings
- Clear browser cache

## Security Checklist

- [ ] Change default passwords in `.env`
- [ ] Generate strong SECRET_KEY values
- [ ] Enable HTTPS in production
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Monitor access logs

## Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review documentation: `/docs`
- Open issue: https://github.com/williambevans/BCMCE/issues
