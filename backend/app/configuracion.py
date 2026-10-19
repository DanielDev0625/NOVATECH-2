# · Configuración central: aquí viven las constantes y las variables de entorno de toda la app.
import os
from pathlib import Path

from dotenv import load_dotenv

# · Carga el archivo backend/.env (un nivel por encima de la carpeta app).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# · Clave con la que se firman los tokens JWT. En producción debe venir de la variable SECRET_KEY.
SECRET = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo")

# · Factores de emisión de CO2: kg por kWh consumido y kg por km recorrido.
FE_KWH = float(os.getenv("FACTOR_EMISION_KWH", "0.126"))
FE_KM = float(os.getenv("FACTOR_EMISION_KM", "0.25"))

# · Porcentaje de comisión que se cobra sobre la tarifa de cada pedido (10 %).
COMISION = 0.10

# · Estados válidos de un pedido.
ESTADOS_PEDIDO = ["Pendiente", "En ruta", "Entregado", "Cancelado"]

# · Etapas que se crean en cada lote nuevo: (nombre, días hasta la fecha límite).
ETAPAS_BASE = [("Producción", 2), ("Almacenamiento", 4), ("Entrega", 7)]

# · Carpeta del frontend (backend/estaticos), donde están los HTML, CSS, JS e imágenes.
ESTATICOS = Path(__file__).resolve().parent.parent / "estaticos"

# · Ciudades disponibles para logística: nombre -> (latitud, longitud).
CIUDADES = {
    "Barranquilla": (10.9685, -74.7813), "Cartagena": (10.3910, -75.4794),
    "Santa Marta": (11.2408, -74.1990), "Bogotá": (4.7110, -74.0721),
    "Medellín": (6.2442, -75.5812), "Cali": (3.4516, -76.5320),
    "Bucaramanga": (7.1193, -73.1227), "Cúcuta": (7.8939, -72.5078),
}
