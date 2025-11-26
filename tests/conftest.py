import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.cliente import Cliente, EstadoCliente

@pytest.fixture
def setup_db():
    """
    Crea DB en memoria para cada test.
    IMPORTANTE: Cada test tiene su propia instancia aislada.
    """
    # Crear engine temporal para tests
    SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Datos demo (mismo seed que startup)
    clientes = [
        Cliente(id=1, nombre="Juan Pérez", identificacion="1234567890",
                email="juan@test.com", score_cifin=750, 
                ingresos_mensuales=5_000_000, estado=EstadoCliente.ACTIVO),
        Cliente(id=2, nombre="María López", identificacion="0987654321",
                email="maria@test.com", score_cifin=None,
                ingresos_mensuales=3_000_000, estado=EstadoCliente.ACTIVO),
        Cliente(id=3, nombre="Pedro Gómez", identificacion="1122334455",
                email="pedro@test.com", score_cifin=450,
                ingresos_mensuales=2_000_000, estado=EstadoCliente.ACTIVO),
        Cliente(id=4, nombre="Ana Martínez", identificacion="5566778899",
                email="ana@test.com", score_cifin=650,
                ingresos_mensuales=4_000_000, estado=EstadoCliente.BLOQUEADO),
    ]
    
    db.add_all(clientes)
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)
