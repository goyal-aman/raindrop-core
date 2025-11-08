from sqlalchemy import create_engine, Column, String, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path
import os

# default DB at repo root (same as previous db.sqlite)
DB_PATH = Path(__file__).resolve().parent.parent / "db.sqlite"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# for sqlite we need to disable same-thread check for multi-threaded access
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


class Ingest(Base):
    __tablename__ = "ingests"
    url = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(Float)
    updated_at = Column(Float)


def init_db():
    Base.metadata.create_all(bind=engine)
