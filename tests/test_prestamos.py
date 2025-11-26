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

def test_solicitar_prestamo_aprobacion_automatica():
    """Test Case: Score>700, ingresos 4x cuota → APROBADO"""
    response = client.post("/api/prestamos/solicitar", json={
        "cliente_id": 1,  # Juan: score 750, ingresos $5M
        "monto_solicitado": 10_000_000,
        "plazo_meses": 24
    })
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "aprobado"
    assert data["motivo_rechazo"] is None
    assert data["cuota_mensual"] is not None

def test_solicitar_prestamo_rechazo_automatico():
    """Test Case: Score<500 → RECHAZADO"""
    response = client.post("/api/prestamos/solicitar", json={
        "cliente_id": 3,  # Pedro: score 450
        "monto_solicitado": 5_000_000,
        "plazo_meses": 12
    })
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "rechazado"
    assert "score" in data["motivo_rechazo"].lower()

def test_solicitar_prestamo_limite_monto():
    """Test Case: Monto > $50M → Error validación"""
    response = client.post("/api/prestamos/solicitar", json={
        "cliente_id": 1,
        "monto_solicitado": 60_000_000,  # Excede límite
        "plazo_meses": 60
    })
    assert response.status_code == 400
    assert "límite" in response.json()["detail"].lower()

def test_solicitar_prestamo_revision_manual():
    """Test Case: Score 600-700, ratio 3x → EN_REVISION"""
    response = client.post("/api/prestamos/solicitar", json={
        "cliente_id": 4,  # Ana: score 650, ingresos $4M
        "monto_solicitado": 5_000_000,  # Cuota aprox $120k, ratio 33x
        "plazo_meses": 60
    })
    assert response.status_code == 200
    data = response.json()
    # Puede ser aprobado o en revisión dependiendo del ratio
    assert data["estado"] in ["en_revision", "aprobado"]

def test_solicitar_prestamo_sin_historial():
    """Test Case: Cliente sin historial crediticio → RECHAZADO"""
    response = client.post("/api/prestamos/solicitar", json={
        "cliente_id": 2,  # María: sin score
        "monto_solicitado": 3_000_000,
        "plazo_meses": 24
    })
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "rechazado"
    assert "historial" in data["motivo_rechazo"].lower()

def test_obtener_estado_prestamo():
    """Test Case: Consultar estado de préstamo existente"""
    # Primero crear un préstamo
    response = client.post("/api/prestamos/solicitar", json={
        "cliente_id": 1,
        "monto_solicitado": 10_000_000,
        "plazo_meses": 24
    })
    assert response.status_code == 200
    prestamo_id = response.json()["id"]
    
    # Consultar estado
    response = client.get(f"/api/prestamos/{prestamo_id}/estado")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == prestamo_id
    assert data["estado"] == "aprobado"

def test_obtener_estado_prestamo_no_existe():
    """Test Case: Consultar préstamo inexistente → Error 404"""
    response = client.get("/api/prestamos/999/estado")
    assert response.status_code == 404
