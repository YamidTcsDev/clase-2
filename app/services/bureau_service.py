from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.cliente import Cliente

class BureauService:
    # Límite: 1 consulta por cliente cada 24h
    LIMITE_CONSULTAS_24H = 1
    
    def consultar_score(self, db: Session, cliente_id: int):
        """
        Test Cases implementados:
        1. Path feliz: Cliente con score 750 → OK
        2. Sin historial: Cliente nuevo → score=0, mensaje="Sin historial"
        3. Límite consultas: >1 en 24h → Error
        4. Cliente bloqueado: estado=BLOQUEADO → Error
        """
        
        # Validar cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Test Case: Cliente bloqueado
        if cliente.estado.value == "bloqueado":
            raise ValueError("Cliente en lista de riesgo. Consulta bloqueada.")
        
        # Test Case: Límite de consultas (simular con cache/DB)
        ultima_consulta = self._obtener_ultima_consulta(db, cliente_id)
        if ultima_consulta and (datetime.utcnow() - ultima_consulta) < timedelta(hours=24):
            raise ValueError("Límite de consultas: solo 1 permitida cada 24 horas")
        
        # Test Case: Sin historial crediticio
        if cliente.score_cifin is None:
            return {
                "cliente_id": cliente.id,
                "score": 0,
                "deudas_activas": 0,
                "monto_deudas": 0.0,
                "puntualidad": "Sin información",
                "tiene_historial": False,
                "fecha_consulta": datetime.utcnow().isoformat(),
                "mensaje": "Cliente sin historial crediticio registrado"
            }
        
        # Test Case: Path feliz
        puntualidad = self._calcular_puntualidad(cliente.score_cifin)
        return {
            "cliente_id": cliente.id,
            "score": cliente.score_cifin,
            "deudas_activas": 2,  # Mock
            "monto_deudas": 5000000.0,
            "puntualidad": puntualidad,
            "tiene_historial": True,
            "fecha_consulta": datetime.utcnow().isoformat(),
            "mensaje": f"Score {cliente.score_cifin}. Cliente {'apto' if cliente.score_cifin > 650 else 'no apto'} para crédito."
        }
    
    def _calcular_puntualidad(self, score: int) -> str:
        if score >= 800: return "Excelente"
        if score >= 700: return "Buena"
        if score >= 600: return "Regular"
        return "Mala"
    
    def _obtener_ultima_consulta(self, db: Session, cliente_id: int):
        """
        Mock: En memoria no persiste entre requests.
        En producción: guardar timestamp en tabla 'consultas_bureau'
        """
        # Para demo: siempre retorna None (primera consulta)
        return None
