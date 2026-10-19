# · Clase que encapsula todo lo relacionado con el hash y la verificación de contraseñas.
import hashlib
import hmac
import secrets
from typing import Optional


class HasherContrasena:
    # · Veces que se repite PBKDF2 al generar un hash nuevo.
    ITERACIONES = 200_000

    def generar(self, clave: str, salt: Optional[str] = None) -> str:
        # · Hash nuevo con el formato propio de la app: "salt$hash" (PBKDF2-SHA256).
        salt = salt or secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac("sha256", clave.encode(), salt.encode(), self.ITERACIONES).hex()
        return f"{salt}${h}"

    def verificar(self, clave: str, guardado: str) -> bool:
        # · Acepta tres formatos guardados en la tabla usuarios:
        # ·   salt$hash                       (formato propio)
        # ·   scrypt:N:r:p$salt$hash          (werkzeug, versión Flask anterior)
        # ·   pbkdf2:sha256:iter$salt$hash    (werkzeug)
        # · Si el formato es desconocido devuelve False en vez de romper con un error 500.
        if not guardado:
            return False
        try:
            partes = guardado.split("$")
            if len(partes) == 2:
                return self._verificar_propio(clave, partes)
            if len(partes) == 3:
                return self._verificar_werkzeug(clave, partes)
        except (ValueError, IndexError, TypeError):
            return False
        return False

    def _verificar_propio(self, clave: str, partes: list) -> bool:
        # · Recalcula el hash con la misma sal y lo compara en tiempo constante.
        salt, h = partes
        return hmac.compare_digest(self.generar(clave, salt).split("$")[1], h)

    def _verificar_werkzeug(self, clave: str, partes: list) -> bool:
        # · Reproduce el cálculo de werkzeug según el método indicado en el primer bloque.
        metodo, salt, h = partes
        esquema = metodo.split(":")
        if esquema[0] == "scrypt":
            n, r, p = (int(x) for x in esquema[1:4])
            calculado = hashlib.scrypt(clave.encode(), salt=salt.encode(), n=n, r=r, p=p,
                                       maxmem=132 * n * r * p).hex()
        elif esquema[0] == "pbkdf2":
            calculado = hashlib.pbkdf2_hmac(esquema[1], clave.encode(), salt.encode(),
                                            int(esquema[2])).hex()
        else:
            return False
        return hmac.compare_digest(calculado, h)
