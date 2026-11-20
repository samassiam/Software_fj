"""Clase Cliente con encapsulación y validación estricta."""

from .entidades import Entidad
from .excepciones import ClienteError
from .registro import obtener_logger
from .validaciones import (
    validar_correo,
    validar_nombre_persona,
    validar_telefono,
)

LOG = obtener_logger("cliente")


class Cliente(Entidad):
    """Cliente de Software FJ.

    Los datos personales son privados (name mangling) y solo se leen/modifican
    mediante propiedades; cada setter vuelve a validar, de modo que el objeto
    nunca queda en un estado inválido, ni al crearse ni al editarse.
    """

    def __init__(self, codigo, nombre, correo, telefono):
        super().__init__(codigo)
        self.__nombre = None
        self.__correo = None
        self.__telefono = None
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        LOG.debug("Cliente %s creado", self.codigo)

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = validar_nombre_persona(valor, "nombre", error=ClienteError)

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        self.__correo = validar_correo(valor, error=ClienteError)

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        self.__telefono = validar_telefono(valor, error=ClienteError)

    def mostrar_info(self):
        return f"Cliente {self.codigo}: {self.nombre} | {self.correo} | Tel. {self.telefono}"
