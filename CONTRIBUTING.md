# Contributing to BCMCE Platform

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                 BOSQUE COUNTY MINERAL & COMMODITIES EXCHANGE             ║
║                          Contribution Guidelines                         ║
║                                                                           ║
║   Operator:    HH Holdings LLC / Bevans Real Estate                      ║
║   Location:    397 Highway 22, Clifton, TX 76634                         ║
║   Broker:      Biri Bevans, Designated Broker                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

Thank you for your interest in contributing to the BCMCE Platform! This document provides guidelines for contributing to the project.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Submitting Changes](#submitting-changes)

---

## 🤝 Code of Conduct

### Our Commitment

This project is dedicated to serving the public interest of rural Texas counties and their infrastructure needs. We are committed to providing a professional, respectful, and inclusive environment for all contributors.

### Expected Behavior

- Be professional and respectful in all interactions
- Focus on constructive feedback and collaborative problem-solving
- Respect the time and expertise of other contributors
- Maintain confidentiality of sensitive county information
- Follow all applicable laws and regulations

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

```
✓ Python 3.11 or higher
✓ Docker and Docker Compose
✓ Git
✓ A code editor (VS Code recommended)
✓ PostgreSQL knowledge (for database changes)
✓ FastAPI experience (for API changes)
```

### Areas for Contribution

We welcome contributions in these areas:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ FRONTEND                                                                 │
├──────────────────────────────────────────────────────────────────────────┤
│ • Bloomberg Terminal styling improvements                               │
│ • Mobile responsiveness                                                  │
│ • Accessibility enhancements                                             │
│ • Interactive data visualizations                                        │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ BACKEND                                                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ • API endpoint optimization                                              │
│ • Database query performance                                             │
│ • WebSocket enhancements                                                 │
│ • Authentication improvements                                            │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ AUTOMATION                                                               │
├──────────────────────────────────────────────────────────────────────────┤
│ • County scraper improvements                                            │
│ • Additional data sources                                                │
│ • Alert system enhancements                                              │
│ • Price prediction algorithms                                            │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ DOCUMENTATION                                                            │
├──────────────────────────────────────────────────────────────────────────┤
│ • User guides                                                            │
│ • API documentation                                                      │
│ • Deployment guides                                                      │
│ • Code comments and docstrings                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/BCMCE.git
cd BCMCE
```

### 2. Set Up Environment

```bash
# Run the setup script
./setup.sh

# Or manually:
cp .env.example .env
cd backend && pip install -r requirements.txt
```

### 3. Start Development Services

```bash
# Option 1: Using the dev script
./start-dev.sh

# Option 2: Using Make
make setup-dev
make docker-up

# Option 3: Manually
docker-compose up -d postgres redis
cd backend && python main.py
```

### 4. Verify Setup

```bash
# Check API is running
curl http://localhost:8000/health

# Run tests
make test
```

---

## 🔧 Making Changes

### Branch Naming Convention

Use descriptive branch names following this pattern:

```
feature/add-material-forecasting
bugfix/fix-option-pricing-calculation
docs/update-api-documentation
refactor/optimize-database-queries
```

### Development Workflow

```bash
# 1. Create a new branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# Edit files...

# 3. Test your changes
make test
make lint

# 4. Commit with descriptive message
git add .
git commit -m "Add detailed commit message"

# 5. Push to your fork
git push origin feature/your-feature-name

# 6. Create Pull Request on GitHub
```

---

## 📝 Coding Standards

### Python (Backend)

```python
# Use type hints
def calculate_option_premium(
    spot_price: float,
    duration_days: int,
    volatility: float
) -> float:
    """
    Calculate option premium based on market conditions.

    Args:
        spot_price: Current spot price of material
        duration_days: Option duration in days
        volatility: Market volatility factor

    Returns:
        Calculated premium amount
    """
    pass

# Follow PEP 8
# Use Black for formatting
# Use isort for import ordering
# Maximum line length: 88 characters
```

### JavaScript (Frontend)

```javascript
// Use ES6+ syntax
// Use descriptive variable names
// Add JSDoc comments for functions

/**
 * Fetch current pricing for all materials
 * @returns {Promise<Array>} Array of pricing objects
 */
async function fetchCurrentPricing() {
    // Implementation
}
```

### SQL (Database)

```sql
-- Use meaningful table and column names
-- Include comments for complex queries
-- Follow PostgreSQL naming conventions

-- Example:
CREATE TABLE option_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES materials(id),
    strike_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
cd backend
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Writing Tests

```python
# tests/test_pricing.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_current_pricing():
    """Test retrieving current pricing data"""
    response = client.get("/api/v1/pricing/current")
    assert response.status_code == 200
    assert "materials" in response.json()
```

### Test Coverage Requirements

- All new API endpoints must have tests
- Aim for 80%+ code coverage
- Include edge cases and error scenarios
- Test authentication and authorization

---

## 📚 Documentation

### Code Documentation

```python
# Use docstrings for all functions and classes
class OptionContract:
    """
    Represents a commodity option contract.

    Attributes:
        material_id: UUID of the underlying material
        strike_price: Locked-in price for the option
        duration_days: Option validity period
        premium: Cost of the option
    """
    pass
```

### API Documentation

- Update `docs/API.md` for endpoint changes
- Use FastAPI's built-in OpenAPI documentation
- Include request/response examples
- Document error codes and responses

### User Documentation

- Update `docs/GETTING_STARTED.md` for user-facing changes
- Include screenshots where helpful
- Write clear, step-by-step instructions
- Consider the audience (counties vs. suppliers)

---

## 📤 Submitting Changes

### Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Update CHANGELOG.md with your changes
   - Update API.md for endpoint changes

2. **Ensure Tests Pass**
   ```bash
   make test
   make lint
   ```

3. **Write a Clear PR Description**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   Describe tests performed

   ## Screenshots (if applicable)
   Add screenshots for UI changes
   ```

4. **Reference Issues**
   - Link to related issues
   - Use "Fixes #123" to auto-close issues

### Review Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Submit PR                                                            │
│ 2. Automated checks run (tests, linting)                               │
│ 3. Code review by maintainers                                          │
│ 4. Address feedback and make changes                                   │
│ 5. Approval and merge                                                  │
│ 6. Changes deployed                                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Guidelines

### Backend Structure

```
backend/
├── api/           # API route handlers
├── models/        # Pydantic schemas
├── database.py    # Database models and connections
├── auth.py        # Authentication logic
├── config.py      # Configuration management
└── main.py        # Application entry point
```

### Database Changes

- Create migration scripts in `data/migrations/`
- Test migrations on sample data
- Document schema changes
- Ensure backward compatibility when possible

### API Design

- Follow RESTful principles
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return appropriate status codes
- Include pagination for list endpoints
- Validate all inputs with Pydantic

---

## 🔒 Security Guidelines

### Sensitive Data

- Never commit credentials or API keys
- Use environment variables for secrets
- Sanitize all user inputs
- Follow OWASP security best practices

### Code Review Checklist

```
[ ] No hardcoded credentials
[ ] Input validation present
[ ] SQL injection prevention
[ ] XSS prevention
[ ] CSRF protection
[ ] Proper authentication/authorization
[ ] Secure password handling
```

---

## 🆘 Getting Help

### Resources

- **Documentation**: `/docs` directory
- **API Reference**: http://localhost:8000/api/docs
- **Issue Tracker**: GitHub Issues

### Questions?

For questions about:
- **Technical issues**: Open a GitHub issue
- **Business requirements**: Contact HH Holdings
- **Security concerns**: Email security@hhholdings.com (if available)

---

## 📜 License

By contributing to BCMCE, you agree that your contributions will be licensed under the project's proprietary license owned by HH Holdings LLC.

---

```
════════════════════════════════════════════════════════════════════════════════
              Thank you for contributing to BCMCE Platform!
                Building transparent infrastructure markets
                        for rural Texas counties
════════════════════════════════════════════════════════════════════════════════
                   © 2026 HH Holdings LLC / Bevans Real Estate
════════════════════════════════════════════════════════════════════════════════
```
