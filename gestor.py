"""GestorFJ: administra las listas internas de clientes, servicios y reservas.

Reglas que aplica (y que antes no existían):
- Códigos únicos en cada lista y correo único por cliente.
- Búsquedas que lanzan ``RegistroNoEncontrado`` en vez de devolver None.
- Fábrica de servicios extensible: para agregar un tipo nuevo basta con
  llamar a ``registrar_tipo_servicio`` (principio abierto/cerrado).
"""

from .cliente import Cliente
from .excepciones import (
    ParametroFaltanteError,
    RegistroDuplicado,
    RegistroNoEncontrado,
    ServicioError,
)
from .registro import obtener_logger
from .reserva import Reserva
from .servicios import Asesoria, AlquilerEquipo, SalaReuniones

LOG = obtener_logger("gestor")


class GestorFJ:
    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        self.__tipos_servicio = {
            "sala": SalaReuniones,
            "equipo": AlquilerEquipo,
            "asesoria": Asesoria,
        }

    # ---------- consultas (copias: la lista interna no se expone) ----------
    @property
    def clientes(self):
        return list(self.__clientes)

    @property
    def servicios(self):
        return list(self.__servicios)

    @property
    def reservas(self):
        return list(self.__reservas)

    @staticmethod
    def _buscar(lista, codigo, nombre):
        for item in lista:
            if item.codigo == codigo:
                return item
        raise RegistroNoEncontrado(f"No existe {nombre} con código {codigo}")

    def buscar_cliente(self, codigo):
        return self._buscar(self.__clientes, codigo, "un cliente")

    def buscar_servicio(self, codigo):
        return self._buscar(self.__servicios, codigo, "un servicio")

    def buscar_reserva(self, codigo):
        return self._buscar(self.__reservas, codigo, "una reserva")

    # ---------- clientes ----------
    def registrar_cliente(self, codigo, nombre, correo, telefono):
        cliente = Cliente(codigo, nombre, correo, telefono)
        if cliente in self.__clientes:
            raise RegistroDuplicado(f"Ya existe un cliente con código {codigo}")
        if any(c.correo == cliente.correo for c in self.__clientes):
            raise RegistroDuplicado(f"El correo {cliente.correo} ya está registrado")
        self.__clientes.append(cliente)
        LOG.info("Cliente %s registrado: %s", codigo, cliente.nombre)
        return cliente

    # ---------- servicios ----------
    def registrar_tipo_servicio(self, clave, clase):
        """Permite extender el sistema con nuevos tipos de servicio."""
        self.__tipos_servicio[clave] = clase

    def crear_servicio(self, tipo, **datos):
        clase = self.__tipos_servicio.get(tipo)
        if clase is None:
            raise ServicioError(
                f"Tipo de servicio desconocido: '{tipo}' "
                f"(disponibles: {', '.join(self.__tipos_servicio)})"
            )
        try:
            servicio = clase(**datos)
        except TypeError as causa:  # faltan o sobran argumentos
            raise ParametroFaltanteError(
                f"Parámetros incorrectos para el servicio '{tipo}'"
            ) from causa
        if servicio in self.__servicios:
            raise RegistroDuplicado(f"Ya existe un servicio con código {servicio.codigo}")
        self.__servicios.append(servicio)
        LOG.info("Servicio %s creado: %s", servicio.codigo, servicio.nombre)
        return servicio

    # ---------- reservas ----------
    def crear_reserva(self, codigo, codigo_cliente, codigo_servicio, horas):
        cliente = self.buscar_cliente(codigo_cliente)
        servicio = self.buscar_servicio(codigo_servicio)
        reserva = Reserva(codigo, cliente, servicio, horas)
        if reserva in self.__reservas:
            raise RegistroDuplicado(f"Ya existe una reserva con código {codigo}")
        self.__reservas.append(reserva)
        return reserva

    # ---------- reportes ----------
    def resumen(self):
        lineas = ["--- Clientes ---"]
        lineas += [str(c) for c in self.__clientes]
        lineas.append("--- Servicios ---")
        lineas += [str(s) for s in self.__servicios]
        lineas.append("--- Reservas ---")
        lineas += [str(r) for r in self.__reservas]
        return lineas
