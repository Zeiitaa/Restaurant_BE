from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv


# Link DataBase
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# membuat engine dengan link database
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ngebuat session
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

base = declarative_base()

# fungsi getDB
def getDB():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()