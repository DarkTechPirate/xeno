# Production Deployment Guide - TransactIQ

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database backups enabled
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Email notifications setup
- [ ] Monitoring alerts configured
- [ ] Security audit completed
- [ ] Load testing performed

## Deployment Options

## Option 1: Docker Compose (Single Server)

### 1. Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/transactiq
cd /opt/transactiq
```

### 2. Deploy Application

```bash
# Clone or copy repository
git clone https://github.com/your-org/transactiq.git .

# Create production environment files
cat > backend/.env << EOF
DATABASE_URL=postgresql://user:password@postgres:5432/transactiq
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=production
SECRET_KEY=<generate-random-key>
EOF

cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENVIRONMENT=production
EOF

# Start services
docker-compose -f infrastructure/docker-compose.yml up -d

# Run database migrations
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### 3. Configure SSL

```bash
# Using Let's Encrypt with Certbot
sudo apt-get install certbot python3-certbot-nginx

sudo certbot certify -d yourdomain.com -d api.yourdomain.com

# Update nginx configuration with certificates
```

## Option 2: AWS ECS (Recommended for Scale)

### 1. Create AWS Resources

```bash
# Create RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier transactiq-prod \
  --db-instance-class db.t3.small \
  --engine postgres \
  --master-username transactiq \
  --allocated-storage 100 \
  --vpc-security-group-ids sg-xxxxx

# Create ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id transactiq-redis \
  --cache-node-type cache.t3.small \
  --engine redis

# Create ALB (Application Load Balancer)
aws elbv2 create-load-balancer \
  --name transactiq-alb \
  --subnets subnet-xxxxx subnet-xxxxx
```

### 2. Build and Push Docker Images

```bash
# Create ECR repositories
aws ecr create-repository --repository-name transactiq/backend
aws ecr create-repository --repository-name transactiq/frontend

# Build and push images
docker build -t transactiq/backend:latest -f infrastructure/Dockerfile.backend .
docker tag transactiq/backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/transactiq/backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/transactiq/backend:latest

# Repeat for frontend
```

### 3. Create ECS Tasks and Services

```bash
# Create task definitions
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create services
aws ecs create-service \
  --cluster transactiq-prod \
  --service-name transactiq-backend \
  --task-definition transactiq-backend:1 \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:...,containerName=backend,containerPort=8000
```

## Option 3: Kubernetes (Helm)

### 1. Create Kubernetes Cluster

```bash
# Using AWS EKS
eksctl create cluster --name transactiq-prod --version 1.27 --region us-east-1

# Configure kubectl
aws eks update-kubeconfig --name transactiq-prod --region us-east-1
```

### 2. Install Helm Chart

```bash
# Create values file
cat > values.yaml << EOF
environment: production
domain: yourdomain.com

frontend:
  replicas: 3
  image: transactiq/frontend:latest

backend:
  replicas: 3
  image: transactiq/backend:latest
  
database:
  host: transactiq-db.xxxxx.rds.amazonaws.com
  name: transactiq

redis:
  host: transactiq-redis.xxxxx.ng.0001.use1.cache.amazonaws.com
EOF

# Install
helm repo add transactiq https://charts.transactiq.com
helm install transactiq transactiq/transactiq -f values.yaml
```

## Environment Configuration for Production

### Backend (.env)

```
# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/transactiq
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://prod-redis:6379/0

# Security
SECRET_KEY=<random-64-character-string>
HASH_ALGORITHM=bcrypt
CORS_ORIGINS=https://yourdomain.com

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# File Storage (use S3 in production)
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_STORAGE_BUCKET_NAME=transactiq-files
USE_S3_STORAGE=true

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=xxxxx

# Validation
PHONE_VALIDATION_ENABLED=true
DATE_VALIDATION_ENABLED=true
DUPLICATE_DETECTION_ENABLED=true
```

### Frontend (.env.production)

```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_ANALYTICS_ID=GA-XXXXX
```

## Database Setup

### Backup Strategy

```bash
# Automated daily backups
0 2 * * * pg_dump -U transactiq -d transactiq | gzip > /backups/transactiq-$(date +\%Y\%m\%d).sql.gz

# Backup to S3
0 3 * * * aws s3 cp /backups/transactiq-$(date +\%Y\%m\%d).sql.gz s3://transactiq-backups/
```

### High Availability Setup

```bash
# Use PostgreSQL replication
# Primary-Standby setup with automatic failover
# Configure streaming replication with slots

# Connection string with failover
postgresql://user:password@primary-db:5432,standby-db:5432/transactiq?target_session_attrs=read-write
```

## Monitoring & Observability

### CloudWatch Metrics

```bash
# Create custom metrics
aws cloudwatch put-metric-data \
  --namespace TransactIQ \
  --metric-name ValidationLatency \
  --value 150 \
  --unit Milliseconds
```

### Application Monitoring

```python
# In backend main.py
from prometheus_client import Counter, Histogram

validation_counter = Counter('validations_total', 'Total validations')
validation_duration = Histogram('validation_duration_seconds', 'Validation duration')

@app.get('/metrics')
async def metrics():
    return generate_latest()
```

### Log Aggregation

```bash
# Using ELK Stack or CloudWatch Logs
# Configure log groups
aws logs create-log-group --log-group-name /transactiq/backend
aws logs create-log-group --log-group-name /transactiq/frontend
```

## Security Hardening

### 1. Network Security

```bash
# Security Groups
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Restrict database access
aws ec2 authorize-security-group-ingress \
  --group-id sg-db \
  --protocol tcp \
  --port 5432 \
  --source-security-group-id sg-app
```

### 2. Secrets Management

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name transactiq/db-password \
  --secret-string "your-secure-password"

# Reference in application
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='transactiq/db-password')
```

### 3. SSL/TLS Configuration

```bash
# Generate strong certificate
certbot certonly -d yourdomain.com --agree-tos --no-eff-email

# Update nginx with A+ SSL rating
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

## Load Testing

```bash
# Using Apache Bench
ab -n 10000 -c 100 https://yourdomain.com/

# Using JMeter for comprehensive testing
jmeter -n -t transactiq-load-test.jmx -l results.csv
```

## Rollback Strategy

```bash
# Keep previous versions available
docker-compose -f infrastructure/docker-compose.yml.v1.0 pull
docker-compose -f infrastructure/docker-compose.yml.v1.0 up -d

# For Kubernetes
kubectl rollout undo deployment/transactiq-backend
kubectl rollout history deployment/transactiq-backend
```

## Maintenance

### Regular Updates

```bash
# Update dependencies
npm update --production
pip install --upgrade -r requirements.txt

# Run security checks
npm audit
pip install safety && safety check
```

### Database Maintenance

```bash
# Vacuum and analyze
VACUUM ANALYZE;

# Reindex if needed
REINDEX DATABASE transactiq;
```

### Monitoring Tasks

```bash
# Daily checks
- Verify backups completed
- Check error logs
- Monitor resource usage
- Verify SSL certificates (30 days before expiry)
```

## Disaster Recovery

### Backup Recovery

```bash
# Restore from backup
dropdb transactiq
createdb transactiq
gunzip -c /backups/transactiq-20240101.sql.gz | psql -U transactiq -d transactiq
```

### High Availability Setup

```bash
# Implement multi-region failover
# Primary region: US-EAST-1
# Failover region: US-WEST-2
# Route53 health checks for automatic failover
```

## Cost Optimization

### AWS Cost Reduction

- Use Reserved Instances (40% savings)
- Implement auto-scaling
- Use CloudFront for static files
- Archive old logs to S3 Glacier
- Use spot instances for batch jobs

## Troubleshooting Production Issues

### High Latency

```bash
# Check database performance
EXPLAIN ANALYZE SELECT * FROM datasets;

# Monitor slow queries
enable_slow_query_log = true

# Check API metrics
curl https://api.yourdomain.com/metrics
```

### Memory Leaks

```bash
# Monitor container memory
docker stats

# Restart if needed
docker-compose restart backend
```

### Database Connection Issues

```bash
# Check connection pool
SELECT * FROM pg_stat_activity;

# Restart connection pool
# Adjust pool settings in backend/.env
```

## Support & Escalation

For production issues, contact:
- **Email**: support@transactiq.com
- **Slack**: #transactiq-support
- **PagerDuty**: Auto-escalation for critical alerts
