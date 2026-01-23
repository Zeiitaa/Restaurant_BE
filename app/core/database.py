# berisikan koneksi ke database dan pembuatan engine dan session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Buat SQLAlchemy engine
engine =create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal untuk dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class untuk model ORM

Base = declarative_base()