from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.prestamo import PrestamoRequest, PrestamoResponse
from app.services.prestamo_service import PrestamoService
from app.database import get_db

router = APIRouter(prefix="/api/prestamos", tags=["Préstamos"])

@router.post("/solicitar", response_model=PrestamoResponse)
def solicitar_prestamo(request: PrestamoRequest, db: Session = Depends(get_db)):
    """
    Crea solicitud de préstamo con aprobación automática/manual/rechazo.
    
    **Test Cases cubiertos:**
    - ✅ Aprobación automática: score>700, ingresos 4x cuota
    - ⚠️ Análisis manual: score 600-700, ingresos 3x cuota
    - ❌ Rechazo: score<500 o ingresos insuficientes
    - ❌ Límite monto: >$50M → Error validación
    """
    try:
        service = PrestamoService()
        prestamo = service.solicitar_prestamo(
            db, 
            request.cliente_id, 
            request.monto_solicitado, 
            request.plazo_meses
        )
        return prestamo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{prestamo_id}/estado", response_model=PrestamoResponse)
def obtener_estado_prestamo(prestamo_id: int, db: Session = Depends(get_db)):
    """Consulta estado actual de un préstamo"""
    try:
        service = PrestamoService()
        prestamo = service.obtener_estado_prestamo(db, prestamo_id)
        return prestamo
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
