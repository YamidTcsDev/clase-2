from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.bureau import BureauRequest, BureauResponse
from app.services.bureau_service import BureauService
from app.database import get_db

router = APIRouter(prefix="/api/bureau", tags=["Bureau de Crédito"])

@router.post("/consultar", response_model=BureauResponse)
def consultar_bureau(request: BureauRequest, db: Session = Depends(get_db)):
    """
    Consulta el score y historial crediticio de un cliente.
    
    **Test Cases cubiertos:**
    - ✅ Path feliz: Cliente con historial → Score + detalles
    - ⚠️ Sin historial: Cliente nuevo → score=0
    - ❌ Cliente bloqueado → Error 403
    - ⚠️ Límite consultas: >1 en 24h → Error 429
    """
    try:
        service = BureauService()
        resultado = service.consultar_score(db, request.cliente_id)
        return resultado
    except ValueError as e:
        if "bloqueado" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        if "límite" in str(e).lower():
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{cliente_id}", response_model=BureauResponse)
def obtener_ultima_consulta(cliente_id: int, db: Session = Depends(get_db)):
    """Obtiene la última consulta guardada (mock para demo)"""
    service = BureauService()
    try:
        resultado = service.consultar_score(db, cliente_id)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
