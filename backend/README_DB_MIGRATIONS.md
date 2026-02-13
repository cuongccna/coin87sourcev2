# Alembic Database Migration Guide

## Setup (Already Done)
```bash
cd backend
alembic init alembic
```

## Configuration
- **alembic.ini**: Points to app database URL (reads from .env)
- **alembic/env.py**: Imports all models for autogenerate

## Workflow

### 1. Create Migration (Auto-detect changes)
```bash
cd backend
alembic revision --autogenerate -m "Add new column xyz"
```

### 2. Review Migration
Check `alembic/versions/xxxxx_add_new_column_xyz.py`

### 3. Apply Migration
```bash
alembic upgrade head
```

### 4. Rollback (if needed)
```bash
alembic downgrade -1    # Rollback 1 version
alembic downgrade base  # Rollback all
```

## Common Commands

```bash
# Check current version
alembic current

# Show migration history
alembic history

# Show SQL without executing
alembic upgrade head --sql

# Create empty migration (manual)
alembic revision -m "custom migration"
```

## Important Notes

1. **Always review** auto-generated migrations before applying
2. **Test migrations** on dev database first
3. **Backup database** before running migrations in production
4. **Add new models** to `alembic/env.py` imports for autogenerate

## Example: Adding a New Column

1. Edit model:
```python
# app/models/user.py
class User(Base):
    ...
    new_field = Column(String, nullable=True)
```

2. Generate migration:
```bash
alembic revision --autogenerate -m "Add new_field to users"
```

3. Apply:
```bash
alembic upgrade head
```

## Deployment

On VPS, add to deploy script:
```bash
source venv/bin/activate
alembic upgrade head
```

This ensures database schema is always up-to-date after code deployment.
