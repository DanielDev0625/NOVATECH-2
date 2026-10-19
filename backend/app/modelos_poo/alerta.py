# · Clase que representa una alerta del sistema.
class Alerta:
    def __init__(self, tipo: str, mensaje: str):
        self.tipo = tipo
        self.mensaje = mensaje

    def a_dict(self) -> dict:
        # · Formato que espera el frontend.
        return {"tipo": self.tipo, "mensaje": self.mensaje}
