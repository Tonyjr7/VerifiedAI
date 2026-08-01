import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import Settings

# 1. Define the Database URL (usually from environment variables)
DATABASE_URL = Settings().database_url

# 2. Create the Engine (manages database connections)
engine = create_engine(DATABASE_URL, echo=False) # Set echo=False in production

# 3. Configure the Session Factory (used to create database transactions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Declarative Base (the parent class your models inherit from)
Base = declarative_base()
