@echo off
REM Iniciador de RiesgoVivo (Windows): crea el entorno, instala dependencias y abre la app.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv .venv || (echo No se encontro Python. Instala Python 3.10 o superior. & pause & exit /b 1)
)

call ".venv\Scripts\activate.bat"
echo Instalando dependencias...
python -m pip install -q -r requirements.txt || (echo Error instalando dependencias. & pause & exit /b 1)

if not exist "data\emergencias_ungrd.csv" (
    echo ADVERTENCIA: falta data\emergencias_ungrd.csv. Ver README, paso 4.
)

echo Abriendo http://127.0.0.1:8000/  (Ctrl+C para detener)
start "" http://127.0.0.1:8000/
python manage.py runserver
pause
