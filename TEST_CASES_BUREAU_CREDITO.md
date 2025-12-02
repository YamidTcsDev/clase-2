# 🧪 Test Cases - Consulta Bureau de Crédito

## 📋 Información del Proyecto
- **Sistema:** Préstamos Bancarios
- **Módulo:** Consulta Bureau de Crédito (CIFIN/DataCrédito)
- **Usuario:** Oficial de Crédito
- **Criticidad:** Alta
- **Fecha:** 02/12/2025

---

## 📊 Casos de Prueba

| ID | Escenario | Pre-condiciones | Pasos | Resultado Esperado | Prioridad | Datos de Prueba |
|---|---|---|---|---|---|---|
| **TC-BC-001** | **Path Feliz - Cliente con Buen Historial** | - Cliente existe en BD<br>- Servicio Bureau disponible<br>- Usuario autenticado | 1. Ingresar documento: "1234567890"<br>2. Click en "Consultar Bureau"<br>3. Esperar respuesta | - Status 200<br>- Score: 750-900<br>- Deudas activas: 0-2<br>- Puntualidad: "Excelente"<br>- Mensaje: "Cliente apto para crédito"<br>- Tiempo respuesta: <3 seg | 🔴 Alta | Cliente ID: 1<br>Doc: "1234567890"<br>Nombre: "Juan Pérez"<br>Score esperado: 750 |
| **TC-BC-002** | **Cliente con Deudas Activas Controladas** | - Cliente con 3-5 deudas activas<br>- Score entre 600-700<br>- Servicio Bureau OK | 1. Ingresar documento: "0987654321"<br>2. Consultar Bureau<br>3. Validar detalle deudas | - Status 200<br>- Score: 650<br>- Deudas activas: 4<br>- Monto total: $8,000,000<br>- Puntualidad: "Regular"<br>- Mensaje: "Cliente requiere análisis" | 🔴 Alta | Doc: "0987654321"<br>Deudas activas: 4<br>Monto deudas: $8M<br>Score: 650 |
| **TC-BC-003** | **Cliente en Lista de Riesgo CIFIN** | - Cliente marcado como riesgo<br>- Estado: "BLOQUEADO"<br>- Tiene mora >90 días | 1. Ingresar documento: "5566778899"<br>2. Intentar consultar<br>3. Verificar bloqueo | - Status 403 Forbidden<br>- Mensaje: "Cliente en lista de riesgo. Consulta bloqueada"<br>- No se muestra score<br>- Alerta visual roja<br>- Log de seguridad registrado | 🔴 Alta | Doc: "5566778899"<br>Cliente: "Ana Martínez"<br>Estado: BLOQUEADO<br>Mora: 120 días |
| **TC-BC-004** | **Validación - Documento Inválido (Formato)** | - Usuario en pantalla consulta<br>- Campo documento vacío | 1. Ingresar documento: "ABC123XYZ"<br>2. Click "Consultar"<br>3. Observar validación | - Status 400 Bad Request<br>- Mensaje: "Documento inválido. Solo números permitidos"<br>- Campo documento resaltado en rojo<br>- No se consume servicio externo | 🟡 Media | Doc inválido: "ABC123XYZ"<br>Caracteres especiales: "@#$%"<br>Letras: "ABCDEF" |
| **TC-BC-005** | **Validación - Documento Vacío** | - Formulario en blanco<br>- Ningún campo completado | 1. Dejar campo documento vacío<br>2. Click "Consultar"<br>3. Verificar error | - Status 400<br>- Mensaje: "El documento es obligatorio"<br>- Focus automático en campo<br>- Botón consultar deshabilitado | 🟡 Media | Doc: "" (vacío)<br>Doc: null<br>Doc: "   " (espacios) |
| **TC-BC-006** | **Validación - Longitud Documento** | - Usuario en formulario | 1. Ingresar documento corto: "123"<br>2. Ingresar documento largo: "123456789012345"<br>3. Validar ambos casos | - Doc corto (<7): "Mínimo 7 dígitos"<br>- Doc largo (>15): "Máximo 15 dígitos"<br>- Status 400<br>- Validación en tiempo real | 🟡 Media | Doc corto: "123"<br>Doc largo: "12345678901234567890"<br>Doc válido: "1234567890" |
| **TC-BC-007** | **Error - Servicio Bureau Caído** | - Servicio externo Bureau no disponible<br>- Simular downtime | 1. Configurar mock service down<br>2. Ingresar documento válido<br>3. Consultar Bureau | - Status 503 Service Unavailable<br>- Mensaje: "Servicio Bureau temporalmente no disponible. Intente en 5 minutos"<br>- Opción "Reintentar"<br>- Log de error generado | 🔴 Alta | Mock: Service Down<br>HTTP 503<br>Connection Refused |
| **TC-BC-008** | **Error - Timeout 5 Segundos** | - Servicio externo lento<br>- Delay >5 seg configurado | 1. Simular delay de 7 segundos<br>2. Consultar documento: "1122334455"<br>3. Esperar timeout | - Status 504 Gateway Timeout<br>- Mensaje: "Tiempo de espera agotado. Reintente"<br>- Timeout exacto: 5 seg<br>- Transacción cancelada<br>- No se cobra consulta | 🔴 Alta | Timeout: 5000ms<br>Delay simulado: 7000ms<br>Retry: habilitado |
| **TC-BC-009** | **Error - Respuesta Inválida del Bureau** | - Servicio responde con JSON malformado<br>- Campos faltantes | 1. Mock respuesta sin campo "score"<br>2. Consultar documento válido<br>3. Procesar respuesta | - Status 500 Internal Server Error<br>- Mensaje: "Error procesando respuesta del Bureau"<br>- Fallback: consulta manual<br>- Alerta al supervisor | 🟡 Media | Response: `{"error": true}`<br>JSON malformado<br>Status 200 pero sin datos |
| **TC-BC-010** | **Edge Case - Cliente Sin Historial Crediticio** | - Cliente nuevo en sistema<br>- Score CIFIN = null<br>- Sin deudas registradas | 1. Consultar documento: "9998887776"<br>2. Procesar respuesta vacía<br>3. Validar manejo | - Status 200<br>- Score: 0<br>- tiene_historial: false<br>- Mensaje: "Cliente sin historial crediticio registrado"<br>- Recomendación: "Requiere garantías adicionales" | 🟡 Media | Doc: "9998887776"<br>Cliente: Nuevo<br>Score: null<br>Deudas: 0 |
| **TC-BC-011** | **Edge Case - Documento Duplicado (Consulta Reciente)** | - Cliente consultado hace <24h<br>- Límite: 1 consulta/24h por regulación | 1. Consultar documento: "1234567890"<br>2. Esperar 10 minutos<br>3. Re-consultar mismo documento | - Status 429 Too Many Requests<br>- Mensaje: "Límite de consultas: solo 1 permitida cada 24 horas"<br>- Mostrar última consulta en caché<br>- Fecha/hora última consulta | 🔴 Alta | Primera consulta: 10:00 AM<br>Segunda consulta: 10:10 AM<br>Delta: 10 minutos<br>Límite: 24 horas |
| **TC-BC-012** | **Edge Case - Cliente Extranjero (Pasaporte)** | - Documento tipo: Pasaporte<br>- Formato alfanumérico<br>- País: Colombia acepta extranjeros | 1. Seleccionar tipo: "Pasaporte"<br>2. Ingresar: "AB123456"<br>3. Consultar Bureau | - Status 200<br>- Búsqueda en Bureau internacional<br>- Si no existe: "Sin historial en Colombia"<br>- Sugerir: "Carta referencia bancaria del país origen" | 🟡 Media | Tipo: Pasaporte<br>Número: "AB123456"<br>País: "Venezuela"<br>Historial: No |
| **TC-BC-013** | **Seguridad - Inyección SQL en Campo Documento** | - Usuario malintencionado<br>- Intento de SQL injection | 1. Ingresar: "1234'; DROP TABLE clientes;--"<br>2. Enviar consulta<br>3. Verificar sanitización | - Status 400<br>- Input sanitizado correctamente<br>- Caracteres especiales rechazados<br>- Log de intento de inyección<br>- No ejecución de SQL malicioso | 🔴 Alta | Payload: `1234'; DROP TABLE--`<br>Payload: `1234 OR 1=1`<br>Payload: `<script>alert()</script>` |
| **TC-BC-014** | **Performance - Consultas Concurrentes** | - 50 usuarios simultáneos<br>- Sistema en horario pico<br>- Servicio Bureau con capacidad | 1. Generar 50 consultas paralelas<br>2. Diferentes documentos<br>3. Medir tiempos respuesta | - Todas Status 200<br>- Tiempo promedio: <3 seg<br>- Max tiempo: <5 seg<br>- 0% errores<br>- No degradación del servicio | 🟡 Media | Usuarios: 50 concurrentes<br>Documentos únicos: 50<br>Duración test: 1 minuto |
| **TC-BC-015** | **Cumplimiento Normativo - Auditoría de Consulta** | - Toda consulta debe quedar registrada<br>- Ley de habeas data | 1. Consultar documento: "1234567890"<br>2. Verificar tabla auditoría<br>3. Validar campos obligatorios | - Registro en tabla `auditoria_bureau`<br>- Campos: usuario, fecha_hora, documento, resultado, ip_origen<br>- Encriptación de datos sensibles<br>- Retención: 5 años<br>- Log inmutable | 🔴 Alta | Usuario: "oficial01"<br>IP: "192.168.1.100"<br>Timestamp: UTC<br>Resultado: "Exitoso" |

---

## 📈 Métricas de Cobertura

### Por Prioridad
- 🔴 **Alta:** 7 casos (47%)
- 🟡 **Media:** 8 casos (53%)

### Por Categoría
- ✅ **Happy Path:** 2 casos
- ⚠️ **Validaciones:** 3 casos
- ❌ **Errores:** 3 casos
- 🔍 **Edge Cases:** 4 casos
- 🔒 **Seguridad:** 1 caso
- ⚡ **Performance:** 1 caso
- 📋 **Normativo:** 1 caso

---

## 🎯 Criterios de Aceptación Generales

### Funcionales
- ✅ Tiempo de respuesta promedio <3 segundos
- ✅ Disponibilidad del servicio >99.5%
- ✅ Validación de datos antes de consulta externa
- ✅ Manejo de errores con mensajes claros al usuario

### No Funcionales
- 🔒 Encriptación TLS 1.3 en comunicación con Bureau
- 📊 Logs de auditoría para todas las consultas
- 🚀 Soporte para 100 consultas/minuto
- 💾 Caché de consultas por 24 horas

### Regulatorios
- 📜 Cumplimiento Ley 1266 de 2008 (Habeas Data)
- 🔐 Consentimiento del cliente para consulta
- 📋 Trazabilidad completa de operaciones
- ⏰ Retención de logs por 5 años

---

## 🔧 Configuración de Ambiente de Pruebas

### Variables de Entorno
```bash
BUREAU_API_URL=https://api-mock-bureau.test.com
BUREAU_TIMEOUT=5000
BUREAU_RETRY_ATTEMPTS=2
CACHE_TTL=86400  # 24 horas
LOG_LEVEL=DEBUG
```

### Datos de Prueba
```sql
-- Clientes para testing
INSERT INTO clientes (documento, nombre, score_cifin, estado) VALUES
('1234567890', 'Juan Pérez', 750, 'ACTIVO'),      -- TC-BC-001
('0987654321', 'María López', 650, 'ACTIVO'),     -- TC-BC-002
('5566778899', 'Ana Martínez', 450, 'BLOQUEADO'), -- TC-BC-003
('9998887776', 'Carlos Nuevo', NULL, 'ACTIVO');   -- TC-BC-010
```

---

## 📝 Notas Adicionales

### Bloqueos Identificados
1. Servicio Bureau mock requiere configuración de delays
2. Validar integración con sistema de auditoría
3. Confirmar límites de consultas con área legal

### Riesgos
- 🔴 **Alto:** Dependencia de servicio externo (SLA 95%)
- 🟡 **Medio:** Límite de consultas puede afectar UX
- 🟢 **Bajo:** Performance en horario pico

### Recomendaciones
1. Implementar circuit breaker para servicio Bureau
2. Caché inteligente para reducir consultas duplicadas
3. Dashboard de monitoreo en tiempo real
4. Plan de contingencia si Bureau no disponible

---

**Generado por:** QA Senior - Sistemas Bancarios  
**Fecha:** 02/12/2025  
**Versión:** 1.0
