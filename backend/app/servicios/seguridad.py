# · Seguridad: contraseñas, tokens JWT y la dependencia que identifica al usuario de cada petición.
from datetime import timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.configuracion import SECRET
from app.modelos_db import Usuario, ahora, get_db
from app.modelos_poo.hasher import HasherContrasena

# · Una sola instancia del hasher para toda la app.
_hasher = HasherContrasena()


def hash_password(clave: str) -> str:
    # · Genera el hash que se guarda en la base de datos.
    return _hasher.generar(clave)


def verificar_password(clave: str, guardado: str) -> bool:
    # · Comprueba una contraseña contra el hash guardado.
    return _hasher.verificar(clave, guardado)


def crear_token(u: Usuario) -> str:
    # · Token JWT con el id del usuario; caduca a las 12 horas.
    return jwt.encode({"sub": str(u.id), "exp": ahora() + timedelta(hours=12)},
                      SECRET, algorithm="HS256")


# · Lee el encabezado "Authorization: Bearer <token>" sin fallar si no viene.
bearer = HTTPBearer(auto_error=False)


def usuario_actual(cred: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
                   db: Session = Depends(get_db)) -> Usuario:
    # · Dependencia: devuelve el usuario dueño del token o responde 401.
    if not cred:
        raise HTTPException(401, "No autenticado")
    try:
        datos = jwt.decode(cred.credentials, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido")
    u = db.get(Usuario, int(datos["sub"]))
    if not u or u.activo is False:
        raise HTTPException(401, "Usuario no válido")
    return u
