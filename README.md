TPFinal - Instrucciones de ejecución

Este repositorio contiene una aplicación Python que usa SQLite y una interfaz gráfica ligera.

**Requisitos**
- Python 3.11+ instalado en el sistema (se usó Python 3.12 en desarrollo).
- Windows (instrucciones y comandos están orientados a PowerShell/Windows).

**Estado actual**
- Las dependencias se instalan desde `requirements.txt` y se recomienda usar un virtualenv localizado en `.venv`.
- Se creó y probó el entorno virtual `.venv` y `main.py` arranca correctamente.

**Crear/activar entorno y (re)instalar dependencias**
PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Command Prompt (cmd.exe):
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Ejecutar la aplicación**
- Usando el Python del virtualenv (recomendado):
```powershell
.\.venv\Scripts\python.exe main.py
```

**Ejecutar tests**
```powershell
.\.venv\Scripts\python.exe -m pytest
```

**Notas y solución de problemas**
- Si aparece un import faltante (por ejemplo `ModuleNotFoundError: No module named 'bcrypt'`), instálalo con:
```powershell
.\.venv\Scripts\python.exe -m pip install bcrypt
```
- Si ves advertencias tipo "Ignoring invalid distribution ~ip", se pueden eliminar borrando la carpeta problemática en `.venv\Lib\site-packages`.
- La base de datos SQLite presente es `taller3d.db` (archivo en el repo). Verifica permisos si tienes errores de escritura.

**VS Code**
- Selecciona el intérprete del proyecto apuntando a `.venv\Scripts\python.exe` desde la esquina inferior derecha.

**Cómo invitar colaboradores**
- No puedo añadir usuarios al repo desde aquí; el propietario del repositorio debe invitarte en GitHub (Settings → Manage access → Invite collaborators).

Si querés, pruebo funcionalidades concretas de la app o genero pasos adicionales para desarrollo (ej. cómo ejecutar un flujo de ejemplo).
# tpfinal ADICTO AL PENE RACING PECHO FRIO
