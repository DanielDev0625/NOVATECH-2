# · Punto de entrada de la API: crea la app, registra las rutas y sirve el frontend.
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.configuracion import ESTATICOS
from app.modelos_db import Base, engine
from app.rutas import auth, energia, logistica, panel, trazabilidad


@asynccontextmanager
async def lifespan(app: FastAPI):
    # · Al arrancar crea las tablas que falten (no modifica las que ya existen).
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # · Si la base no responde en el arranque, la app sigue viva y cada petición informará el error.
        logging.getLogger("smartops").exception("No se pudieron crear/verificar las tablas")
    yield


app = FastAPI(title="SmartOps API", lifespan=lifespan)

# · Rutas públicas primero (login, registro, consulta de lotes por QR).
app.include_router(auth.router_publico)
app.include_router(trazabilidad.router_publico)

# · Rutas protegidas: cada módulo exige token.
app.include_router(auth.router)
app.include_router(trazabilidad.router)
app.include_router(logistica.router)
app.include_router(energia.router)
app.include_router(panel.router)


@app.get("/", include_in_schema=False)
def raiz():
    # · La raíz lleva a la pantalla de login.
    return RedirectResponse("/login.html")


# · El frontend (HTML, CSS, JS, imágenes) se monta al final para no tapar las rutas de la API.
app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="estaticos")
