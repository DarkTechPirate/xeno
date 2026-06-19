# TransactIQ Architecture

## System Overview

TransactIQ is a modern, scalable enterprise SaaS platform built with:
- **Frontend**: Next.js 14 with React, TypeScript, Tailwind CSS
- **Backend**: FastAPI with Python 3.11+
- **Database**: PostgreSQL 15+
- **Caching**: Redis 7+
- **Processing**: Pandas, Polars
- **Deployment**: Docker, Docker Compose, Kubernetes-ready

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Browser                            │
└────────────────────────┬──────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                       │
│              (SSL Termination, Load Balancing)               │
└────────────────────────┬──────────────────────────────────────┘
            ┌───────────┴────────────┐
            ▼                        ▼
  ┌──────────────────┐    ┌──────────────────────┐
  │  Frontend (SPA)  │    │   Backend API        │
  │  Next.js 14      │    │   FastAPI            │
  │  React + TS      │    │   Async Handlers     │
  │  Tailwind CSS    │    │   CORS Enabled       │
  └────────┬─────────┘    └──────────┬───────────┘
           │                         │
           └────────────┬────────────┘
                        ▼
           ┌────────────────────────┐
           │   API Communication    │
           │   JSON over HTTP/HTTPS │
           └────────────┬───────────┘
                        ▼
        ┌───────────────────────────────────┐
        │      Application Layer            │
        ├───────────────────────────────────┤
        │ • Validation Engines              │
        │ • Correction Engine               │
        │ • Chunking Service                │
        │ • Reporting Service               │
        │ • Analytics Service               │
        └───────────────────────────────────┘
                        │
        ┌───────────────┴────────────────┐
        ▼                                ▼
    ┌─────────────┐            ┌──────────────────┐
    │ PostgreSQL  │            │     Redis        │
    │ Database    │            │     Cache        │
    │             │            │                  │
    │ • Datasets  │            │ • Sessions       │
    │ • Results   │            │ • Temp Data      │
    │ • Errors    │            │ • Queues         │
    │ • Audits    │            │                  │
    └─────────────┘            └──────────────────┘
```

## Component Architecture

### Frontend (Next.js)

```
frontend/
├── app/                          # Next.js App Router
│   ├── page.tsx                 # Landing page
│   ├── upload/                  # Upload page
│   ├── dashboard/               # Dashboard page
│   ├── datasets/                # Datasets listing
│   │   └── [datasetId]/         # Dataset detail
│   └── settings/                # Settings page
├── components/                   # React components
│   ├── Button.tsx               # Base components
│   ├── Card.tsx
│   ├── Badge.tsx
│   ├── MainLayout.tsx           # Layout wrapper
│   ├── QualityScoreGauge.tsx    # Custom components
│   ├── StatCard.tsx
│   └── Tabs.tsx
├── lib/                         # Utilities
│   ├── api.ts                  # API client
│   ├── store.ts                # Zustand store
│   └── utils.ts
├── types/                       # TypeScript types
│   └── index.ts
└── styles/
    └── globals.css             # Tailwind styles
```

### Backend (FastAPI)

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── validators/
│   │   ├── phone_validator.py  # Phone validation
│   │   ├── date_validator.py   # Date validation
│   │   └── validation_engine.py # Main validator
│   ├── engines/
│   │   ├── __init__.py         # Chunking engine
│   │   └── correction_engine.py # Correction engine
│   ├── services/
│   │   └── __init__.py         # Business logic
│   ├── routes/
│   │   └── __init__.py         # API endpoints
│   └── database/
│       └── __init__.py         # DB config
└── main.py                      # FastAPI app
```

## Database Schema

### Core Tables

```sql
-- Datasets table
CREATE TABLE datasets (
  id UUID PRIMARY KEY,
  name VARCHAR NOT NULL,
  filename VARCHAR,
  total_records INTEGER,
  total_columns INTEGER,
  detected_countries JSONB,
  quality_score FLOAT,
  status ENUM,
  created_at TIMESTAMP
);

-- Validation results
CREATE TABLE validation_results (
  id UUID PRIMARY KEY,
  dataset_id UUID REFERENCES datasets,
  valid_records INTEGER,
  invalid_records INTEGER,
  total_errors INTEGER,
  quality_score FLOAT
);

-- Validation errors
CREATE TABLE validation_errors (
  id UUID PRIMARY KEY,
  dataset_id UUID REFERENCES datasets,
  row_number INTEGER,
  field_name VARCHAR,
  error_type VARCHAR,
  error_message TEXT,
  severity ENUM,
  current_value TEXT
);

-- Corrections
CREATE TABLE corrections (
  id UUID PRIMARY KEY,
  dataset_id UUID REFERENCES datasets,
  row_number INTEGER,
  field_name VARCHAR,
  original_value TEXT,
  suggested_value TEXT,
  confidence_score FLOAT,
  is_accepted BOOLEAN
);

-- Chunks
CREATE TABLE dataset_chunks (
  id UUID PRIMARY KEY,
  dataset_id UUID REFERENCES datasets,
  chunk_number INTEGER,
  start_row INTEGER,
  end_row INTEGER,
  file_path VARCHAR
);

-- Audit logs
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  action VARCHAR,
  entity_type VARCHAR,
  entity_id UUID,
  details JSONB,
  created_at TIMESTAMP
);
```

## Validation Pipeline

### 1. Upload & Ingestion
```
CSV Upload
    ↓
Temp File Storage
    ↓
File Size Check
    ↓
Schema Detection
    ↓
Chunk Creation (if > 50MB)
```

### 2. Validation
```
Load Chunk/File
    ↓
Parse Data
    ↓
Row-by-Row Validation
    ├─ Required Fields
    ├─ Format Validation
    ├─ Country Detection
    ├─ Phone Validation
    ├─ Date Validation
    ├─ Payment Validation
    └─ Duplicate Detection
    ↓
Aggregate Errors
    ↓
Calculate Metrics
```

### 3. Auto-Correction
```
Analyze Errors
    ↓
Match Against Rules
    ↓
Generate Suggestions
    ├─ Phone Number Formatting
    ├─ Date Normalization
    ├─ Field Trimming
    └─ Value Standardization
    ↓
Calculate Confidence
    ↓
Store Suggestions
```

### 4. Reporting
```
Aggregate Results
    ↓
Generate Insights
    ↓
Create Report
    ├─ PDF Export
    └─ CSV Export
```

## API Endpoints

### Datasets
- `POST /api/v1/datasets/upload` - Upload CSV
- `GET /api/v1/datasets/{id}` - Get dataset details
- `GET /api/v1/datasets/{id}/results` - Get validation results

### Validation
- `GET /api/v1/datasets/{id}/errors` - List errors (paginated)
- `GET /api/v1/datasets/{id}/corrections` - List corrections
- `POST /api/v1/datasets/{id}/corrections/{id}/action` - Accept/reject correction

### Reports
- `GET /api/v1/datasets/{id}/report/pdf` - Download PDF report
- `GET /api/v1/datasets/{id}/report/csv` - Download CSV report

### Demo
- `GET /api/v1/demo-datasets` - List demo datasets
- `POST /api/v1/demo-datasets/{id}/load` - Load demo dataset

## Data Quality Scoring Algorithm

### Completeness Score (30%)
```
completeness = (records_with_all_fields / total_records) * 100
```

### Accuracy Score (40%)
```
accuracy = (valid_records / total_records) * 100
```

### Consistency Score (20%)
```
consistency = 100 - (duplicate_percentage + schema_mismatches) * 2
```

### Overall Quality Score
```
overall = 
  (completeness * 0.3) +
  (accuracy * 0.4) +
  (consistency * 0.2) +
  (custom_rules * 0.1)
```

## Performance Considerations

### Database Optimization
- Indexing on frequently queried columns
- Partitioning large tables
- Connection pooling
- Query optimization

### Caching Strategy
- Session data in Redis
- Temporary validation results
- API response caching
- Frontend state management

### File Processing
- Streaming CSV parsing
- Chunking for large files
- Async background jobs
- Memory-efficient operations

## Security Architecture

### Authentication & Authorization
- JWT-based session management
- Role-based access control (RBAC)
- API key authentication
- Rate limiting

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PII masking in logs
- Secure password hashing (bcrypt)

### Compliance
- GDPR compliance
- Audit trail logging
- Data retention policies
- Access control logs

## Deployment Topology

### Development
- Single Docker container per service
- Local PostgreSQL
- Hot reload enabled

### Staging
- Replicated services (2+)
- Managed PostgreSQL
- SSL certificates
- Staging DNS

### Production
- Load-balanced services
- Auto-scaling enabled
- RDS PostgreSQL
- CloudFront CDN
- WAF protection
- Monitoring & alerting

## Monitoring & Observability

### Metrics
- Request latency
- Error rates
- Processing time
- Memory usage
- CPU usage

### Logging
- Structured JSON logging
- Centralized log aggregation
- Log retention policies
- Error tracking

### Health Checks
- API health endpoints
- Database connectivity
- Redis connectivity
- File system checks

## Future Enhancements

- [ ] Machine learning for auto-correction
- [ ] Advanced analytics dashboard
- [ ] Real-time validation streaming
- [ ] Webhook integrations
- [ ] GraphQL API
- [ ] Multi-tenancy support
- [ ] Advanced audit controls
- [ ] Custom validation UI builder
