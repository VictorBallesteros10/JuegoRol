import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    clave = Column(String, nullable=False)
    partidas = relationship("Partida", back_populates="usuario")

class Partida(Base):
    __tablename__ = 'partidas'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    nombre_personaje = Column(String, nullable=False)
    datos_personaje  = Column(Text, nullable=False)
    fecha_guardado      = Column(DateTime, default=datetime.datetime.utcnow)
    usuario          = relationship("Usuario", back_populates="partidas")
    historia = Column(Text, nullable=True)


# Motor y sesión global
engine = create_engine('sqlite:///app/data/juegorol.db', echo=False, future=True)
Session = sessionmaker(bind=engine, future=True)

# Crea las tablas si no existen
Base.metadata.create_all(engine)
