"""SQLAlchemy database models for TruthGuard."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


# ── Base ──

class Base(DeclarativeBase):
    pass


# ── Helper ──

def generate_id() -> str:
    return str(uuid.uuid4())[:12]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Models ──

class User(Base):
    __tablename__ = "users"

    id = Column(String(12), primary_key=True, default=generate_id)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    analyses = relationship("Analysis", back_populates="user")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(12), primary_key=True, default=generate_id)
    user_id = Column(String(12), ForeignKey("users.id"), nullable=True)
    input_type = Column(String(20), nullable=False)  # text, url, image, video
    input_content = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    verdict = Column(String(20), nullable=True)  # LIKELY_TRUE, LIKELY_FALSE, UNVERIFIED, SUSPICIOUS
    confidence = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    evidence_coverage = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    user = relationship("User", back_populates="analyses")
    claims = relationship("Claim", back_populates="analysis", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="analysis", cascade="all, delete-orphan")
    result = relationship("Result", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(12), ForeignKey("analyses.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(String(50), nullable=True)
    verdict = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)

    # Relationships
    analysis = relationship("Analysis", back_populates="claims")
    evidence = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(12), ForeignKey("analyses.id"), nullable=False)
    url = Column(Text, nullable=True)
    title = Column(String(500), nullable=True)
    publisher = Column(String(200), nullable=True)
    source_type = Column(String(50), nullable=True)  # official, news, fact-checker, etc.
    reliability_score = Column(Float, nullable=True)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    analysis = relationship("Analysis", back_populates="sources")
    evidence = relationship("Evidence", back_populates="source", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    evidence_text = Column(Text, nullable=False)
    evidence_type = Column(String(50), nullable=True)  # support, contradiction, warning
    support_score = Column(Float, nullable=True)  # -1.0 (contradicts) to 1.0 (supports)

    # Relationships
    claim = relationship("Claim", back_populates="evidence")
    source = relationship("Source", back_populates="evidence")


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(12), ForeignKey("analyses.id"), nullable=False, unique=True)
    verdict = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    explanation = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)

    # Relationships
    analysis = relationship("Analysis", back_populates="result")


# ── Database Setup ──

_engine = None
_session_factory = None


def get_engine(database_url: str):
    global _engine
    if _engine is None:
        connect_args = {}
        if "sqlite" in database_url:
            connect_args = {"check_same_thread": False}
        _engine = create_async_engine(database_url, echo=False, connect_args=connect_args)
    return _engine


def get_session_factory(database_url: str):
    global _session_factory
    if _session_factory is None:
        engine = get_engine(database_url)
        _session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return _session_factory


async def init_db(database_url: str):
    """Create all tables."""
    engine = get_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db(database_url: str):
    """Dependency that yields a database session."""
    factory = get_session_factory(database_url)
    async with factory() as session:
        yield session
