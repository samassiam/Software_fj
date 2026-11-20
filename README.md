# Software_fj
Software FJ: aplicación en Python con programación orientada a objetos para gestionar clientes, servicios y reservas, con manejo de excepciones y registro de logs (UNAD, Programación 213023)

# Software FJ – Sistema integral de gestión de clientes, servicios y reservas

Programación (213023) – UNAD – Fase 4  
Integrantes: _(Samuel Samit Assia Mercado, Keiner David Méndez de la Rosa, Melany Torres Torres)_

Sistema orientado a objetos en Python, **sin base de datos**: toda la información
vive en objetos y listas en memoria; el único archivo que se escribe es el de logs.

## Ejecución

```bash
python main.py
```

Requiere Python 3.8 o superior y no usa librerías externas. Los eventos y errores
se guardan en `logs/software_fj.log`.

## Estructura

```
main.py                    Simulación de 27 operaciones (válidas e inválidas)
software_fj/
├── excepciones.py         Jerarquía de excepciones personalizadas con códigos FJ-xxx
├── registro.py            Configuración del logging (archivo rotativo)
├── validaciones.py        Validadores reutilizables (texto, correo, teléfono, números)
├── entidades.py           Clase abstracta Entidad
├── cliente.py             Cliente (encapsulación + propiedades con validación)
├── servicios.py           Servicio (abstracta) + SalaReuniones, AlquilerEquipo, Asesoria
├── reserva.py             Reserva con máquina de estados
└── gestor.py              GestorFJ: listas internas, unicidad y fábrica de servicios
```

## Cumplimiento de los requisitos

| Requisito del enunciado | Dónde está |
|---|---|
| Clase abstracta de entidades generales | `Entidad` (`entidades.py`) |
| Cliente con validaciones y encapsulación | `Cliente` (`cliente.py`) |
| Servicio abstracto + 3 servicios con polimorfismo | `Servicio`, `SalaReuniones`, `AlquilerEquipo`, `Asesoria` (`servicios.py`) |
| Reserva (cliente, servicio, duración, estado; confirmar, cancelar, procesar) | `Reserva` (`reserva.py`) |
| Métodos sobrecargados | `Servicio.calcular_total` (varias firmas) y `_resolver_descuento` (`singledispatchmethod`) |
| Excepciones personalizadas | `excepciones.py` |
| `try/except`, `try/except/else`, `try/except/finally` | `Reserva.confirmar`, `Simulador.ejecutar` |
| Encadenamiento de excepciones (`raise ... from`) | `Reserva.__init__`, `Reserva.procesar`, `GestorFJ.crear_servicio` |
| Archivo de logs | `registro.py` → `logs/software_fj.log` |
| Mínimo 10 operaciones con éxitos y fallos | `main.py` (27 operaciones) |
| Sin base de datos | Listas internas en `GestorFJ` |

## Cálculo de costos (sobrecarga)

```python
servicio.calcular_total(2)                  # IVA por defecto (19 %), sin descuento
servicio.calcular_total(2, 0.05)            # IVA personalizado
servicio.calcular_total(2, 0.19, 0.10)      # descuento porcentual
servicio.calcular_total(2, 0.19, "FJ20")    # descuento por cupón
```

## Cómo extender el sistema

Para agregar un nuevo servicio basta con crear una subclase de `Servicio`,
implementar `calcular_costo`, `validar_horas` y `describir`, y registrarla:

```python
gestor.registrar_tipo_servicio("catering", Catering)
```
