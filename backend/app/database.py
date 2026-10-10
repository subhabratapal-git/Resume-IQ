import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


# ResumeIQ project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Existing root database folder
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# SQLite fallback database file
DATABASE_PATH = DATABASE_DIR / "resumeiq.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

raw_db_url = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

# SQLAlchemy 1.4+ requires postgresql:// instead of postgres://
if raw_db_url.startswith("postgres://"):
    DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = raw_db_url

# Database engine configuration
is_sqlite = DATABASE_URL.startswith("sqlite")
engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs
)

# Safe column migration for existing SQLite databases
def _migrate_columns():
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_changed_at DATETIME"))
            conn.commit()
    except Exception:
        pass
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 1"))
            conn.commit()
    except Exception:
        pass

_migrate_columns()


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