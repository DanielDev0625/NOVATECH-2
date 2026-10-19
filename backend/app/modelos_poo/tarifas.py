# · Clase que analiza las franjas de tarifa eléctrica y recomienda cuándo producir.
from typing import Sequence


class RecomendadorTarifa:
    def recomendar(self, tarifas: Sequence) -> dict:
        # · Cada tarifa debe tener: nombre, hora_inicio, hora_fin y valor_kwh.
        if not tarifas:
            return {"mensaje": "Registra tarifas por franja horaria para recibir recomendaciones."}
        mejor = min(tarifas, key=lambda t: t.valor_kwh)
        peor = max(tarifas, key=lambda t: t.valor_kwh)
        ahorro = round((1 - mejor.valor_kwh / peor.valor_kwh) * 100) if peor.valor_kwh else 0
        return {"mensaje": f"Programa los procesos de mayor consumo en la franja '{mejor.nombre}' "
                           f"({mejor.hora_inicio}:00 a {mejor.hora_fin}:00), a {mejor.valor_kwh:g} por kWh: "
                           f"hasta {ahorro}% menos que en '{peor.nombre}'."}
