"""
Script para ejecutar test cases contra la API FastAPI
Servidor: http://localhost:8000
Genera reporte en formato CSV
"""

import requests
import csv
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Configuración
BASE_URL = "http://localhost:8000"
TIMEOUT = 5

class TestCaseRunner:
    def __init__(self):
        self.results = []
        self.test_count = 0
        self.passed = 0
        self.failed = 0
        
    def add_result(self, test_id: str, scenario: str, status: str, 
                   expected: str, actual: str, execution_time: float, notes: str = ""):
        """Agrega resultado de un test case"""
        self.test_count += 1
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
            
        self.results.append({
            "ID": test_id,
            "Escenario": scenario,
            "Estado": status,
            "Esperado": expected,
            "Obtenido": actual,
            "Tiempo (ms)": round(execution_time * 1000, 2),
            "Notas": notes,
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[requests.Response, float]:
        """Realiza petición HTTP y mide tiempo"""
        url = f"{BASE_URL}{endpoint}"
        start_time = datetime.now()
        try:
            response = requests.request(method, url, timeout=TIMEOUT, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            return response, execution_time
        except requests.exceptions.Timeout:
            execution_time = (datetime.now() - start_time).total_seconds()
            return None, execution_time
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return None, execution_time
    
    # ==================== BUREAU DE CRÉDITO ====================
    
    def test_bc_001_path_feliz(self):
        """TC-BC-001: Path Feliz - Cliente con Buen Historial"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/bureau/consultar",
            json={"cliente_id": 1}
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("score") == 750 and data.get("tiene_historial") == True:
                self.add_result(
                    "TC-BC-001", 
                    "Cliente con buen historial crediticio",
                    "PASS",
                    "Status 200, Score 750, historial=true",
                    f"Status {response.status_code}, Score {data.get('score')}, historial={data.get('tiene_historial')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-BC-001", 
                    "Cliente con buen historial crediticio",
                    "FAIL",
                    "Score 750, historial=true",
                    f"Score {data.get('score')}, historial={data.get('tiene_historial')}",
                    exec_time,
                    "Datos incorrectos en la respuesta"
                )
        else:
            status = response.status_code if response else "TIMEOUT"
            self.add_result(
                "TC-BC-001", 
                "Cliente con buen historial crediticio",
                "FAIL",
                "Status 200",
                f"Status {status}",
                exec_time,
                "Error en la petición HTTP"
            )
    
    def test_bc_002_sin_historial(self):
        """TC-BC-002: Cliente sin historial crediticio"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/bureau/consultar",
            json={"cliente_id": 2}
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("score") == 0 and data.get("tiene_historial") == False:
                self.add_result(
                    "TC-BC-002", 
                    "Cliente sin historial crediticio",
                    "PASS",
                    "Status 200, Score 0, historial=false",
                    f"Status {response.status_code}, Score {data.get('score')}, historial={data.get('tiene_historial')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-BC-002", 
                    "Cliente sin historial crediticio",
                    "FAIL",
                    "Score 0, historial=false",
                    f"Score {data.get('score')}, historial={data.get('tiene_historial')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-BC-002", 
                "Cliente sin historial crediticio",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_bc_003_cliente_bloqueado(self):
        """TC-BC-003: Cliente en lista de riesgo (bloqueado)"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/bureau/consultar",
            json={"cliente_id": 4}
        )
        
        expected_status = 403
        if response and response.status_code == expected_status:
            data = response.json()
            if "bloqueado" in data.get("detail", "").lower():
                self.add_result(
                    "TC-BC-003", 
                    "Cliente bloqueado en lista de riesgo",
                    "PASS",
                    f"Status {expected_status}, mensaje de bloqueo",
                    f"Status {response.status_code}, mensaje: {data.get('detail')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-BC-003", 
                    "Cliente bloqueado en lista de riesgo",
                    "FAIL",
                    "Mensaje de bloqueo",
                    f"Mensaje: {data.get('detail')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-BC-003", 
                "Cliente bloqueado en lista de riesgo",
                "FAIL",
                f"Status {expected_status}",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_bc_004_cliente_no_existe(self):
        """TC-BC-004: Cliente inexistente"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/bureau/consultar",
            json={"cliente_id": 999}
        )
        
        if response and response.status_code == 400:
            data = response.json()
            if "no encontrado" in data.get("detail", "").lower():
                self.add_result(
                    "TC-BC-004", 
                    "Cliente inexistente",
                    "PASS",
                    "Status 400, mensaje de error",
                    f"Status {response.status_code}, mensaje: {data.get('detail')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-BC-004", 
                    "Cliente inexistente",
                    "FAIL",
                    "Mensaje 'no encontrado'",
                    f"Mensaje: {data.get('detail')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-BC-004", 
                "Cliente inexistente",
                "FAIL",
                "Status 400",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_bc_005_get_ultima_consulta(self):
        """TC-BC-005: Obtener última consulta"""
        response, exec_time = self.make_request("GET", "/api/bureau/1")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("cliente_id") == 1:
                self.add_result(
                    "TC-BC-005", 
                    "Obtener última consulta (GET)",
                    "PASS",
                    "Status 200, cliente_id=1",
                    f"Status {response.status_code}, cliente_id={data.get('cliente_id')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-BC-005", 
                    "Obtener última consulta (GET)",
                    "FAIL",
                    "cliente_id=1",
                    f"cliente_id={data.get('cliente_id')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-BC-005", 
                "Obtener última consulta (GET)",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    # ==================== PRÉSTAMOS ====================
    
    def test_pr_001_aprobacion_automatica(self):
        """TC-PR-001: Aprobación automática (score>700, ingresos 4x)"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/prestamos/solicitar",
            json={
                "cliente_id": 1,
                "monto_solicitado": 10_000_000,
                "plazo_meses": 24
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("estado") == "aprobado":
                self.add_result(
                    "TC-PR-001", 
                    "Préstamo aprobado automáticamente",
                    "PASS",
                    "Status 200, estado=aprobado",
                    f"Status {response.status_code}, estado={data.get('estado')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-PR-001", 
                    "Préstamo aprobado automáticamente",
                    "FAIL",
                    "estado=aprobado",
                    f"estado={data.get('estado')}",
                    exec_time,
                    f"Motivo: {data.get('motivo_rechazo')}"
                )
        else:
            self.add_result(
                "TC-PR-001", 
                "Préstamo aprobado automáticamente",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_pr_002_rechazo_automatico(self):
        """TC-PR-002: Rechazo automático (score<500)"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/prestamos/solicitar",
            json={
                "cliente_id": 3,
                "monto_solicitado": 5_000_000,
                "plazo_meses": 12
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("estado") == "rechazado":
                self.add_result(
                    "TC-PR-002", 
                    "Préstamo rechazado (score bajo)",
                    "PASS",
                    "Status 200, estado=rechazado",
                    f"Status {response.status_code}, estado={data.get('estado')}, motivo={data.get('motivo_rechazo')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-PR-002", 
                    "Préstamo rechazado (score bajo)",
                    "FAIL",
                    "estado=rechazado",
                    f"estado={data.get('estado')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-PR-002", 
                "Préstamo rechazado (score bajo)",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_pr_003_limite_monto(self):
        """TC-PR-003: Validación límite de monto (>$50M)"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/prestamos/solicitar",
            json={
                "cliente_id": 1,
                "monto_solicitado": 60_000_000,
                "plazo_meses": 60
            }
        )
        
        if response and response.status_code == 400:
            data = response.json()
            if "límite" in data.get("detail", "").lower():
                self.add_result(
                    "TC-PR-003", 
                    "Validación límite de monto excedido",
                    "PASS",
                    "Status 400, mensaje de límite",
                    f"Status {response.status_code}, mensaje: {data.get('detail')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-PR-003", 
                    "Validación límite de monto excedido",
                    "FAIL",
                    "Mensaje de límite",
                    f"Mensaje: {data.get('detail')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-PR-003", 
                "Validación límite de monto excedido",
                "FAIL",
                "Status 400",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_pr_004_revision_manual(self):
        """TC-PR-004: Préstamo en revisión manual (score 600-700)"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/prestamos/solicitar",
            json={
                "cliente_id": 4,
                "monto_solicitado": 10_000_000,
                "plazo_meses": 36
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            expected_estado = "en_revision"
            if data.get("estado") == expected_estado:
                self.add_result(
                    "TC-PR-004", 
                    "Préstamo requiere revisión manual",
                    "PASS",
                    f"Status 200, estado={expected_estado}",
                    f"Status {response.status_code}, estado={data.get('estado')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-PR-004", 
                    "Préstamo requiere revisión manual",
                    "FAIL",
                    f"estado={expected_estado}",
                    f"estado={data.get('estado')}",
                    exec_time,
                    f"Motivo: {data.get('motivo_rechazo')}"
                )
        else:
            self.add_result(
                "TC-PR-004", 
                "Préstamo requiere revisión manual",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_pr_005_sin_historial(self):
        """TC-PR-005: Préstamo rechazado por falta de historial"""
        response, exec_time = self.make_request(
            "POST", 
            "/api/prestamos/solicitar",
            json={
                "cliente_id": 2,
                "monto_solicitado": 5_000_000,
                "plazo_meses": 12
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("estado") == "rechazado" and "historial" in data.get("motivo_rechazo", "").lower():
                self.add_result(
                    "TC-PR-005", 
                    "Préstamo rechazado sin historial",
                    "PASS",
                    "Status 200, estado=rechazado, motivo=sin historial",
                    f"Status {response.status_code}, estado={data.get('estado')}, motivo={data.get('motivo_rechazo')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-PR-005", 
                    "Préstamo rechazado sin historial",
                    "FAIL",
                    "estado=rechazado, motivo incluye 'historial'",
                    f"estado={data.get('estado')}, motivo={data.get('motivo_rechazo')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-PR-005", 
                "Préstamo rechazado sin historial",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_pr_006_consultar_estado(self):
        """TC-PR-006: Consultar estado de préstamo"""
        # Primero crear un préstamo
        create_response, _ = self.make_request(
            "POST", 
            "/api/prestamos/solicitar",
            json={
                "cliente_id": 1,
                "monto_solicitado": 10_000_000,
                "plazo_meses": 24
            }
        )
        
        if create_response and create_response.status_code == 200:
            prestamo_id = create_response.json().get("id")
            
            # Consultar estado
            response, exec_time = self.make_request("GET", f"/api/prestamos/{prestamo_id}/estado")
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get("id") == prestamo_id:
                    self.add_result(
                        "TC-PR-006", 
                        "Consultar estado de préstamo",
                        "PASS",
                        f"Status 200, id={prestamo_id}",
                        f"Status {response.status_code}, id={data.get('id')}, estado={data.get('estado')}",
                        exec_time
                    )
                else:
                    self.add_result(
                        "TC-PR-006", 
                        "Consultar estado de préstamo",
                        "FAIL",
                        f"id={prestamo_id}",
                        f"id={data.get('id')}",
                        exec_time
                    )
            else:
                self.add_result(
                    "TC-PR-006", 
                    "Consultar estado de préstamo",
                    "FAIL",
                    "Status 200",
                    f"Status {response.status_code if response else 'ERROR'}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-PR-006", 
                "Consultar estado de préstamo",
                "FAIL",
                "No se pudo crear préstamo previo",
                f"Status {create_response.status_code if create_response else 'ERROR'}",
                0
            )
    
    def test_pr_007_prestamo_no_existe(self):
        """TC-PR-007: Consultar préstamo inexistente"""
        response, exec_time = self.make_request("GET", "/api/prestamos/999/estado")
        
        if response and response.status_code == 404:
            data = response.json()
            if "no encontrado" in data.get("detail", "").lower():
                self.add_result(
                    "TC-PR-007", 
                    "Consultar préstamo inexistente",
                    "PASS",
                    "Status 404, mensaje de error",
                    f"Status {response.status_code}, mensaje: {data.get('detail')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-PR-007", 
                    "Consultar préstamo inexistente",
                    "FAIL",
                    "Mensaje 'no encontrado'",
                    f"Mensaje: {data.get('detail')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-PR-007", 
                "Consultar préstamo inexistente",
                "FAIL",
                "Status 404",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    # ==================== HEALTH CHECK ====================
    
    def test_health_check(self):
        """TC-SYS-001: Health check del sistema"""
        response, exec_time = self.make_request("GET", "/health")
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                self.add_result(
                    "TC-SYS-001", 
                    "Health check del sistema",
                    "PASS",
                    "Status 200, status=OK",
                    f"Status {response.status_code}, status={data.get('status')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-SYS-001", 
                    "Health check del sistema",
                    "FAIL",
                    "status=OK",
                    f"status={data.get('status')}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-SYS-001", 
                "Health check del sistema",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def test_root_endpoint(self):
        """TC-SYS-002: Endpoint raíz"""
        response, exec_time = self.make_request("GET", "/")
        
        if response and response.status_code == 200:
            data = response.json()
            if "message" in data:
                self.add_result(
                    "TC-SYS-002", 
                    "Endpoint raíz",
                    "PASS",
                    "Status 200, contiene 'message'",
                    f"Status {response.status_code}, message={data.get('message')}",
                    exec_time
                )
            else:
                self.add_result(
                    "TC-SYS-002", 
                    "Endpoint raíz",
                    "FAIL",
                    "Contiene 'message'",
                    f"Respuesta: {data}",
                    exec_time
                )
        else:
            self.add_result(
                "TC-SYS-002", 
                "Endpoint raíz",
                "FAIL",
                "Status 200",
                f"Status {response.status_code if response else 'ERROR'}",
                exec_time
            )
    
    def run_all_tests(self):
        """Ejecuta todos los test cases"""
        print("🧪 Iniciando ejecución de test cases...")
        print(f"📡 Servidor: {BASE_URL}")
        print("-" * 60)
        
        # Bureau de Crédito
        print("\n📋 BUREAU DE CRÉDITO")
        self.test_bc_001_path_feliz()
        print("  ✓ TC-BC-001 ejecutado")
        self.test_bc_002_sin_historial()
        print("  ✓ TC-BC-002 ejecutado")
        self.test_bc_003_cliente_bloqueado()
        print("  ✓ TC-BC-003 ejecutado")
        self.test_bc_004_cliente_no_existe()
        print("  ✓ TC-BC-004 ejecutado")
        self.test_bc_005_get_ultima_consulta()
        print("  ✓ TC-BC-005 ejecutado")
        
        # Préstamos
        print("\n💰 PRÉSTAMOS")
        self.test_pr_001_aprobacion_automatica()
        print("  ✓ TC-PR-001 ejecutado")
        self.test_pr_002_rechazo_automatico()
        print("  ✓ TC-PR-002 ejecutado")
        self.test_pr_003_limite_monto()
        print("  ✓ TC-PR-003 ejecutado")
        self.test_pr_004_revision_manual()
        print("  ✓ TC-PR-004 ejecutado")
        self.test_pr_005_sin_historial()
        print("  ✓ TC-PR-005 ejecutado")
        self.test_pr_006_consultar_estado()
        print("  ✓ TC-PR-006 ejecutado")
        self.test_pr_007_prestamo_no_existe()
        print("  ✓ TC-PR-007 ejecutado")
        
        # Sistema
        print("\n⚙️  SISTEMA")
        self.test_health_check()
        print("  ✓ TC-SYS-001 ejecutado")
        self.test_root_endpoint()
        print("  ✓ TC-SYS-002 ejecutado")
        
        print("\n" + "=" * 60)
        print(f"✅ Tests ejecutados: {self.test_count}")
        print(f"✅ Pasados: {self.passed} ({round(self.passed/self.test_count*100, 1)}%)")
        print(f"❌ Fallidos: {self.failed} ({round(self.failed/self.test_count*100, 1)}%)")
        print("=" * 60)
    
    def export_to_csv(self, filename: str = "report_test_cases.csv"):
        """Exporta resultados a CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["ID", "Escenario", "Estado", "Esperado", "Obtenido", "Tiempo (ms)", "Notas", "Fecha"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        
        print(f"\n📄 Reporte exportado: {filename}")

def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("🚀 TEST RUNNER - API FASTAPI CLASE 2")
    print("=" * 60)
    
    runner = TestCaseRunner()
    
    # Verificar conectividad
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ Servidor disponible en {BASE_URL}")
        else:
            print(f"⚠️  Servidor responde pero con status {response.status_code}")
    except:
        print(f"❌ ERROR: No se puede conectar a {BASE_URL}")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   uvicorn app.main:app --reload --port 8000")
        return
    
    # Ejecutar tests
    runner.run_all_tests()
    
    # Exportar resultados
    runner.export_to_csv()
    
    print("\n✅ Ejecución completada exitosamente!")

if __name__ == "__main__":
    main()
