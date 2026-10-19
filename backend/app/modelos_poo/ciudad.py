# · Clases de dominio para ciudades y distancias.
import math
from typing import Dict, List, Tuple


class Ciudad:
    # · Radio medio de la Tierra en km.
    RADIO_TIERRA_KM = 6371
    # · Factor para pasar de línea recta a distancia aproximada por carretera.
    FACTOR_CARRETERA = 1.25

    def __init__(self, nombre: str, latitud: float, longitud: float):
        self.nombre = nombre
        self.latitud = latitud
        self.longitud = longitud

    def distancia_a(self, otra: "Ciudad") -> float:
        # · Distancia en km por carretera hasta otra ciudad (fórmula de Haversine).
        p1, p2 = math.radians(self.latitud), math.radians(otra.latitud)
        a = (math.sin((p2 - p1) / 2) ** 2 +
             math.cos(p1) * math.cos(p2) *
             math.sin(math.radians(otra.longitud - self.longitud) / 2) ** 2)
        return round(self.RADIO_TIERRA_KM * 2 * math.asin(math.sqrt(a)) * self.FACTOR_CARRETERA, 1)


class CatalogoCiudades:
    # · Conjunto de ciudades conocidas; se construye a partir del diccionario de configuración.
    def __init__(self, datos: Dict[str, Tuple[float, float]]):
        self._ciudades = {n: Ciudad(n, lat, lon) for n, (lat, lon) in datos.items()}

    def existe(self, nombre: str) -> bool:
        return nombre in self._ciudades

    def obtener(self, nombre: str) -> Ciudad:
        return self._ciudades[nombre]

    def nombres(self) -> List[str]:
        # · Nombres ordenados alfabéticamente.
        return sorted(self._ciudades)
