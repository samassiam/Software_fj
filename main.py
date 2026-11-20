"""Software FJ - Simulación de operaciones (Programación 213023, UNAD).

Ejecuta más de 10 operaciones, válidas e inválidas, y demuestra que la
aplicación sigue funcionando ante cualquier error. Todo queda registrado en
logs/software_fj.log.

Uso:  python main.py
"""

from software_fj import (
    ErrorSistema,
    GestorFJ,
    Servicio,
)
from software_fj.registro import RUTA_LOG, obtener_logger

LOG = obtener_logger("main")


def cadena_de_errores(error):
    """Convierte un error y sus causas encadenadas en una sola línea legible."""
    partes = []
    while error is not None:
        partes.append(f"{type(error).__name__}: {error}")
        error = error.__cause__
    return "  <-causado por-  ".join(partes)


class Simulador:
    """Ejecuta operaciones de forma segura y lleva el conteo de resultados."""

    def __init__(self):
        self.numero = 0
        self.exitosas = 0
        self.fallidas = 0

    def ejecutar(self, descripcion, operacion):
        """Corre ``operacion``; si falla, registra el error y el programa continúa."""
        self.numero += 1
        etiqueta = f"Op {self.numero:02d} - {descripcion}"
        try:
            resultado = operacion()
        except ErrorSistema as error:
            self.fallidas += 1
            detalle = cadena_de_errores(error)
            LOG.error("%s | %s", etiqueta, detalle)
            print(f"  [ERROR CONTROLADO] {etiqueta}\n      {detalle}")
            return None
        except Exception as error:  # error imprevisto: igual se registra y se sigue
            self.fallidas += 1
            LOG.critical("%s | error inesperado: %r", etiqueta, error, exc_info=True)
            print(f"  [ERROR INESPERADO] {etiqueta}\n      {type(error).__name__}: {error}")
            return None
        else:
            self.exitosas += 1
            LOG.info("%s | OK", etiqueta)
            print(f"  [OK] {etiqueta}")
            return resultado
        finally:
            LOG.debug("Finalizó %s", etiqueta)


def main():
    LOG.info("=" * 20 + " Inicio de la simulación " + "=" * 20)
    gestor = GestorFJ()
    sim = Simulador()

    print("\n=== CLIENTES ===")
    sim.ejecutar("Registrar cliente Ana Gómez",
                 lambda: gestor.registrar_cliente(1, "Ana Gómez", "ana@correo.com", "3001234567"))
    sim.ejecutar("Registrar cliente Luis Pérez",
                 lambda: gestor.registrar_cliente(2, "Luis Pérez", "luis@correo.com", 3109876543))
    sim.ejecutar("Cliente con correo inválido",
                 lambda: gestor.registrar_cliente(3, "Pedro Ruiz", "pedro@correo", "3001112233"))
    sim.ejecutar("Cliente con nombre vacío",
                 lambda: gestor.registrar_cliente(4, "", "vacio@correo.com", "3001112233"))
    sim.ejecutar("Cliente con correo duplicado",
                 lambda: gestor.registrar_cliente(5, "Ana Copia", "ANA@correo.com", "3005556677"))

    print("\n=== SERVICIOS ===")
    sim.ejecutar("Crear sala de reuniones",
                 lambda: gestor.crear_servicio("sala", codigo=1, nombre="Sala A",
                                               precio_hora=50000, capacidad=12))
    sim.ejecutar("Crear alquiler de equipo",
                 lambda: gestor.crear_servicio("equipo", codigo=2, nombre="Portátil Pro",
                                               precio_hora=8000, tipo_equipo="Computador"))
    sim.ejecutar("Crear asesoría de Python",
                 lambda: gestor.crear_servicio("asesoria", codigo=3, nombre="Asesoría Python",
                                               precio_hora=70000, especialidad="Python"))
    sim.ejecutar("Servicio con precio negativo",
                 lambda: gestor.crear_servicio("sala", codigo=4, nombre="Sala B",
                                               precio_hora=-100, capacidad=5))
    sim.ejecutar("Servicio con parámetros faltantes",
                 lambda: gestor.crear_servicio("equipo", codigo=5, nombre="Proyector"))
    sim.ejecutar("Tipo de servicio inexistente",
                 lambda: gestor.crear_servicio("catering", codigo=6, nombre="Café"))
    sim.ejecutar("Instanciar la clase abstracta Servicio",
                 lambda: Servicio(7, "Genérico", 1000))

    print("\n=== RESERVAS ===")
    r1 = sim.ejecutar("Reserva de sala por 3 horas", lambda: gestor.crear_reserva(1, 1, 1, 3))
    r2 = sim.ejecutar("Reserva de equipo por 30 horas", lambda: gestor.crear_reserva(2, 2, 2, 30))
    r3 = sim.ejecutar("Reserva de asesoría por 2 horas", lambda: gestor.crear_reserva(3, 2, 3, 2))
    sim.ejecutar("Reserva de asesoría por 20 horas (excede el máximo)",
                 lambda: gestor.crear_reserva(4, 1, 3, 20))
    sim.ejecutar("Reserva con cliente inexistente", lambda: gestor.crear_reserva(5, 99, 1, 2))

    print("\n=== CONFIRMAR, PROCESAR Y CANCELAR ===")
    if r1:
        sim.ejecutar("Confirmar reserva 1", r1.confirmar)
        sim.ejecutar("Procesar reserva 1 (IVA por defecto)", r1.procesar)
        sim.ejecutar("Cancelar reserva 1 ya procesada", r1.cancelar)
    if r2:
        sim.ejecutar("Confirmar reserva 2", r2.confirmar)
        sim.ejecutar("Procesar reserva 2 con descuento de 150 %", lambda: r2.procesar(0.19, 1.5))
        sim.ejecutar("Procesar reserva 2 con cupón inválido", lambda: r2.procesar(0.19, "REGALO"))
        sim.ejecutar("Procesar reserva 2 con IVA 5 % y cupón FJ20",
                     lambda: r2.procesar(0.05, "FJ20"))
    if r3:
        gestor.buscar_servicio(3).deshabilitar("mantenimiento")
        sim.ejecutar("Confirmar reserva 3 con servicio no disponible", r3.confirmar)
        sim.ejecutar("Cancelar reserva 3", lambda: r3.cancelar("servicio no disponible"))
        sim.ejecutar("Cancelar reserva 3 otra vez", r3.cancelar)

    print("\n=== RESUMEN FINAL ===")
    for linea in gestor.resumen():
        print(linea)
    print(f"\nOperaciones: {sim.numero} | Exitosas: {sim.exitosas} | "
          f"Errores controlados: {sim.fallidas}")
    print(f"Log completo en: {RUTA_LOG}")
    LOG.info("Simulación terminada: %d operaciones (%d OK, %d con error)",
             sim.numero, sim.exitosas, sim.fallidas)


if __name__ == "__main__":
    main()
