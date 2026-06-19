# SETUP GUIDE - TransactIQ Development and Production

## Prerequisites

- Docker & Docker Compose 
- Python 3.11+ (for development)
- Node.js 18+ (for development)
- PostgreSQL 15+ (for development)

## Quick Start (Docker)

### 1. Clone the repository
```bash
cd /Users/jk/Desktop/xeno
```

### 2. Start all services
```bash
docker-compose -f infrastructure/docker-compose.yml up -d
```

### 3. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

### 4. Initialize database
```bash
docker exec transactiq-backend python -c "from app.database import init_db; init_db()"
```

## Development Setup (Local)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://transactiq:transactiq_dev@localhost:5432/transactiq
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
LOG_SQL=true
EOF

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start development server
python main.py
```

The backend will be available at http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_ENVIRONMENT=development
EOF

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

### Database Setup (Local PostgreSQL)

```bash
# Create database
createdb transactiq

# Create user
createuser transactiq --password --interactive
# Enter password: transactiq_dev

# Initialize schema
psql -U transactiq -d transactiq < backend/schema.sql
```

## Production Deployment

### Using Docker Compose

```bash
# Build images
docker-compose -f infrastructure/docker-compose.yml build

# Start services
docker-compose -f infrastructure/docker-compose.yml up -d

# Check logs
docker-compose -f infrastructure/docker-compose.yml logs -f
```

### Using Kubernetes (Helm)

[Helm charts coming soon]

### Manual Deployment

1. **Build Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   npm start
   ```

2. **Start Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

3. **Setup Nginx**
   ```bash
   sudo cp infrastructure/nginx.conf /etc/nginx/sites-available/transactiq
   sudo ln -s /etc/nginx/sites-available/transactiq /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port/0
ENVIRONMENT=production|development
LOG_SQL=true|false
CORS_ORIGINS=http://localhost:3000,https://example.com
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_ENVIRONMENT=production|development
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
docker ps | grep postgres

# Check logs
docker logs transactiq-db

# Recreate database
docker exec transactiq-db dropdb transactiq
docker exec transactiq-db createdb transactiq
```

### Backend API Issues
```bash
# Check API status
curl http://localhost:8000/health

# View logs
docker logs transactiq-backend
```

### Frontend Connection Issues
```bash
# Check if API is accessible
curl http://localhost:8000/api/v1/health

# Clear cache
npm run build
npm start
```

## Documentation

- [API Documentation](http://localhost:8000/docs)
- [Architecture Guide](./ARCHITECTURE.md)
- [Database Schema](./DATABASE.md)
- [Validation Rules](./VALIDATION.md)

## Support

For issues or questions, please contact support@transactiq.com
