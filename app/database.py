from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite en memoria - datos se pierden al cerrar API (ideal para demos)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# check_same_thread=False permite usar SQLite desde múltiples threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency para obtener sesión de DB en endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Crea todas las tablas al iniciar la API"""
    Base.metadata.create_all(bind=engine)

def seed_data(db):
    """Inserta datos iniciales para demostración"""
    from app.models.cliente import Cliente, EstadoCliente
    
    clientes_demo = [
        Cliente(
            id=1, nombre="Juan Pérez", identificacion="1234567890",
            email="juan@test.com", score_cifin=750, 
            ingresos_mensuales=5_000_000, estado=EstadoCliente.ACTIVO
        ),
        Cliente(
            id=2, nombre="María López", identificacion="0987654321",
            email="maria@test.com", score_cifin=None,  # Sin historial
            ingresos_mensuales=3_000_000, estado=EstadoCliente.ACTIVO
        ),
        Cliente(
            id=3, nombre="Pedro Gómez", identificacion="1122334455",
            email="pedro@test.com", score_cifin=450,  # Bajo score
            ingresos_mensuales=2_000_000, estado=EstadoCliente.ACTIVO
        ),
        Cliente(
            id=4, nombre="Ana Martínez", identificacion="5566778899",
            email="ana@test.com", score_cifin=650,
            ingresos_mensuales=4_000_000, estado=EstadoCliente.BLOQUEADO
        ),
    ]
    
    db.add_all(clientes_demo)
    db.commit()
    print("✅ Base de datos inicializada con 4 clientes demo")
