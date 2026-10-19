# · Clase que calcula la huella de carbono a partir de energía consumida y km recorridos.
class HuellaCarbono:
    NOTA = "Estimación con factores de emisión de referencia configurables en .env."

    def __init__(self, factor_kwh: float, factor_km: float):
        # · kg de CO2 por cada kWh y por cada km.
        self.factor_kwh = factor_kwh
        self.factor_km = factor_km

    def calcular(self, kwh: float, km: float) -> dict:
        energia = kwh * self.factor_kwh
        transporte = km * self.factor_km
        return {"kwh_total": round(kwh, 1), "km_total": round(km, 1),
                "co2_energia_kg": round(energia, 1), "co2_transporte_kg": round(transporte, 1),
                "co2_total_kg": round(energia + transporte, 1), "nota": self.NOTA}
