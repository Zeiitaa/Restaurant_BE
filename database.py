from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Link DataBase
DATABASE_URL = "postgresql://postgres.emgnclsjjykzgnhtccvs:hjfyfqmovF3NcCeb@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

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