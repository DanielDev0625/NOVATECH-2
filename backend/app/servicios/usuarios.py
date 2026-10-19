# · Lógica de negocio de usuarios: registrar una cuenta e iniciar sesión.
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.esquemas.auth import LoginIn, RegistroIn
from app.modelos_db import Usuario
from app.servicios.seguridad import crear_token, hash_password, verificar_password


def registrar_usuario(db: Session, d: RegistroIn) -> dict:
    email = d.email.strip().lower()
    if len(d.password) < 6:
        raise HTTPException(400, "La contraseña debe tener al menos 6 caracteres")
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(400, "El correo ya está registrado")
    # · El primer usuario que se registra queda como administrador; el resto como operarios.
    rol = "admin" if db.query(Usuario).count() == 0 else "operario"
    u = Usuario(nombre=d.nombre.strip(), email=email,
                password_hash=hash_password(d.password), rol=rol)
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"token": crear_token(u), "usuario": {"nombre": u.nombre, "rol": u.rol}}


def iniciar_sesion(db: Session, d: LoginIn) -> dict:
    u = db.query(Usuario).filter(Usuario.email == d.email.strip().lower()).first()
    # · Mismo mensaje para correo inexistente, usuario inactivo o clave mala (no revela cuál falló).
    if not u or u.activo is False or not verificar_password(d.password, u.password_hash):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {"token": crear_token(u), "usuario": {"nombre": u.nombre, "rol": u.rol}}
