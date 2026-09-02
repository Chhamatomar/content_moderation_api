from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load variables from .env into the environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine manages the actual connection pool to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory for creating new DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class our SQLAlchemy models will inherit from
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI routes.
    Opens a session, hands it to the route, then closes it afterward
    even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()