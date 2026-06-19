# TransactIQ - Enterprise Transaction Validation & Data Quality Intelligence Platform

A production-grade SaaS platform for validating, cleaning, and analyzing transaction datasets with enterprise-grade accuracy.

## 🎯 Features

### Core Capabilities
- **CSV Upload & Processing** - Drag-and-drop upload with auto-chunking for large files (100k+ rows)
- **Multi-Level Validation** - Order, product, payment, and compliance checks
- **Country-Specific Phone Validation** - Configurable rules for 50+ countries
- **Date/Time Format Validation** - Flexible format detection and validation
- **Data Integrity Checks** - Duplicate detection, schema validation, type checking

### Advanced Features
- **Dataset Health Analyzer** - Auto-detect schema, columns, countries, duplicates
- **Data Quality Scoring** - Completeness, accuracy, consistency metrics (0-100%)
- **AI-Powered Auto-Correction** - Intelligent suggestions with confidence scores
- **Interactive Validation Dashboard** - Real-time error explorer with search/filters
- **Audit & Compliance Reports** - PDF/CSV exports with full validation history
- **Enterprise Rule Engine** - Custom validation rules, regex patterns, format configs
- **Chunk Management** - Visual chunking, individual chunk downloads, statistics
- **Root Cause Analysis** - AI insights on failure patterns and recommendations

### Demo Mode
8 pre-loaded datasets for immediate testing:
1. **Perfect Dataset** - 100% valid records
2. **Phone Validation Dataset** - Country-specific phone errors
3. **Date Validation Dataset** - Invalid timestamps and formats
4. **Mixed Country Dataset** - India, Singapore, USA, UK scenarios
5. **Duplicate Orders Dataset** - Duplicate detection scenarios
6. **Payment Integrity Dataset** - Invalid payment modes
7. **Large Scale Dataset** - 100,000+ rows
8. **Real World Dirty Dataset** - Mixed realistic issues

## 🏗️ Architecture

```
TransactIQ/
├── backend/                 # FastAPI + Python
│   ├── app/
│   │   ├── models/         # SQLAlchemy models + Pydantic schemas
│   │   ├── validators/     # Validation logic by domain
│   │   ├── engines/        # Correction & chunking engines
│   │   ├── services/       # Business logic & orchestration
│   │   ├── routes/         # API endpoints
│   │   └── database/       # PostgreSQL setup
│   ├── requirements.txt
│   └── main.py
├── frontend/                # Next.js + TypeScript + Tailwind
│   ├── app/                # Next.js App Router
│   ├── components/         # React components (ShadCN)
│   ├── types/              # TypeScript interfaces
│   ├── lib/                # Utilities & API clients
│   └── package.json
├── shared/                  # Shared types & constants
├── infrastructure/          # Docker & deployment configs
└── demo_datasets/          # Pre-loaded demo data

```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 🗄️ Database

PostgreSQL with comprehensive schema for:
- Datasets & metadata
- Validation results & error tracking
- Corrections & suggestions
- Audit logs & compliance
- User settings & preferences

## 🔧 Technology Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, ShadCN/ui
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy ORM
- **Data Processing**: Pandas, Polars, NumPy
- **Database**: PostgreSQL 15+
- **Deployment**: Docker, Docker Compose
- **Reports**: ReportLab (PDF), CSV exports

## 📊 Data Quality Scoring

Algorithmic quality scoring combining:
- **Completeness**: (records_with_all_fields / total_records) * 100
- **Accuracy**: Based on format validation & business rule compliance
- **Consistency**: Schema adherence & data type consistency
- **Overall**: Weighted combination of above metrics

## 🤖 Auto-Correction Examples

| Issue | Current | Suggested | Confidence |
|-------|---------|-----------|------------|
| Phone | 987654321 | 9876543210 (IN) | 95% |
| Date | 2025/31/12 | 31/12/2025 | 88% |
| Country | IND | India | 99% |
| Status | invoiced | INVOICED | 92% |

## 📦 Deployment

Docker-based deployment with:
- Multi-stage builds for optimization
- Environment-based configuration
- Health checks & monitoring
- Horizontal scaling support

```bash
docker-compose up -d
```

## 📝 API Examples

### Upload Dataset
```bash
curl -X POST http://localhost:8000/api/v1/datasets/upload \
  -F "file=@transactions.csv"
```

### Get Validation Results
```bash
curl http://localhost:8000/api/v1/datasets/{dataset_id}/results
```

### Download Report
```bash
curl http://localhost:8000/api/v1/datasets/{dataset_id}/report/pdf \
  -o report.pdf
```

## 🎨 UI/UX Philosophy

- **Enterprise Design** - Similar to Stripe, Notion, Linear, Datadog
- **Light Theme First** - Clean, professional appearance
- **Minimalist** - Excellent whitespace, clear hierarchy
- **Responsive** - Mobile-first, accessible (WCAG 2.1 AA)
- **Smooth** - Micro-interactions, skeleton loaders, animations
- **Intuitive** - Zero learning curve for enterprise users

## 📊 Performance

- **Upload Handling**: Automatic chunking for files >50MB
- **Validation Speed**: ~10,000 rows/second on standard hardware
- **Correction Suggestions**: AI-powered with <100ms response time
- **Report Generation**: PDF generation in <2s for 100k records
- **Query Performance**: Optimized with PostgreSQL indexing

## 🔒 Security & Compliance

- CSRF protection
- Rate limiting per user/IP
- Data encryption at rest (PostgreSQL)
- Audit trail for all operations
- GDPR-compliant data handling
- Password hashing (bcrypt)

## 📞 Support

For issues, feature requests, or enterprise inquiries, please contact support@transactiq.com

---

**TransactIQ** - Transform Raw Data Into Business-Ready Insights
