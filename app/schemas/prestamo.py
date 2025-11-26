from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PrestamoRequest(BaseModel):
    cliente_id: int = Field(..., description="ID del cliente")
    monto_solicitado: float = Field(..., gt=0, le=50_000_000)
    plazo_meses: int = Field(..., ge=12, le=60)

class PrestamoResponse(BaseModel):
    id: int
    cliente_id: int
    monto_solicitado: float
    plazo_meses: int
    cuota_mensual: Optional[float] = None
    estado: str
    motivo_rechazo: Optional[str] = None
    fecha_solicitud: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "cliente_id": 1,
                "monto_solicitado": 10000000.0,
                "plazo_meses": 24,
                "cuota_mensual": 483871.0,
                "estado": "aprobado",
                "motivo_rechazo": None,
                "fecha_solicitud": "2025-11-26T10:30:00"
            }
        }
