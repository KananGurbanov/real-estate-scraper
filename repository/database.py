from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from repository.models import Base
import logging

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/real_estate_db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    try:
        Base.metadata.create_all(engine)
        logging.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logging.error(f"Error initializing the database: {e}")
        raise
