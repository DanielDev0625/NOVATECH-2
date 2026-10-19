# · Configuración central: aquí viven las constantes y las variables de entorno de toda la app.
import os
from pathlib import Path

from dotenv import load_dotenv

# · Carga el archivo backend/.env (un nivel por encima de la carpeta app).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# · Cuando corre en Vercel, la variable VERCEL está definida.
EN_VERCEL = bool(os.getenv("VERCEL"))

# · Clave con la que se firman los tokens JWT. En producción debe venir de la variable SECRET_KEY.
SECRET = os.getenv("SECRET_KEY", "")
if not SECRET:
    if EN_VERCEL:
        # · Sin clave propia cualquiera podría falsificar sesiones; es mejor fallar con un mensaje claro.
        raise RuntimeError("Falta la variable de entorno SECRET_KEY en Vercel.")
    SECRET = "clave-solo-para-desarrollo"

# · Diferencia horaria del negocio respecto a UTC (Colombia = -5). Se usa para "hoy", "ayer", etc.
UTC_OFFSET_HORAS = int(os.getenv("UTC_OFFSET_HORAS", "-5"))

# · Factores de emisión de CO2: kg por kWh consumido y kg por km recorrido.
FE_KWH = float(os.getenv("FACTOR_EMISION_KWH", "0.126"))
FE_KM = float(os.getenv("FACTOR_EMISION_KM", "0.25"))

# · Porcentaje de comisión que se cobra sobre la tarifa de cada pedido (10 %).
COMISION = 0.10

# · Estados válidos de un pedido.
ESTADOS_PEDIDO = ["Pendiente", "En ruta", "Entregado", "Cancelado"]

# · Etapas que se crean en cada lote nuevo: (nombre, días hasta la fecha límite).
ETAPAS_BASE = [("Producción", 2), ("Almacenamiento", 4), ("Entrega", 7)]

# · Carpeta del frontend (backend/public), donde están los HTML, CSS, JS e imágenes.
# · Vercel sirve esta carpeta directamente; en local la sirve FastAPI.
ESTATICOS = Path(__file__).resolve().parent.parent / "public"

# · Ciudades disponibles para logística: nombre -> (latitud, longitud).
CIUDADES = {
    "Barranquilla": (10.9685, -74.7813), "Cartagena": (10.3910, -75.4794),
    "Santa Marta": (11.2408, -74.1990), "Bogotá": (4.7110, -74.0721),
    "Medellín": (6.2442, -75.5812), "Cali": (3.4516, -76.5320),
    "Bucaramanga": (7.1193, -73.1227), "Cúcuta": (7.8939, -72.5078),
}
