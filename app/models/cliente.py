from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
import enum
from app.database import Base

class EstadoCliente(str, enum.Enum):
    ACTIVO = "activo"
    BLOQUEADO = "bloqueado"
    INACTIVO = "inactivo"

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    identificacion = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    score_cifin = Column(Integer)  # 300-900
    ingresos_mensuales = Column(Float)
    estado = Column(Enum(EstadoCliente), default=EstadoCliente.ACTIVO)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
