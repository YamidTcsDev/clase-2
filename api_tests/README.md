# 🧪 API Test Runner

Script Python para ejecutar test cases contra la API FastAPI de Clase 2.

## 📋 Descripción

Este script:
- ✅ Ejecuta 15 test cases automatizados
- ✅ Consume la API en `http://localhost:8000`
- ✅ Genera reporte en formato CSV
- ✅ Mide tiempos de respuesta
- ✅ Valida status codes y respuestas

## 🚀 Uso

### 1. Asegúrate de que el servidor esté corriendo

```bash
# En otra terminal
cd "c:\Users\2687259\Documents\IA BANISTMO - Formación TCS\clase2"
venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

### 2. Ejecuta el test runner

```bash
# Desde el directorio api_tests
cd api_tests
python test_runner.py
```

### 3. Revisa el reporte generado

El script genera `report_test_cases.csv` con los resultados.

## 📊 Test Cases Incluidos

### Bureau de Crédito (5 tests)
- **TC-BC-001:** Cliente con buen historial (score 750)
- **TC-BC-002:** Cliente sin historial crediticio
- **TC-BC-003:** Cliente bloqueado en lista de riesgo
- **TC-BC-004:** Cliente inexistente
- **TC-BC-005:** Obtener última consulta (GET)

### Préstamos (7 tests)
- **TC-PR-001:** Aprobación automática (score>700)
- **TC-PR-002:** Rechazo automático (score<500)
- **TC-PR-003:** Validación límite de monto (>$50M)
- **TC-PR-004:** Préstamo en revisión manual (score 600-700)
- **TC-PR-005:** Rechazo por falta de historial
- **TC-PR-006:** Consultar estado de préstamo
- **TC-PR-007:** Préstamo inexistente (404)

### Sistema (2 tests)
- **TC-SYS-001:** Health check
- **TC-SYS-002:** Endpoint raíz

## 📄 Formato del Reporte CSV

El archivo `report_test_cases.csv` contiene:

| Columna | Descripción |
|---------|-------------|
| ID | Identificador del test case |
| Escenario | Descripción del caso de prueba |
| Estado | PASS / FAIL |
| Esperado | Resultado esperado |
| Obtenido | Resultado obtenido |
| Tiempo (ms) | Tiempo de ejecución en milisegundos |
| Notas | Observaciones adicionales |
| Fecha | Timestamp de ejecución |

## 🔧 Requisitos

```bash
pip install requests
```

(Ya incluido en requirements.txt del proyecto principal)

## 📈 Ejemplo de Salida

```
============================================================
🚀 TEST RUNNER - API FASTAPI CLASE 2
============================================================
✅ Servidor disponible en http://localhost:8000
🧪 Iniciando ejecución de test cases...
📡 Servidor: http://localhost:8000
------------------------------------------------------------

📋 BUREAU DE CRÉDITO
  ✓ TC-BC-001 ejecutado
  ✓ TC-BC-002 ejecutado
  ✓ TC-BC-003 ejecutado
  ✓ TC-BC-004 ejecutado
  ✓ TC-BC-005 ejecutado

💰 PRÉSTAMOS
  ✓ TC-PR-001 ejecutado
  ✓ TC-PR-002 ejecutado
  ✓ TC-PR-003 ejecutado
  ✓ TC-PR-004 ejecutado
  ✓ TC-PR-005 ejecutado
  ✓ TC-PR-006 ejecutado
  ✓ TC-PR-007 ejecutado

⚙️  SISTEMA
  ✓ TC-SYS-001 ejecutado
  ✓ TC-SYS-002 ejecutado

============================================================
✅ Tests ejecutados: 15
✅ Pasados: 14 (93.3%)
❌ Fallidos: 1 (6.7%)
============================================================

📄 Reporte exportado: report_test_cases.csv

✅ Ejecución completada exitosamente!
```

## 💡 Tips

- El script valida automáticamente que el servidor esté disponible
- Los tiempos de respuesta se miden en milisegundos
- Cada test es independiente y no afecta a los demás
- El reporte CSV se puede abrir con Excel o cualquier editor de hojas de cálculo
