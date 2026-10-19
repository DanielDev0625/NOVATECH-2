# · Clase que calcula rutas de entrega.
from typing import Callable, List


class PlanificadorRuta:
    # · Recibe una función distancia(origen, destino) -> km, para no depender de cómo se calcule.
    def __init__(self, distancia: Callable[[str, str], float]):
        self._distancia = distancia

    def vecino_mas_cercano(self, origen: str, destinos: List[str]) -> dict:
        # · Ruta por vecino más cercano: desde donde se está, va siempre al destino más próximo.
        pendientes = list(dict.fromkeys(destinos))  # · quita destinos repetidos y conserva el orden
        actual, tramos, total = origen, [], 0.0
        while pendientes:
            siguiente = min(pendientes, key=lambda c: self._distancia(actual, c))
            km = self._distancia(actual, siguiente)
            tramos.append({"desde": actual, "hasta": siguiente, "km": km})
            total += km
            actual = siguiente
            pendientes.remove(siguiente)
        return {"tramos": tramos, "total_km": round(total, 1)}
