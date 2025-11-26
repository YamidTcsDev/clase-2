# 🚀 API FastAPI para Test Cases - Clase 2

API REST con FastAPI para ejecutar test cases de **Consulta Bureau de Crédito** y **Aprobación de Préstamo**.

## 📋 Descripción

Esta API implementa los test cases de la Clase 2, incluyendo:

### 1. **Bureau de Crédito**
- ✅ Path feliz: Cliente con historial crediticio
- ⚠️ Sin historial: Cliente nuevo
- ❌ Cliente bloqueado
- ⚠️ Límite de consultas (1 cada 24h)

### 2. **Aprobación de Préstamo**
- ✅ Aprobación automática: score > 700, ingresos 4x cuota
- ⚠️ Análisis manual: score 600-700, ingresos 3x cuota
- ❌ Rechazo automático: score < 500
- ❌ Límite de monto: $50M máximo

## 🛠️ Stack Tecnológico

- Python 3.10+
- FastAPI
- SQLAlchemy (ORM)
- SQLite en memoria
- Pydantic (validación)
- pytest (testing)

## 📂 Estructura del Proyecto

```
clase2/
├── app/
│   ├── models/          # Modelos SQLAlchemy (Cliente, Prestamo)
│   ├── schemas/         # Schemas Pydantic (Request/Response)
│   ├── routers/         # Endpoints FastAPI
│   ├── services/        # Lógica de negocio
│   ├── database.py      # Configuración DB
│   ├── config.py        # Configuraciones
│   └── main.py          # Punto de entrada
├── tests/               # Tests automatizados con pytest
├── requirements.txt
└── README.md
```

## 🚀 Instalación y Ejecución

### 1. Crear entorno virtual

Es **IMPORTANTE** usar un entorno virtual para evitar conflictos de dependencias:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**Nota**: Verás `(venv)` al inicio de tu terminal cuando el entorno virtual esté activado.

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

Este comando instalará:
- FastAPI 0.104.1
- Uvicorn 0.24.0 (servidor ASGI)
- SQLAlchemy 2.0.23 (ORM)
- Pydantic 2.4.2 (validación)
- pytest y otras herramientas de testing

### 3. Levantar el servidor FastAPI

#### Opción 1: Con entorno virtual activado (Recomendado)

```bash
# Asegúrate de estar en el directorio del proyecto
cd "c:\Users\2687259\Documents\IA BANISTMO - Formación TCS\clase2"

# Activa el entorno virtual si no está activado
venv\Scripts\activate

# Inicia el servidor
uvicorn app.main:app --reload --port 8000
```

#### Opción 2: Sin activar el entorno virtual (Directa)

```bash
# Desde el directorio del proyecto
venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

### ✅ Verificar que el servidor está funcionando

Deberías ver en la terminal:

```
INFO:     Will watch for changes in these directories: ['c:\\Users\\...\\clase2']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
🚀 Inicializando base de datos en memoria...
✅ Base de datos inicializada con 4 clientes demo
INFO:     Application startup complete.
```

La API estará disponible en:
- **API Principal**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs (📚 Documentación interactiva)
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

### 🛑 Detener el servidor

Presiona `CTRL+C` en la terminal donde se está ejecutando el servidor.

## 🧪 Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest --cov=app tests/

# Test específico
pytest tests/test_bureau.py -v
```

## 📊 Endpoints Disponibles

### Bureau de Crédito

#### POST `/api/bureau/consultar`
Consulta el score y historial crediticio de un cliente.

**Request:**
```json
{
  "cliente_id": 1
}
```

**Response (200):**
```json
{
  "cliente_id": 1,
  "score": 750,
  "deudas_activas": 2,
  "monto_deudas": 5000000.0,
  "puntualidad": "Excelente",
  "tiene_historial": true,
  "fecha_consulta": "2025-11-26T10:30:00",
  "mensaje": "Score 750. Cliente apto para crédito."
}
```

#### GET `/api/bureau/{cliente_id}`
Obtiene la última consulta de un cliente.

### Préstamos

#### POST `/api/prestamos/solicitar`
Crea una nueva solicitud de préstamo.

**Request:**
```json
{
  "cliente_id": 1,
  "monto_solicitado": 10000000,
  "plazo_meses": 24
}
```

**Response (200):**
```json
{
  "id": 1,
  "cliente_id": 1,
  "monto_solicitado": 10000000.0,
  "plazo_meses": 24,
  "cuota_mensual": 483871.0,
  "estado": "aprobado",
  "motivo_rechazo": null,
  "fecha_solicitud": "2025-11-26T10:30:00"
}
```

#### GET `/api/prestamos/{prestamo_id}/estado`
Consulta el estado de un préstamo.

## 💾 Base de Datos

La API usa **SQLite en memoria** (`sqlite:///:memory:`), lo que significa:

- ✅ No requiere instalación externa
- ✅ Ideal para demos y pruebas
- ⚠️ Los datos se pierden al reiniciar la API
- ⚠️ Cada ejecución inicia con datos limpios

### Datos Demo Iniciales

Al iniciar la API, se cargan 4 clientes de prueba:

1. **Juan Pérez** (ID: 1) - Score 750, ingresos $5M → Perfil aprobación automática
2. **María López** (ID: 2) - Sin score, ingresos $3M → Sin historial
3. **Pedro Gómez** (ID: 3) - Score 450, ingresos $2M → Rechazo automático
4. **Ana Martínez** (ID: 4) - Score 650, ingresos $4M → Cliente bloqueado

### Persistir Datos

Para persistir datos entre reinicios, cambiar en `app/database.py`:

```python
# Memoria (actual)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Archivo local (persiste)
SQLALCHEMY_DATABASE_URL = "sqlite:///./testcases.db"
```

## 🎯 Test Cases Implementados

### Bureau de Crédito
- ✅ `test_consulta_bureau_path_feliz`
- ✅ `test_consulta_bureau_sin_historial`
- ✅ `test_consulta_bureau_cliente_bloqueado`
- ✅ `test_consulta_bureau_cliente_no_existe`
- ✅ `test_obtener_ultima_consulta`

### Préstamos
- ✅ `test_solicitar_prestamo_aprobacion_automatica`
- ✅ `test_solicitar_prestamo_rechazo_automatico`
- ✅ `test_solicitar_prestamo_limite_monto`
- ✅ `test_solicitar_prestamo_revision_manual`
- ✅ `test_solicitar_prestamo_sin_historial`
- ✅ `test_obtener_estado_prestamo`
- ✅ `test_obtener_estado_prestamo_no_existe`

## 🔧 Configuración

Límites de negocio definidos en `app/config.py`:

- Monto máximo préstamo: $50,000,000
- Plazo máximo: 60 meses
- Score aprobación automática: 700
- Score rechazo automático: 500
- Ratio mínimo ingresos/cuota: 3x

## 📝 Ejemplos de Uso

### Usando curl

```bash
# Consultar bureau
curl -X POST http://localhost:8000/api/bureau/consultar \
  -H "Content-Type: application/json" \
  -d '{"cliente_id": 1}'

# Solicitar préstamo
curl -X POST http://localhost:8000/api/prestamos/solicitar \
  -H "Content-Type: application/json" \
  -d '{"cliente_id": 1, "monto_solicitado": 10000000, "plazo_meses": 24}'
```

### Usando Python

```python
import requests

# Consultar bureau
response = requests.post(
    "http://localhost:8000/api/bureau/consultar",
    json={"cliente_id": 1}
)
print(response.json())

# Solicitar préstamo
response = requests.post(
    "http://localhost:8000/api/prestamos/solicitar",
    json={
        "cliente_id": 1,
        "monto_solicitado": 10000000,
        "plazo_meses": 24
    }
)
print(response.json())
```

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'app'`

Asegúrate de estar en el directorio correcto y ejecutar:
```bash
# Desde el directorio clase2/
uvicorn app.main:app --reload
```

### Error: `sqlite3.OperationalError: no such table`

La base de datos en memoria se inicializa al arrancar. Reinicia la API:
```bash
# Detener: Ctrl+C
# Reiniciar:
uvicorn app.main:app --reload
```

### Tests fallan

Asegúrate de tener todas las dependencias instaladas:
```bash
pip install -r requirements.txt
```

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [pytest](https://docs.pytest.org/)

## 🎓 Próximos Pasos

1. Completar endpoint transferencias internacionales
2. Agregar autenticación JWT
3. Conectar a PostgreSQL corporativo
4. Integrar con frontend Angular (Clase 8)
5. Deploy a servidor/cloud

## 📧 Contacto

Proyecto desarrollado para **IA BANISTMO - Formación TCS - Clase 2**

---

**Nota**: Esta API usa SQLite en memoria. Los datos no persisten entre reinicios. Ideal para demos y aprendizaje.
