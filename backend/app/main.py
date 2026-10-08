import logging
import os

from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env file FIRST — before any service module reads os.getenv().
# This ensures JWT_SECRET_KEY, GEMINI_API_KEY, etc. are set at import time.
load_dotenv()

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models.analysis import ResumeAnalysis
from app.models.user import User
from app.routes import auth, resume, pro


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("ResumeIQ API started — database tables ready.")
    yield


# Disable interactive docs in production.
# Set ENABLE_DOCS=true in .env for local development.
_docs_url = "/docs" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None
_redoc_url = "/redoc" if os.getenv("ENABLE_DOCS", "false").lower() == "true" else None

app = FastAPI(
    title="ResumeIQ API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth.router,
    prefix="/auth",
)

app.include_router(
    resume.router,
    prefix="/resume",
)

app.include_router(
    pro.router,
    prefix="/api/pro",
)


@app.get("/")
def home():
    return {
        "message": "ResumeIQ API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ResumeIQ API"
    }


@app.get("/stats/analyses")
def analysis_total(db: Session = Depends(get_db)):
    # Public aggregate only; no account or report details are exposed.
    return {"total_analyses": db.query(func.count(ResumeAnalysis.id)).scalar()}
