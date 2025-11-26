from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from datetime import datetime
import enum
from app.database import Base

class EstadoPrestamo(str, enum.Enum):
    SOLICITADO = "solicitado"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    DESEMBOLSADO = "desembolsado"

class Prestamo(Base):
    __tablename__ = "prestamos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    monto_solicitado = Column(Float, nullable=False)
    plazo_meses = Column(Integer, nullable=False)  # 12, 24, 36, 48, 60
    tasa_interes = Column(Float)  # %
    cuota_mensual = Column(Float)
    estado = Column(Enum(EstadoPrestamo), default=EstadoPrestamo.SOLICITADO)
    motivo_rechazo = Column(String, nullable=True)
    fecha_solicitud = Column(DateTime, default=datetime.utcnow)
    fecha_decision = Column(DateTime, nullable=True)
