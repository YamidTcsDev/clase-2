import pytest
import httpx
from datetime import datetime, timedelta

from app import database
from app.models.cliente import Cliente, EstadoCliente


BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="module")
def db_session():
    # Ensure DB and tables exist
    database.init_db()
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upsert_cliente(db, cliente_id, identificacion, score, estado=EstadoCliente.ACTIVO, email=None):
    # Remove existing with same id if present
    existing = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if existing:
        db.delete(existing)
        db.commit()

    cliente = Cliente(
        id=cliente_id,
        nombre=f"Test {cliente_id}",
        identificacion=identificacion,
        email=email or f"test{cliente_id}@example.com",
        score_cifin=score,
        ingresos_mensuales=1000.0,
        estado=estado
    )
    db.add(cliente)
    db.commit()


@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=10.0)


def test_tp_01_path_feliz(db_session, client):
    upsert_cliente(db_session, 1001, "1001-IDENT", 750, EstadoCliente.ACTIVO)
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1001})
    assert r.status_code == 200
    body = r.json()
    assert body["cliente_id"] == 1001
    assert body["score"] == 750
    assert body["tiene_historial"] is True


def test_tp_02_cliente_con_deudas_activas(db_session, client):
    upsert_cliente(db_session, 1002, "1002-IDENT", 680, EstadoCliente.ACTIVO)
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1002})
    assert r.status_code == 200
    body = r.json()
    assert body["deudas_activas"] >= 0
    assert body["monto_deudas"] >= 0.0


def test_tp_03_cliente_en_lista_riesgo(db_session, client):
    upsert_cliente(db_session, 1003, "1003-IDENT", 600, EstadoCliente.BLOQUEADO)
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1003})
    assert r.status_code == 403


def test_tp_04_validacion_documento_invalido(client):
    r = client.post("/api/bureau/consultar", json={"cliente_id": "ABC123"})
    assert r.status_code == 422


@pytest.mark.skip("Requiere capacidad de simular caída del servicio externo (test double)")
def test_tp_05_servicio_externo_caido(client):
    # Simulación requerida en la integración para que este test sea válido
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1010})
    assert r.status_code in (502, 503)


@pytest.mark.skip("Requiere simular latencia >5s en integración externa")
def test_tp_06_timeout_5s(client):
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1011})
    assert r.status_code == 504


@pytest.mark.skip("Requiere simular respuesta inválida del servicio externo")
def test_tp_07_respuesta_invalida(client):
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1012})
    assert r.status_code in (500, 502)


@pytest.mark.skip("Duplicidad en identificaciones requiere cambiar esquema de BD o endpoint de creación")
def test_tp_08_documento_duplicado(db_session, client):
    # DB tiene constraint unique; test de duplicidad requiere un flujo diferente
    pytest.skip("Requiere manipulación de la base para crear inconsistencia")


def test_tp_09_cliente_extranjero(db_session, client):
    upsert_cliente(db_session, 2001, "EXT-999", None, EstadoCliente.ACTIVO)
    r = client.post("/api/bureau/consultar", json={"cliente_id": 2001})
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 0
    assert body["tiene_historial"] is False


def test_tp_10_sin_historial(db_session, client):
    upsert_cliente(db_session, 1004, "1004-IDENT", None, EstadoCliente.ACTIVO)
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1004})
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 0
    assert body["tiene_historial"] is False


def test_tp_11_get_ultima_consulta_existente(db_session, client):
    # Ensure a client exists (seeded or upserted)
    upsert_cliente(db_session, 1, "1234567890", 750, EstadoCliente.ACTIVO)
    r = client.get("/api/bureau/1")
    assert r.status_code == 200
    body = r.json()
    assert body["cliente_id"] == 1


def test_tp_12_get_ultima_consulta_no_existente(client):
    r = client.get("/api/bureau/9999")
    assert r.status_code == 404


@pytest.mark.skip("Requiere registro de última consulta en tabla de consultas (no implementado)")
def test_tp_13_limite_consultas_24h(client):
    r = client.post("/api/bureau/consultar", json={"cliente_id": 1005})
    assert r.status_code == 429


def test_tp_14_cliente_id_negativo(client):
    r = client.post("/api/bureau/consultar", json={"cliente_id": -1})
    # Servicio retorna 400 para 'Cliente no encontrado' en ese caso
    assert r.status_code == 400


def test_tp_15_payload_incompleto(client):
    r = client.post("/api/bureau/consultar", json={})
    assert r.status_code == 422
