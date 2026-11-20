"""Jerarquía de excepciones personalizadas de Software FJ.

Todas heredan de ``ErrorSistema``, de modo que el programa principal puede
capturar cualquier error propio con un solo ``except ErrorSistema`` y, aun así,
distinguir cada caso por su tipo o por su ``codigo_error``.

Jerarquía:
    ErrorSistema
    ├── ValidacionError
    │   ├── ClienteError
    │   └── ParametroFaltanteError
    ├── ServicioError
    │   └── ServicioNoDisponible
    ├── ReservaError
    │   └── OperacionNoPermitida
    ├── CalculoError
    ├── RegistroDuplicado
    └── RegistroNoEncontrado
"""


class ErrorSistema(Exception):
    """Excepción base del sistema. Cada subclase define un código de error."""

    codigo_error = "FJ-000"

    def __str__(self):
        return f"[{self.codigo_error}] {super().__str__()}"


class ValidacionError(ErrorSistema):
    """Un dato no cumple las reglas de validación."""
    codigo_error = "FJ-100"


class ClienteError(ValidacionError):
    """Dato inválido en un cliente."""
    codigo_error = "FJ-110"


class ParametroFaltanteError(ValidacionError):
    """Falta un parámetro obligatorio."""
    codigo_error = "FJ-120"


class ServicioError(ErrorSistema):
    """Servicio mal configurado o con parámetros inválidos."""
    codigo_error = "FJ-200"


class ServicioNoDisponible(ServicioError):
    """El servicio existe pero no se puede usar en este momento."""
    codigo_error = "FJ-210"


class ReservaError(ErrorSistema):
    """Error al crear o gestionar una reserva."""
    codigo_error = "FJ-300"


class OperacionNoPermitida(ReservaError):
    """La operación no es válida para el estado actual de la reserva."""
    codigo_error = "FJ-310"


class CalculoError(ErrorSistema):
    """Cálculo de costos inconsistente (impuesto, descuento, resultado)."""
    codigo_error = "FJ-400"


class RegistroDuplicado(ErrorSistema):
    """Se intentó registrar una entidad con un código/correo ya existente."""
    codigo_error = "FJ-500"


class RegistroNoEncontrado(ErrorSistema):
    """Se buscó una entidad que no existe en el sistema."""
    codigo_error = "FJ-510"
