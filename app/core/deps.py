# berisikan fungsi untuk mengambil sesi database
from database import sessionLocal

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()