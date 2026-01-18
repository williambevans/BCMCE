# BCMCE Platform - Deployment Checklist

**Status:** 🔴 NOT READY | **Target:** ✅ PRODUCTION READY

---

## Phase 1: Critical Fixes (MUST DO)

### Configuration Issues
- [ ] **Fix Pydantic v2 import** `config.py:8`
  - Change: `from pydantic import BaseSettings`
  - To: `from pydantic_settings import BaseSettings`
  - Add: `pydantic-settings` to requirements.txt
  - **Time: 5 min** | **Priority: IMMEDIATE**

- [ ] **Fix health check settings import** `main.py:104`
  - Change: `from config import settings`
  - To: `from config import get_settings` + call function
  - **Time: 5 min** | **Priority: IMMEDIATE**

- [ ] **Add os import to auth.py**
  - Move `import os` from line 465 to top of file
  - **Time: 1 min** | **Priority: IMMEDIATE**

### Database Issues
- [ ] **Resolve UUID vs Integer schema mismatch**
  - Decision: [ ] Keep UUID [ ] Switch to Integer
  - If UUID: Update all models in `database.py`
  - If Integer: Update `001_create_tables.sql`
  - Test all relationships
  - **Time: 2-4 hours** | **Priority: BLOCKER**

### API Endpoints
- [ ] **Create auth API router**
  - Create: `/home/user/BCMCE/backend/api/auth.py`
  - Implement: POST /api/v1/auth/login
  - Implement: POST /api/v1/auth/register
  - Implement: POST /api/v1/auth/refresh
  - Implement: GET /api/v1/auth/me
  - Register router in `main.py`
  - **Time: 1-2 hours** | **Priority: BLOCKER**

- [ ] **Wire WebSocket endpoint**
  - Add WebSocket route to `main.py`
  - Import from `websocket.py`
  - Test connection
  - **Time: 15 min** | **Priority: HIGH**

### Environment & Configuration
- [ ] **Create production .env file**
  - Copy .env.example to .env
  - Generate: `API_SECRET_KEY` (run: `openssl rand -hex 32`)
  - Generate: `JWT_SECRET_KEY` (run: `openssl rand -hex 32`)
  - Set: `POSTGRES_PASSWORD` (strong password)
  - Configure: SMTP_* variables (if email needed)
  - **Time: 15 min** | **Priority: BLOCKER**

- [ ] **Complete docker-compose.yml env mapping**
  - Add JWT_SECRET_KEY mapping
  - Add API_SECRET_KEY mapping
  - Add all SMTP_* mappings
  - Add CORS_ORIGINS mapping
  - Add LOG_LEVEL mapping
  - **Time: 30 min** | **Priority: HIGH**

### Data Loading
- [ ] **Create seed data loading scripts**
  - Create: `backend/seed_data.py`
  - Implement: `load_materials()` from materials.json
  - Implement: `load_suppliers()` from suppliers.json
  - Implement: `create_admin_user()`
  - Test loading process
  - **Time: 1-2 hours** | **Priority: BLOCKER**

---

## Phase 2: High Priority (SHOULD DO)

### Database Management
- [ ] **Initialize Alembic**
  - Run: `alembic init alembic`
  - Configure: `alembic.ini`
  - Create: Initial migration
  - Test: Migration up/down
  - **Time: 2-3 hours**

### API Completion
- [ ] **Complete pricing update authentication**
  - Implement supplier auth in `api/pricing.py:194-195`
  - Add authentication decorator
  - Test price update workflow
  - **Time: 2-3 hours**

### Background Tasks
- [ ] **Set up Celery tasks**
  - Create: `backend/tasks.py`
  - Define: Price monitoring task
  - Define: Option expiry alert task
  - Uncomment Celery services in docker-compose.yml
  - Test background execution
  - **Time: 3-4 hours**

### Production Config
- [ ] **Create docker-compose.prod.yml**
  - Remove debug volumes
  - Add restart policies
  - Add health checks
  - Add resource limits
  - Configure for production
  - **Time: 1 hour**

### Code Quality
- [ ] **Fix import path issues**
  - Test all imports in Docker context
  - Configure PYTHONPATH if needed
  - Update import statements
  - **Time: 1-2 hours**

- [ ] **Add comprehensive error handling**
  - Add try/catch to all API endpoints
  - Handle database connection failures
  - Handle Redis connection failures
  - Handle email sending failures
  - Add proper error responses
  - **Time: 4-6 hours**

---

## Phase 3: Production Polish (NICE TO HAVE)

### Testing
- [ ] **Add integration tests**
  - Test authentication flow
  - Test option contract lifecycle
  - Test bid submission workflow
  - Test WebSocket connections
  - Test email notifications
  - **Time: 8-12 hours**

### Observability
- [ ] **Set up proper logging**
  - Call `configure_logging()` in main.py
  - Add structured logging
  - Configure log levels
  - Add request logging
  - **Time: 2 hours**

- [ ] **Add monitoring endpoints**
  - Add /metrics endpoint
  - Add performance tracking
  - Configure Sentry (if using)
  - **Time: 2-3 hours**

### Security
- [ ] **Implement rate limiting**
  - Add rate limiting middleware
  - Configure limits per endpoint
  - Add rate limit headers
  - **Time: 2-3 hours**

### External Integrations
- [ ] **Complete TxDOT scraper**
  - Implement actual API calls
  - Add error handling
  - Add retry logic
  - Test data parsing
  - **Time: 4-6 hours**

### Reliability
- [ ] **Add database retry logic**
  - Implement connection retry
  - Add exponential backoff
  - Handle transient failures
  - **Time: 2 hours**

### Documentation
- [ ] **Update documentation**
  - Document auth flow
  - Update API examples
  - Add deployment guide updates
  - Create runbook
  - **Time: 2 hours**

### Utilities
- [ ] **Create admin setup script**
  - Script to create admin user
  - Script to configure initial settings
  - Add to startup documentation
  - **Time: 1 hour**

- [ ] **Add backup automation**
  - Create database backup script
  - Schedule automated backups
  - Test restore process
  - **Time: 2-3 hours**

---

## Deployment Verification

### Pre-Deployment Checks
```bash
# 1. Verify all critical fixes completed
grep -n "from pydantic import BaseSettings" backend/config.py
# Should return nothing (fixed)

# 2. Check .env exists
ls -la .env
# Should show .env file

# 3. Verify secrets are not defaults
grep "change-this-secret-key" .env
# Should return nothing

# 4. Check import errors
cd backend && python -c "import config; import main; import auth"
# Should have no errors

# 5. Verify database schema
psql -U bcmce -d bcmce_db -c "\d suppliers"
# Should show correct primary key type
```

### Deployment Test
```bash
# 1. Start services
./start-dev.sh

# 2. Check health
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# 3. Check API docs
curl http://localhost:8000/api/docs
# Should return HTML

# 4. Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
# Should return token or proper error

# 5. Test WebSocket
wscat -c ws://localhost:8000/ws/pricing
# Should connect successfully

# 6. Check database
docker-compose exec postgres psql -U bcmce -d bcmce_db -c "SELECT COUNT(*) FROM materials;"
# Should return material count

# 7. Check logs for errors
docker-compose logs backend | grep -i error
# Should have no critical errors
```

---

## Progress Tracking

**Phase 1 Progress:** 0/8 tasks complete (0%)
**Phase 2 Progress:** 0/6 tasks complete (0%)
**Phase 3 Progress:** 0/9 tasks complete (0%)

**Overall Progress:** 0/23 tasks complete (0%)

---

## Time Tracking

| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| Phase 1 (Critical) | 8-12 hours | - | ⏳ Not Started |
| Phase 2 (High Priority) | 15-20 hours | - | ⏳ Not Started |
| Phase 3 (Production) | 25-35 hours | - | ⏳ Not Started |
| **TOTAL** | **48-67 hours** | **-** | ⏳ **Not Started** |

---

## Quick Reference

### Critical Path (Must Do First)
1. Pydantic import (5 min)
2. Health check import (5 min)
3. Create .env (15 min)
4. Database schema decision (2-4 hours)
5. Auth router (1-2 hours)
6. Data loading scripts (1-2 hours)

### Deployment Command
```bash
# After Phase 1 complete:
./start-dev.sh

# For production:
./start-production.sh
```

### Rollback Plan
```bash
# If deployment fails:
docker-compose down
git checkout main
git pull
# Review logs and fix issues
```

---

**Last Updated:** 2026-01-18
**Status:** Ready for Phase 1 execution

© 2026 HH Holdings LLC / Bevans Real Estate
