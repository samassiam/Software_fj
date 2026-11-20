"""Clase Reserva: integra cliente, servicio, duración y estado.

El ciclo de vida se controla con una máquina de estados explícita
(``Enum`` + tabla de transiciones), por lo que cualquier operación fuera de
orden lanza ``OperacionNoPermitida`` en lugar de dejar la reserva inconsistente.

    PENDIENTE ──confirmar──> CONFIRMADA ──procesar──> PROCESADA
        │                        │
        └────────cancelar────────┴──────> CANCELADA
"""

from datetime import datetime
from enum import Enum

from .cliente import Cliente
from .entidades import Entidad
from .excepciones import (
    ErrorSistema,
    OperacionNoPermitida,
    ParametroFaltanteError,
    ReservaError,
    ServicioError,
    ServicioNoDisponible,
)
from .registro import obtener_logger
from .servicios import Servicio
from .validaciones import validar_numero

LOG = obtener_logger("reserva")


class EstadoReserva(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


_TRANSICIONES = {
    "confirmar": {EstadoReserva.PENDIENTE},
    "procesar": {EstadoReserva.CONFIRMADA},
    "cancelar": {EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA},
}


class Reserva(Entidad):
    def __init__(self, codigo, cliente, servicio, horas):
        super().__init__(codigo)
        if cliente is None or servicio is None:
            raise ParametroFaltanteError("La reserva requiere un cliente y un servicio")
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaError("Cliente o servicio con tipo inválido")
        try:
            validar_numero(horas, "horas", minimo=0, minimo_inclusivo=False,
                           error=ServicioError)
            servicio.validar_horas(horas)
        except ServicioError as causa:
            # Encadenamiento: el error original queda como __cause__
            raise ReservaError(
                f"No se pudo crear la reserva {codigo} para '{servicio.nombre}'"
            ) from causa
        if not servicio.disponible:
            raise ServicioNoDisponible(f"El servicio '{servicio.nombre}' no está disponible")

        self.__cliente = cliente
        self.__servicio = servicio
        self.__horas = horas
        self.__estado = EstadoReserva.PENDIENTE
        self.__total = 0.0
        self.__creada = datetime.now()
        LOG.info("Reserva %s creada (%s, %s, %s h)", codigo, cliente.nombre,
                 servicio.nombre, horas)

    # ---------- propiedades ----------
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def horas(self):
        return self.__horas

    @property
    def estado(self):
        return self.__estado

    @property
    def total(self):
        return self.__total

    # ---------- control de estados ----------
    def _exigir_estado(self, operacion):
        if self.__estado not in _TRANSICIONES[operacion]:
            permitidos = ", ".join(e.value for e in _TRANSICIONES[operacion])
            raise OperacionNoPermitida(
                f"No se puede {operacion} la reserva {self.codigo} en estado "
                f"'{self.__estado.value}' (requiere: {permitidos})"
            )

    # ---------- operaciones ----------
    def confirmar(self):
        """Confirma la reserva. Demuestra try/except/else/finally."""
        try:
            self._exigir_estado("confirmar")
            if not self.__servicio.disponible:
                raise ServicioNoDisponible(
                    f"El servicio '{self.__servicio.nombre}' no está disponible"
                )
        except ServicioNoDisponible as causa:
            raise ReservaError(f"No se pudo confirmar la reserva {self.codigo}") from causa
        else:  # solo se ejecuta si no hubo ninguna excepción
            self.__estado = EstadoReserva.CONFIRMADA
            LOG.info("Reserva %s confirmada", self.codigo)
        finally:  # se ejecuta siempre, haya o no error
            LOG.debug("Fin del intento de confirmar la reserva %s", self.codigo)

    def cancelar(self, motivo="sin motivo"):
        self._exigir_estado("cancelar")
        self.__estado = EstadoReserva.CANCELADA
        LOG.info("Reserva %s cancelada (%s)", self.codigo, motivo)

    def procesar(self, impuesto=None, descuento=None):
        """Calcula el total y cierra la reserva (admite las variantes de costo)."""
        self._exigir_estado("procesar")
        try:
            total = self.__servicio.calcular_total(self.__horas, impuesto, descuento)
        except ErrorSistema as causa:
            raise ReservaError(f"Error al procesar la reserva {self.codigo}") from causa
        self.__total = total
        self.__estado = EstadoReserva.PROCESADA
        LOG.info("Reserva %s procesada. Total: $%s", self.codigo, f"{total:,.2f}")
        return total

    def mostrar_info(self):
        return (f"Reserva {self.codigo} [{self.__estado.value}] "
                f"{self.__cliente.nombre} -> {self.__servicio.nombre} "
                f"({self.__horas} h) | Total: ${self.__total:,.2f}")
