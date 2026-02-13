"""Run ALTER TABLE directly using asyncpg to avoid importing app modules."""
import asyncio
import os
import asyncpg


def get_db_url():
    env = {}
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    db = env.get("DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not db:
        raise SystemExit("DATABASE_URL not found in .env or environment")
    # remove +asyncpg if present
    return db.replace("+asyncpg", "")


async def main():
    db_url = get_db_url()
    conn = await asyncpg.connect(dsn=db_url)
    try:
        await conn.execute("ALTER TABLE news ADD COLUMN IF NOT EXISTS confidence_score FLOAT")
        print("✓ confidence_score column added")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
