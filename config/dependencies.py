from typing import Generator
from config.base import SessionLocal

def get_db() -> Generator:
    """ Opens a database session per request and closes it after. """
    db = SessionLocal()
    try:
        yield db  # Hands the session over to the endpoint
    finally:
        db.close() # Guarantees the session closes, even if errors occur
