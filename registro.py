"""Configuración centralizada del archivo de logs.

- Escribe en ``logs/software_fj.log`` (se crea la carpeta si no existe).
- Usa ``RotatingFileHandler`` para que el archivo no crezca sin límite.
- Cada módulo obtiene su propio logger hijo con ``obtener_logger("nombre")``,
  así el log indica de qué módulo viene cada mensaje.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

RUTA_LOG = Path(__file__).resolve().parent.parent / "logs" / "software_fj.log"
_NOMBRE_RAIZ = "software_fj"


def _configurar():
    raiz = logging.getLogger(_NOMBRE_RAIZ)
    if raiz.handlers:  # ya configurado: evita mensajes duplicados
        return
    raiz.setLevel(logging.DEBUG)
    raiz.propagate = False
    RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)
    manejador = RotatingFileHandler(
        RUTA_LOG, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    manejador.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s")
    )
    raiz.addHandler(manejador)


def obtener_logger(modulo):
    """Devuelve el logger del módulo indicado (p. ej. ``software_fj.reserva``)."""
    _configurar()
    return logging.getLogger(f"{_NOMBRE_RAIZ}.{modulo}")
