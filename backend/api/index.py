# · Punto de entrada para Vercel: expone la app FastAPI como función serverless.
import sys
from pathlib import Path

# · Asegura que el paquete "app" (carpeta backend/app) sea importable desde esta función.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402,F401
