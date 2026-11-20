"""Funciones de validación reutilizables.

Cada función recibe la clase de error a lanzar (``error``), así el mismo
validador sirve para clientes, servicios o reservas sin repetir código.
Todas devuelven el valor ya normalizado (sin espacios sobrantes, etc.).
"""

import math
import re

from .excepciones import ValidacionError

_PATRON_CORREO = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
)
_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]+$")
_PATRON_TELEFONO = re.compile(r"^\d{7,10}$")


def validar_texto(valor, campo, minimo=3, maximo=60, error=ValidacionError):
    """Texto obligatorio, con espacios normalizados y longitud controlada."""
    if valor is None:
        raise error(f"El campo '{campo}' es obligatorio")
    if not isinstance(valor, str):
        raise error(f"El campo '{campo}' debe ser texto, no {type(valor).__name__}")
    limpio = " ".join(valor.split())
    if not minimo <= len(limpio) <= maximo:
        raise error(f"El campo '{campo}' debe tener entre {minimo} y {maximo} caracteres")
    return limpio


def validar_nombre_persona(valor, campo="nombre", error=ValidacionError):
    """Nombre de persona: solo letras, espacios, apóstrofes, puntos y guiones."""
    limpio = validar_texto(valor, campo, minimo=3, maximo=60, error=error)
    if not _PATRON_NOMBRE.match(limpio):
        raise error(f"El campo '{campo}' solo admite letras y espacios")
    return limpio


def validar_correo(valor, error=ValidacionError):
    """Correo con formato usuario@dominio.ext, normalizado a minúsculas."""
    limpio = validar_texto(valor, "correo", minimo=6, maximo=80, error=error).lower()
    if not _PATRON_CORREO.match(limpio):
        raise error(f"El correo '{limpio}' no tiene un formato válido")
    return limpio


def validar_telefono(valor, error=ValidacionError):
    """Teléfono de 7 a 10 dígitos (acepta texto o número; ignora espacios)."""
    if valor is None:
        raise error("El campo 'teléfono' es obligatorio")
    limpio = str(valor).strip().replace(" ", "")
    if not _PATRON_TELEFONO.match(limpio):
        raise error("El teléfono debe tener entre 7 y 10 dígitos numéricos")
    return limpio


def validar_numero(valor, campo, minimo=None, maximo=None,
                   minimo_inclusivo=True, entero=False, error=ValidacionError):
    """Número finito dentro de un rango; rechaza bool, texto, NaN e infinito."""
    if valor is None:
        raise error(f"El campo '{campo}' es obligatorio")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise error(f"El campo '{campo}' debe ser numérico, no {type(valor).__name__}")
    if not math.isfinite(valor):
        raise error(f"El campo '{campo}' no es un número finito")
    if entero and int(valor) != valor:
        raise error(f"El campo '{campo}' debe ser un entero")
    if minimo is not None:
        if valor < minimo or (not minimo_inclusivo and valor == minimo):
            simbolo = ">=" if minimo_inclusivo else ">"
            raise error(f"El campo '{campo}' debe ser {simbolo} {minimo}")
    if maximo is not None and valor > maximo:
        raise error(f"El campo '{campo}' debe ser <= {maximo}")
    return int(valor) if entero else valor
