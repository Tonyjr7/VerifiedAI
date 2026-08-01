from sqlalchemy import Column, Integer, String, JSON
from config.base import Base

import uuid

class Library(Base):
    __tablename__ = 'library'

    id = Column(Integer, primary_key=True)
    claim_id = Column(String, default=uuid.uuid4)
    username = Column(String)

    # Standard agnostic JSON field
    debunked = Column(JSON, default=dict)
