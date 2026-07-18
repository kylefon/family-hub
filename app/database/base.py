import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

load_dotenv()

USERNAME = os.getenv("DB_USER")
NAME = os.getenv("DB_NAME")
PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(f'postgresql+psycopg://{USERNAME}:{PASSWORD}@postgres:5432/{NAME}'.format('postgres', '5432', 'db'))
Session = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


