"""Servicio (clase abstracta) y servicios especializados.

Conceptos aplicados:
- Abstracción: ``Servicio`` define el contrato (métodos abstractos).
- Herencia/polimorfismo: cada hijo sobrescribe ``calcular_costo``,
  ``validar_horas`` y ``describir``.
- Patrón Template Method: ``calcular_total`` fija los pasos del cálculo y
  delega en los métodos que cada hijo sobrescribe.
- Sobrecarga: ``calcular_total`` admite varias firmas y el descuento se
  resuelve por TIPO de argumento (None, número o código de cupón) con
  ``functools.singledispatchmethod``.
"""

import math
from abc import abstractmethod
from functools import singledispatchmethod
from typing import overload

from .entidades import Entidad
from .excepciones import CalculoError, ServicioError
from .registro import obtener_logger
from .validaciones import validar_numero, validar_texto

LOG = obtener_logger("servicio")


class Servicio(Entidad):
    """Clase abstracta de la que heredan todos los servicios de Software FJ."""

    IMPUESTO_POR_DEFECTO = 0.19
    CUPONES = {"BIENVENIDO10": 0.10, "FJ20": 0.20}

    def __init__(self, codigo, nombre, precio_hora):
        super().__init__(codigo)
        self.__nombre = validar_texto(nombre, "nombre del servicio", error=ServicioError)
        self.__precio_hora = validar_numero(
            precio_hora, "precio por hora", minimo=0, minimo_inclusivo=False,
            error=ServicioError,
        )
        self.__disponible = True

    # ---------- propiedades (encapsulación) ----------
    @property
    def nombre(self):
        return self.__nombre

    @property
    def precio_hora(self):
        return self.__precio_hora

    @property
    def disponible(self):
        return self.__disponible

    def habilitar(self):
        self.__disponible = True
        LOG.info("Servicio %s habilitado", self.nombre)

    def deshabilitar(self, motivo="sin motivo"):
        self.__disponible = False
        LOG.warning("Servicio %s deshabilitado (%s)", self.nombre, motivo)

    # ---------- contrato abstracto ----------
    @abstractmethod
    def calcular_costo(self, horas):
        """Costo base (sin impuesto ni descuento) para ``horas`` de servicio."""

    @abstractmethod
    def validar_horas(self, horas):
        """Lanza ``ServicioError`` si la duración no es válida para este servicio."""

    @abstractmethod
    def describir(self):
        """Descripción del servicio."""

    def mostrar_info(self):
        estado = "disponible" if self.disponible else "NO disponible"
        return f"{self.describir()} [{estado}]"

    @staticmethod
    def _validar_rango_horas(horas, minimo, maximo, etiqueta):
        validar_numero(horas, "horas", minimo=minimo, maximo=maximo, error=ServicioError)

    # ---------- sobrecarga de cálculo de costos ----------
    @overload
    def calcular_total(self, horas: float) -> float: ...
    @overload
    def calcular_total(self, horas: float, impuesto: float) -> float: ...
    @overload
    def calcular_total(self, horas: float, impuesto: float, descuento) -> float: ...

    def calcular_total(self, horas, impuesto=None, descuento=None):
        """Total final = costo base - descuento + impuesto.

        Variantes de llamada:
            calcular_total(2)                    -> IVA por defecto, sin descuento
            calcular_total(2, 0.05)              -> IVA personalizado
            calcular_total(2, 0.19, 0.10)        -> descuento porcentual
            calcular_total(2, 0.19, "FJ20")      -> descuento por cupón
        """
        self.validar_horas(horas)
        tasa = self._resolver_impuesto(impuesto)
        desc = self._resolver_descuento(descuento)

        costo = self.calcular_costo(horas)
        if not math.isfinite(costo) or costo <= 0:
            raise CalculoError(f"El costo base calculado es inconsistente: {costo}")

        total = costo * (1 - desc) * (1 + tasa)
        if not 0 < total <= costo * (1 + tasa) + 1e-9:
            raise CalculoError(f"El total calculado es inconsistente: {total}")
        return round(total, 2)

    def _resolver_impuesto(self, impuesto):
        if impuesto is None:
            return self.IMPUESTO_POR_DEFECTO
        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) \
                or not 0 <= impuesto <= 1:
            raise CalculoError(f"Impuesto inválido: {impuesto!r} (debe estar entre 0 y 1)")
        return float(impuesto)

    @singledispatchmethod
    def _resolver_descuento(self, descuento):
        raise CalculoError(
            f"Tipo de descuento no soportado: {type(descuento).__name__}"
        )

    @_resolver_descuento.register(type(None))
    def _descuento_ninguno(self, descuento):
        return 0.0

    @_resolver_descuento.register(int)
    @_resolver_descuento.register(float)
    def _descuento_porcentual(self, descuento):
        if isinstance(descuento, bool) or not 0 <= descuento < 1:
            raise CalculoError(
                f"Descuento fuera de rango: {descuento!r} (debe estar entre 0 y 1)"
            )
        return float(descuento)

    @_resolver_descuento.register(str)
    def _descuento_cupon(self, descuento):
        codigo = descuento.strip().upper()
        if codigo not in self.CUPONES:
            raise CalculoError(f"Cupón inválido: '{descuento}'")
        return self.CUPONES[codigo]


class SalaReuniones(Servicio):
    """Reserva de salas: entre 1 y 12 horas, con capacidad máxima."""

    def __init__(self, codigo, nombre, precio_hora, capacidad):
        super().__init__(codigo, nombre, precio_hora)
        self.__capacidad = validar_numero(
            capacidad, "capacidad", minimo=1, maximo=200, entero=True, error=ServicioError
        )

    @property
    def capacidad(self):
        return self.__capacidad

    def calcular_costo(self, horas):
        return self.precio_hora * horas

    def validar_horas(self, horas):
        self._validar_rango_horas(horas, 1, 12, "las salas")

    def describir(self):
        return (f"Sala '{self.nombre}' para {self.capacidad} personas - "
                f"${self.precio_hora:,.0f}/hora")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos: hasta 72 horas; 10 % de descuento si supera 24 h."""

    HORAS_DESCUENTO = 24
    DESCUENTO_LARGA_DURACION = 0.10

    def __init__(self, codigo, nombre, precio_hora, tipo_equipo):
        super().__init__(codigo, nombre, precio_hora)
        self.__tipo_equipo = validar_texto(
            tipo_equipo, "tipo de equipo", minimo=3, maximo=40, error=ServicioError
        )

    @property
    def tipo_equipo(self):
        return self.__tipo_equipo

    def calcular_costo(self, horas):
        costo = self.precio_hora * horas
        if horas > self.HORAS_DESCUENTO:
            costo *= 1 - self.DESCUENTO_LARGA_DURACION
        return costo

    def validar_horas(self, horas):
        self._validar_rango_horas(horas, 1, 72, "los equipos")

    def describir(self):
        return (f"Equipo '{self.nombre}' ({self.tipo_equipo}) - "
                f"${self.precio_hora:,.0f}/hora")


class Asesoria(Servicio):
    """Asesoría especializada: entre 0.5 y 8 horas, con recargo del 50 %."""

    RECARGO = 1.5

    def __init__(self, codigo, nombre, precio_hora, especialidad):
        super().__init__(codigo, nombre, precio_hora)
        self.__especialidad = validar_texto(
            especialidad, "especialidad", minimo=3, maximo=40, error=ServicioError
        )

    @property
    def especialidad(self):
        return self.__especialidad

    def calcular_costo(self, horas):
        return self.precio_hora * horas * self.RECARGO

    def validar_horas(self, horas):
        self._validar_rango_horas(horas, 0.5, 8, "las asesorías")

    def describir(self):
        return (f"Asesoría '{self.nombre}' en {self.especialidad} - "
                f"${self.precio_hora:,.0f}/hora (+50 % por especialización)")
