# · Rutas de autenticación: registro, login y datos del usuario actual.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.esquemas.auth import LoginIn, RegistroIn
from app.modelos_db import Usuario, get_db
from app.servicios import usuarios as servicio
from app.servicios.seguridad import usuario_actual

# · Rutas públicas: no exigen token.
router_publico = APIRouter(prefix="/api")
# · Rutas protegidas: exigen un token válido.
router = APIRouter(prefix="/api", dependencies=[Depends(usuario_actual)])


@router_publico.post("/auth/registro")
def registro(d: RegistroIn, db: Session = Depends(get_db)):
    return servicio.registrar_usuario(db, d)


@router_publico.post("/auth/login")
def login(d: LoginIn, db: Session = Depends(get_db)):
    return servicio.iniciar_sesion(db, d)


@router.get("/auth/me")
def me(u: Usuario = Depends(usuario_actual)):
    return {"nombre": u.nombre, "email": u.email, "rol": u.rol}
