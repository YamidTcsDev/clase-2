from datetime import datetime
from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.models.prestamo import Prestamo, EstadoPrestamo

class PrestamoService:
    # Constantes de negocio (de test cases Clase 2)
    LIMITE_MONTO = 50_000_000
    PLAZO_MAXIMO_MESES = 60
    SCORE_APROBACION_AUTOMATICA = 700
    SCORE_RECHAZO_AUTOMATICO = 500
    RATIO_INGRESOS_MINIMO = 3  # Ingresos deben ser 3x cuota
    
    def solicitar_prestamo(self, db: Session, cliente_id: int, monto: float, plazo_meses: int):
        """
        Test Cases implementados:
        1. Aprobación automática: score>700, ingresos 4x cuota → APROBADO
        2. Análisis manual: score 600-700, ingresos 3x cuota → EN_REVISION
        3. Rechazo automático: score<500 → RECHAZADO
        4. Límite monto: monto>50M → Error validación
        """
        
        # Test Case: Validar límite de monto
        if monto > self.LIMITE_MONTO:
            raise ValueError(f"Monto solicitado excede límite de ${self.LIMITE_MONTO:,.0f}")
        
        if plazo_meses > self.PLAZO_MAXIMO_MESES:
            raise ValueError(f"Plazo máximo permitido: {self.PLAZO_MAXIMO_MESES} meses")
        
        # Obtener cliente
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Calcular cuota mensual (simplificado: monto/plazo, sin interés)
        tasa_anual = 0.15  # 15% anual
        cuota_mensual = self._calcular_cuota(monto, plazo_meses, tasa_anual)
        
        # Validar que el cliente tenga score
        if cliente.score_cifin is None:
            return self._crear_prestamo_rechazado(
                db, cliente_id, monto, plazo_meses,
                motivo="Cliente sin historial crediticio"
            )
        
        # Test Case: Rechazo automático (score < 500)
        if cliente.score_cifin < self.SCORE_RECHAZO_AUTOMATICO:
            return self._crear_prestamo_rechazado(
                db, cliente_id, monto, plazo_meses,
                motivo="Score crediticio insuficiente (< 500)"
            )
        
        # Validar capacidad de pago
        ratio_ingresos = cliente.ingresos_mensuales / cuota_mensual
        
        # Test Case: Aprobación automática (score > 700 y ratio >= 4x)
        if cliente.score_cifin >= self.SCORE_APROBACION_AUTOMATICA and ratio_ingresos >= 4:
            return self._crear_prestamo_aprobado(db, cliente_id, monto, plazo_meses, cuota_mensual)
        
        # Test Case: Análisis manual (score 600-700 y ratio >= 3x)
        if cliente.score_cifin >= 600 and ratio_ingresos >= self.RATIO_INGRESOS_MINIMO:
            return self._crear_prestamo_revision(db, cliente_id, monto, plazo_meses, cuota_mensual)
        
        # Cualquier otro caso: rechazado
        return self._crear_prestamo_rechazado(
            db, cliente_id, monto, plazo_meses,
            motivo=f"Ingresos insuficientes. Ratio: {ratio_ingresos:.1f}x (mínimo 3x)"
        )
    
    def _calcular_cuota(self, monto: float, plazo_meses: int, tasa_anual: float) -> float:
        tasa_mensual = tasa_anual / 12
        return monto * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)
    
    def _crear_prestamo_aprobado(self, db: Session, cliente_id: int, monto: float, plazo_meses: int, cuota: float):
        prestamo = Prestamo(
            cliente_id=cliente_id, monto_solicitado=monto, plazo_meses=plazo_meses,
            cuota_mensual=cuota, estado=EstadoPrestamo.APROBADO,
            fecha_decision=datetime.utcnow()
        )
        db.add(prestamo)
        db.commit()
        db.refresh(prestamo)
        return prestamo
    
    def _crear_prestamo_revision(self, db: Session, cliente_id: int, monto: float, plazo_meses: int, cuota: float):
        prestamo = Prestamo(
            cliente_id=cliente_id, monto_solicitado=monto, plazo_meses=plazo_meses,
            cuota_mensual=cuota, estado=EstadoPrestamo.EN_REVISION
        )
        db.add(prestamo)
        db.commit()
        db.refresh(prestamo)
        return prestamo
    
    def _crear_prestamo_rechazado(self, db: Session, cliente_id: int, monto: float, plazo_meses: int, motivo: str):
        prestamo = Prestamo(
            cliente_id=cliente_id, monto_solicitado=monto, plazo_meses=plazo_meses,
            estado=EstadoPrestamo.RECHAZADO, motivo_rechazo=motivo,
            fecha_decision=datetime.utcnow()
        )
        db.add(prestamo)
        db.commit()
        db.refresh(prestamo)
        return prestamo
    
    def obtener_estado_prestamo(self, db: Session, prestamo_id: int):
        """Obtiene el estado actual de un préstamo"""
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo:
            raise ValueError("Préstamo no encontrado")
        return prestamo
