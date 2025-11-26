from pydantic import BaseModel, Field
from typing import Optional

class BureauRequest(BaseModel):
    cliente_id: int = Field(..., description="ID del cliente")
    
class BureauResponse(BaseModel):
    cliente_id: int
    score: int = Field(..., ge=0, le=900, description="Score crediticio")
    deudas_activas: int
    monto_deudas: float
    puntualidad: str  # "Excelente", "Buena", "Regular", "Mala"
    tiene_historial: bool
    fecha_consulta: str
    mensaje: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "cliente_id": 123,
                "score": 750,
                "deudas_activas": 2,
                "monto_deudas": 5000000.0,
                "puntualidad": "Excelente",
                "tiene_historial": True,
                "fecha_consulta": "2025-11-25T10:30:00",
                "mensaje": "Cliente apto para crédito"
            }
        }
