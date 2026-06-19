# TransactIQ Server Deployment Guide

**Status**: ✅ **Backend is COMPLETE and production-ready for server deployment**

## Quick Overview

Your TransactIQ project has:
- ✅ **Backend**: Complete FastAPI application with all API endpoints
- ✅ **Frontend**: Complete Next.js React SPA
- ✅ **Infrastructure**: Docker/Docker Compose ready
- ✅ **Database**: PostgreSQL models with proper schema
- ✅ **Documentation**: Comprehensive guides
- ✅ **CI/CD**: GitHub Actions pipeline

**Ready to deploy on any server!**

---

## 🚀 Deployment Options

### Option 1: Simple Server Deployment (Linux/Ubuntu)

#### Prerequisites
```bash
- Linux server (Ubuntu 20.04+ or similar)
- Docker & Docker Compose installed
- Domain name (optional)
- SSH access to server
```

#### Step 1: Connect to Server
```bash
ssh user@your-server-ip
cd /opt
```

#### Step 2: Clone or Copy Project
```bash
# Option A: Clone from GitHub
git clone https://github.com/your-org/transactiq.git
cd transactiq

# Option B: Copy via SCP
scp -r /Users/jk/Desktop/xeno user@your-server-ip:/opt/transactiq
cd /opt/transactiq
```

#### Step 3: Create Production Environment Files
```bash
# Backend environment
cat > backend/.env << EOF
DATABASE_URL=postgresql://transactiq:secure_password@postgres:5432/transactiq
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=$(openssl rand -base64 32)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

# Frontend environment
cat > frontend/.env.production << EOF
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_ENVIRONMENT=production
EOF
```

#### Step 4: Deploy with Docker Compose
```bash
# Start all services
docker-compose -f infrastructure/docker-compose.yml up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

#### Step 5: Initialize Database
```bash
# Run database migrations
docker-compose exec -T backend python -c "from app.database import init_db; init_db()"

# Verify database connection
docker-compose exec postgres psql -U transactiq -d transactiq -c "SELECT version();"
```

---

### Option 2: AWS EC2 Deployment

#### Step 1: Create EC2 Instance
```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups transactiq-sg \
  --subnet-id subnet-xxxxx
```

#### Step 2: Connect and Install Docker
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 3: Deploy Project
```bash
# Follow Option 1 steps from "Clone or Copy Project" onwards
```

---

### Option 3: Railway.app Deployment (Recommended for Quick Setup)

1. Push to GitHub: `git push origin main`
2. Visit [Railway.app](https://railway.app)
3. Click "New Project"
4. Select "Deploy from GitHub"
5. Choose repository
6. Add environment variables (DATABASE_URL, REDIS_URL, etc.)
7. Deploy!

---

### Option 4: Render.com Deployment

1. Push to GitHub
2. Visit [Render.com](https://render.com)
3. Create new "Web Service"
4. Connect GitHub repo
5. Set environment variables
6. Deploy!

---

## 🌐 Domain & SSL Setup

### Using Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot certify -d yourdomain.com -d api.yourdomain.com

# Auto-renew (runs automatically)
sudo certbot renew --dry-run
```

### DNS Configuration

Add these DNS records:
```
yourdomain.com      A       your-server-ip
api.yourdomain.com  A       your-server-ip
```

---

## 📊 Production Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/transactiq
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<generate-random-string>
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=https://yourdomain.com

# File Storage (optional S3)
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_STORAGE_BUCKET_NAME=transactiq-files
```

### Frontend (.env.production)
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## 🔍 Health Checks

After deployment, verify everything is working:

```bash
# Check backend health
curl https://api.yourdomain.com/

# Check API docs
curl https://api.yourdomain.com/docs

# Check frontend
curl https://yourdomain.com

# Check database connection
docker-compose exec postgres psql -U transactiq -d transactiq -c "SELECT COUNT(*) FROM datasets;"

# Check Redis
docker-compose exec redis redis-cli ping
```

---

## 📈 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Resource Usage
```bash
# Monitor containers
docker stats

# Check disk space
df -h

# Check memory
free -h
```

---

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild Docker images
docker-compose build

# Restart services
docker-compose restart
```

### Database Backup
```bash
# Create backup
docker-compose exec -T postgres pg_dump -U transactiq transactiq > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U transactiq transactiq < backup.sql
```

### Database Maintenance
```bash
# Vacuum and analyze
docker-compose exec -T postgres psql -U transactiq transactiq -c "VACUUM ANALYZE;"

# Check database size
docker-compose exec -T postgres psql -U transactiq transactiq -c "SELECT pg_size_pretty(pg_database_size('transactiq'));"
```

---

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.connect())"

# Restart
docker-compose restart backend
```

### Frontend won't build
```bash
# Clear cache
docker-compose down
docker system prune -a

# Rebuild
docker-compose up -d --build frontend
```

### Database connection failed
```bash
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Check credentials in backend/.env
cat backend/.env | grep DATABASE_URL
```

### High memory usage
```bash
# Check memory stats
docker stats

# Restart containers
docker-compose restart

# Increase server resources if needed
```

---

## 📋 Post-Deployment Checklist

- [ ] Backend API responding (`/api/v1/`)
- [ ] Frontend loading (`https://yourdomain.com`)
- [ ] Database initialized and accessible
- [ ] Redis cache working
- [ ] SSL certificate installed
- [ ] DNS records configured
- [ ] Backup strategy in place
- [ ] Monitoring set up
- [ ] Logs being collected
- [ ] Auto-renewal for SSL certificate configured

---

## 🎯 Testing Deployment

### Test Upload Endpoint
```bash
# Create a test CSV
cat > test.csv << EOF
transaction_id,phone,date,amount,country
1,+919876543210,2024-01-15,1000,IN
2,+6598765432,2024-01-16,2000,SG
EOF

# Upload
curl -X POST https://api.yourdomain.com/api/v1/datasets/upload \
  -F "file=@test.csv" \
  -F "name=Test Dataset"
```

### Test Demo Datasets
```bash
# List demo datasets
curl https://api.yourdomain.com/api/v1/demo-datasets

# Load a demo
curl -X POST https://api.yourdomain.com/api/v1/demo-datasets/1/load
```

---

## 📞 Support Commands

### Service Management
```bash
# Stop services
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart

# Bring down (remove containers)
docker-compose down

# Bring up with rebuild
docker-compose up -d --build
```

### Database Access
```bash
# Access psql shell
docker-compose exec postgres psql -U transactiq -d transactiq

# List tables
docker-compose exec -T postgres psql -U transactiq -d transactiq -c "\dt"

# Describe table
docker-compose exec -T postgres psql -U transactiq -d transactiq -c "\d datasets"
```

### View API Status
```bash
# Backend API
curl -s https://api.yourdomain.com/ | jq

# API docs
curl -s https://api.yourdomain.com/docs
```

---

## 🔐 Security Best Practices

1. **Use strong DATABASE_URL password**
   ```bash
   openssl rand -base64 32
   ```

2. **Restrict CORS origins**
   ```
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Enable HTTPS/SSL**
   - Use Let's Encrypt (free)
   - Set up auto-renewal

4. **Keep secrets safe**
   - Never commit `.env` files
   - Use environment variables
   - Rotate keys periodically

5. **Set up firewalls**
   ```bash
   # Allow only necessary ports
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ```

6. **Monitor logs for errors**
   ```bash
   docker-compose logs -f | grep -i error
   ```

---

## 📊 Performance Optimization

### Database
- Add indexes on frequently queried columns
- Use connection pooling (already configured)
- Regular VACUUM ANALYZE

### Frontend
- Enable gzip compression (nginx configured)
- Use CDN for static files
- Minify CSS/JS

### Backend
- Cache frequently accessed data (Redis configured)
- Use async/await (FastAPI native)
- Optimize database queries

---

## 📞 Getting Help

- **API Documentation**: `https://api.yourdomain.com/docs`
- **Architecture Guide**: See `ARCHITECTURE.md`
- **Setup Guide**: See `SETUP.md`
- **GitHub Issues**: Check project repo for known issues

---

## ✅ Deployment Status

**Backend**: ✅ COMPLETE
- All models defined
- All validators implemented
- All services configured
- All endpoints ready
- Database schema ready

**Frontend**: ✅ COMPLETE
- All pages built
- All components created
- API client configured
- Styling complete

**Infrastructure**: ✅ COMPLETE
- Docker images ready
- Docker Compose configured
- Nginx proxy configured
- SSL ready

**Ready for production deployment!**

---

## Next Steps

1. ✅ Set up server (EC2, DigitalOcean, Render, etc.)
2. ✅ Deploy project with Docker Compose
3. ✅ Configure domain & SSL
4. ✅ Initialize database
5. ✅ Test all endpoints
6. ✅ Set up monitoring
7. ✅ Configure backups
8. ✅ Go live! 🎉

---

**For detailed deployment options, see [DEPLOYMENT.md](./DEPLOYMENT.md)**
