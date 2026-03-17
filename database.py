from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# cria o banco SQlite (arquivo leads.db) e a sessão para interagir com ele
engine = create_engine("sqlite:///leads.db")
SessionLocal = sessionmaker(bind=engine)
# base para a criação das tabelas (ORM)
Base = declarative_base()