"""Clase abstracta que representa las entidades generales del sistema."""

from abc import ABC, abstractmethod

from .validaciones import validar_numero


class Entidad(ABC):
    """Base de Cliente, Servicio y Reserva.

    Centraliza la validación del código y define el contrato común
    (``mostrar_info``). Dos entidades son iguales si son del mismo tipo y
    tienen el mismo código.
    """

    def __init__(self, codigo):
        self._codigo = validar_numero(codigo, "código", minimo=1, entero=True)

    @property
    def codigo(self):
        return self._codigo

    @abstractmethod
    def mostrar_info(self):
        """Devuelve una descripción legible de la entidad."""

    def __str__(self):
        return self.mostrar_info()

    def __repr__(self):
        return f"{type(self).__name__}(codigo={self._codigo})"

    def __eq__(self, otro):
        return type(self) is type(otro) and self._codigo == otro._codigo

    def __hash__(self):
        return hash((type(self).__name__, self._codigo))
