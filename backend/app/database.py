from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ResumeIQ project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Existing root database folder
DATABASE_DIR = PROJECT_ROOT / "database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# SQLite database file
DATABASE_PATH = DATABASE_DIR / "resumeiq.db"

DATABASE_URL = (
    f"sqlite:///{DATABASE_PATH.as_posix()}"
)


# Database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models
Base = declarative_base()


# Database dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
        
        
        