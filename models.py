from sqlalchemy import Column, Integer, String
from database import Base

# tabela de leads (clientes)
class Lead(Base):
    __tablename__ = "leads" # nome da tabela no banco de dados

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telefone = Column(String)
    nome = Column(String)
    interesse = Column(String)

# tabela para controlar a etapa do fluxo de cada usuário
class Etapa(Base):
    __tablename__ = "etapas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telefone = Column(String, unique=True) # cada telefone só pode ter uma etapa associada
    etapa = Column(String) 