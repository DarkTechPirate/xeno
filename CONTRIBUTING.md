# Contributing to TransactIQ

## 🎯 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct.

## 💡 How to Contribute

### 1. Report Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one.

**To submit a bug report, create an issue and include:**

- A clear, descriptive title
- Description of the exact steps which reproduce the problem
- Specific examples to demonstrate the steps
- Expected behavior vs. actual behavior
- Screenshots and/or animated GIFs
- Your environment (OS, Python version, Node version, etc.)

### 2. Suggest Enhancements

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide:

- A clear, descriptive title
- A step-by-step description of the suggested enhancement
- Specific examples to demonstrate the steps
- Screenshots and/or mockups
- Why this enhancement would be useful

### 3. Pull Requests

- Fill in the required template
- Follow the JavaScript/Python styleguides
- End all files with a newline
- Ensure all tests pass
- Increase version numbers in any examples files

## 📝 Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Backend Development

```bash
# Clone repository
git clone https://github.com/your-org/transactiq.git
cd transactiq

# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Setup environment
cp .env.example .env

# Start development server
python main.py
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local

# Start dev server
npm run dev
```

### Using Docker

```bash
# Start all services
docker-compose -f infrastructure/docker-compose.yml up -d

# View logs
docker-compose -f infrastructure/docker-compose.yml logs -f
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_phone_validator.py

# Run with verbosity
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run e2e tests
npm run test:e2e
```

## 📚 Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

```bash
# Format code
pip install black
black app/

# Lint code
pip install flake8
flake8 app/

# Type check
pip install mypy
mypy app/
```

### TypeScript/JavaScript (Frontend)

- Use ESLint configuration
- Use Prettier for formatting
- Use TypeScript strict mode
- Use meaningful variable names

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check
```

## 🔄 Git Workflow

### Branches

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `refactor/*` - Refactoring branches

### Commit Messages

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance
- `test`: Adding or updating tests

Example:

```
feat(phone-validator): add country-specific validation

- Add support for 10 additional countries
- Improve error messages
- Add comprehensive test cases

Fixes #123
```

### Creating a Pull Request

1. Create a new branch from `develop`
2. Make your changes
3. Add or update tests
4. Ensure all tests pass
5. Commit with conventional messages
6. Push to your fork
7. Open a pull request to `develop`

## 📋 Pull Request Checklist

- [ ] I have read the CONTRIBUTING guide
- [ ] My code follows the code style of this project
- [ ] I have updated the documentation accordingly
- [ ] I have added tests to cover my changes
- [ ] All new and existing tests passed
- [ ] My branch is up to date with the base branch

## 🔍 Code Review Process

1. Submit your PR
2. Maintainers review your changes
3. Address any feedback
4. Once approved, your PR will be merged

## 📦 Release Process

1. Update version numbers (MAJOR.MINOR.PATCH)
2. Update CHANGELOG.md
3. Create a git tag
4. Push to production
5. Announce release

## 🚀 Project Structure

```
transactiq/
├── backend/
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── validators/  # Validation logic
│   │   ├── engines/     # Processing engines
│   │   ├── services/    # Business logic
│   │   ├── routes/      # API endpoints
│   │   └── database/    # DB configuration
│   ├── tests/           # Test suite
│   └── main.py          # FastAPI app
├── frontend/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   ├── lib/            # Utilities
│   ├── types/          # TypeScript types
│   └── styles/         # CSS styles
├── infrastructure/      # Docker configs
├── demo_datasets/      # Sample data
└── docs/              # Documentation
```

## 🤝 Community

- **GitHub Discussions**: General questions
- **GitHub Issues**: Bug reports and feature requests
- **Slack Community**: Real-time chat
- **Email**: dev@transactiq.com

## 📖 Additional Resources

- [Architecture Overview](./ARCHITECTURE.md)
- [Setup Guide](./SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Quick Start](./QUICKSTART.md)

## 📄 License

By contributing to TransactIQ, you agree that your contributions will be licensed under its license.

---

Thank you for contributing to TransactIQ! 🙏
