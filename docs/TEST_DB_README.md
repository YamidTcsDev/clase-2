**Test DB — Uso y mantenimiento**

- **Ubicación:** `./test.db` (archivo SQLite en la raíz del proyecto).
- **Propósito:** base de datos de demostración con datos seed (4 clientes) usada por la API para pruebas locales.

Contenido y advertencias
- **Tablas relevantes:** `clientes` (vista desde los modelos de `app/models`).
- **Datos:** contiene datos de ejemplo; revisa que no existan datos sensibles antes de compartir o publicar el repositorio.
- **Tamaño:** es un archivo SQLite pequeño; si crece, considera usar fixtures o un dump SQL en lugar del binario.

Resetear la base de datos local
- Para borrar y recrear la base de datos demo (desde PowerShell):
  ```powershell
  # detener servidor si está corriendo (opcional)
  taskkill /F /IM python.exe /T

  # eliminar archivo de base de datos
  Remove-Item .\test.db

  # arrancar la API; en startup se recrean tablas y se hace seed automático
  .\.venv\Scripts\Activate.ps1
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```

Exportar la DB a SQL (dump)
- Con el cliente `sqlite3` instalado:
  ```powershell
  sqlite3 test.db ".output dump.sql" ".dump" ".exit"
  ```
- Alternativa Python (guarda SQL):
  ```powershell
  python - <<'PY'
  import sqlite3
  conn = sqlite3.connect('test.db')
  with open('dump.sql','w',encoding='utf-8') as f:
      for line in conn.iterdump():
          f.write('%s\n' % line)
  conn.close()
  PY
  ```

Importar un dump SQL
- Con `sqlite3`:
  ```powershell
  sqlite3 test.db < dump.sql
  ```

Gestión en Git
- `test.db` está incluido en este repositorio por conveniencia demo. Si prefieres no versionarlo en el futuro:
  - elimina `test.db` del repo: `git rm --cached test.db` y añade `test.db` a `.gitignore`.
  - usa en su lugar `dump.sql` o fixtures (recomendado para CI / repos públicos).

Soporte / notas
- Si quieres que genere y suba un `dump.sql` en lugar del binario, lo creo y lo commiteo.
- Si quieres que el seed use datos anónimos distintos, indícamelo y actualizo `app/database.py`.

---
Archivo generado automáticamente para documentar el uso del demo DB.
