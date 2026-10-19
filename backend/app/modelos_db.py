import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text, create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

URL = os.getenv("DATABASE_URL", "sqlite:///./novatech.db")
if URL.startswith("postgres://"):
    URL = URL.replace("postgres://", "postgresql://", 1)
if URL.startswith("postgresql://"):
    URL = URL.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {"check_same_thread": False} if URL.startswith("sqlite") else {}
engine = create_engine(URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def ahora():
    return datetime.utcnow()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    # Los atributos se llaman email / password_hash en Python,
    # pero apuntan a las columnas reales de la tabla: correo / password.
    email = Column("correo", String(120), unique=True, nullable=False, index=True)
    password_hash = Column("password", String(255), nullable=False)
    rol = Column(String(20), default="operario")
    activo = Column(Boolean, default=True)


class Lote(Base):
    __tablename__ = "lotes"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(40), unique=True, nullable=False, index=True)
    producto = Column(String(160), nullable=False)
    cantidad = Column(Float, default=0)
    unidad = Column(String(30), default="unidades")
    responsable = Column(String(120), default="")
    creado_en = Column(DateTime, default=ahora)
    etapas = relationship("EtapaLote", back_populates="lote",
                          cascade="all, delete-orphan", order_by="EtapaLote.orden")


class EtapaLote(Base):
    __tablename__ = "etapas_lote"
    id = Column(Integer, primary_key=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    orden = Column(Integer, default=0)
    nombre = Column(String(80), nullable=False)
    responsable = Column(String(120), default="")
    control_calidad = Column(Boolean, default=False)
    observaciones = Column(Text, default="")
    completada = Column(Boolean, default=False)
    fecha_limite = Column(DateTime)
    fecha_real = Column(DateTime)
    lote = relationship("Lote", back_populates="etapas")


class Transportista(Base):
    __tablename__ = "transportistas"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    telefono = Column(String(40), default="")
    valoracion = Column(Float, default=4.0)
    costo_km = Column(Float, default=0)
    disponible = Column(Boolean, default=True)
    vehiculos = relationship("Vehiculo", back_populates="transportista")


class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id = Column(Integer, primary_key=True)
    transportista_id = Column(Integer, ForeignKey("transportistas.id"), nullable=False)
    placa = Column(String(20), unique=True, nullable=False)
    tipo = Column(String(60), default="Camión")
    modelo = Column(String(60), default="")
    capacidad_kg = Column(Float, default=0)
    disponible = Column(Boolean, default=True)
    transportista = relationship("Transportista", back_populates="vehiculos")


class Pedido(Base):
    # La base ya tiene una tabla "pedidos" de la versión anterior (con usuario_id, numero, total...).
    # Se usa otro nombre para no chocar con ella ni tocar sus datos.
    __tablename__ = "pedidos_logistica"
    id = Column(Integer, primary_key=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"))
    cliente = Column(String(160), nullable=False)
    origen = Column(String(80), nullable=False)
    destino = Column(String(80), nullable=False)
    peso_kg = Column(Float, default=0)
    distancia_km = Column(Float, default=0)
    transportista_id = Column(Integer, ForeignKey("transportistas.id"))
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"))
    estado = Column(String(30), default="Pendiente")
    tarifa = Column(Float, default=0)
    comision = Column(Float, default=0)
    creado_en = Column(DateTime, default=ahora)
    entregado_en = Column(DateTime)
    lote = relationship("Lote")
    transportista = relationship("Transportista")
    vehiculo = relationship("Vehiculo")


class ConsumoEnergia(Base):
    __tablename__ = "consumos_energia"
    id = Column(Integer, primary_key=True)
    maquina = Column(String(120), nullable=False)
    proceso = Column(String(120), nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"))
    kwh = Column(Float, nullable=False)
    tarifa_kwh = Column(Float, nullable=False)
    fecha = Column(DateTime, default=ahora)
    lote = relationship("Lote")


class TarifaElectrica(Base):
    __tablename__ = "tarifas_electricas"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    hora_inicio = Column(Integer, nullable=False)
    hora_fin = Column(Integer, nullable=False)
    valor_kwh = Column(Float, nullable=False)
