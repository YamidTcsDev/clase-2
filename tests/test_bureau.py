import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, SessionLocal, get_db
from app.models.cliente import Cliente, EstadoCliente
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup de base de datos de prueba
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override de la dependencia de base de datos para tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    """Setup y teardown de base de datos para cada test"""
    Base.metadata.create_all(bind=engine)
    
    # Seed data
    db = TestingSessionLocal()
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
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_consulta_bureau_path_feliz():
    """Test Case: Cliente con score 750 → Respuesta exitosa"""
    response = client.post("/api/bureau/consultar", json={"cliente_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 750
    assert data["tiene_historial"] == True
    assert "apto" in data["mensaje"].lower()

def test_consulta_bureau_sin_historial():
    """Test Case: Cliente sin historial → score=0, mensaje específico"""
    response = client.post("/api/bureau/consultar", json={"cliente_id": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 0
    assert data["tiene_historial"] == False
    assert "sin historial" in data["mensaje"].lower()

def test_consulta_bureau_cliente_bloqueado():
    """Test Case: Cliente en lista riesgo → Error 403"""
    response = client.post("/api/bureau/consultar", json={"cliente_id": 4})
    assert response.status_code == 403
    assert "bloqueado" in response.json()["detail"].lower()

def test_consulta_bureau_cliente_no_existe():
    """Test Case: Cliente inexistente → Error 400"""
    response = client.post("/api/bureau/consultar", json={"cliente_id": 999})
    assert response.status_code == 400
    assert "no encontrado" in response.json()["detail"].lower()

def test_obtener_ultima_consulta():
    """Test Case: Obtener consulta por GET"""
    response = client.get("/api/bureau/1")
    assert response.status_code == 200
    data = response.json()
    assert data["cliente_id"] == 1
    assert data["score"] == 750
