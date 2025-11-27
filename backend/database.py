from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. PASTE YOUR NEW "POOLER" STRING HERE
# It should look like: postgresql://postgres.nmkns...:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
DATABASE_URL = "postgresql://postgres.nmknsbsdzbofxkahhtcx:KairosProject2025@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

# 2. MANUALLY FIX THE PASSWORD
# Replace [YOUR-PASSWORD] with: KairosProject2025
# (Make sure to remove the brackets []!)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()