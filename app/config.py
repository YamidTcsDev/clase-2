import os

class Settings:
    # API Settings
    API_TITLE = "API Test Cases - Clase 2"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "API REST para ejecutar test cases de Bureau, Préstamos y Transferencias"
    
    # Database Settings
    DATABASE_URL = "sqlite:///:memory:"
    
    # Límites de negocio
    LIMITE_MONTO_PRESTAMO = 50_000_000
    PLAZO_MAXIMO_MESES = 60
    SCORE_APROBACION_AUTOMATICA = 700
    SCORE_RECHAZO_AUTOMATICO = 500
    RATIO_INGRESOS_MINIMO = 3
    
settings = Settings()
