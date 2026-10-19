# · Esquemas (Pydantic) de autenticación: validan los datos que llegan en login y registro.
from pydantic import BaseModel


class RegistroIn(BaseModel):
    # · Datos para crear una cuenta nueva.
    nombre: str
    email: str
    password: str


class LoginIn(BaseModel):
    # · Datos para iniciar sesión.
    email: str
    password: str
