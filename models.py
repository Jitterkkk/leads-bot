from sqlalchemy import Column, Integer, String
from database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telefone = Column(String)
    nome = Column(String)
    interesse = Column(String)

class Etapa(Base):
    __tablename__ = "etapas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telefone = Column(String, unique=True)
    etapa = Column(String) 