# Описание подключения к БД

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#DB_URL = "postgresql://postgres:1@localhost/sea_battle"
DB_URL = "postgresql://postgres:1@db:5432/sea_battle"
engine = create_engine(DB_URL)

session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()