from sqlalchemy import create_engine, inspect
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'))
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)

if 'transactions' in tables:
    print('\nTransactions columns:')
    for col in inspector.get_columns('transactions'):
        print(f'  {col["name"]}: {col["type"]}')
else:
    print('\nNo transactions table found!')
