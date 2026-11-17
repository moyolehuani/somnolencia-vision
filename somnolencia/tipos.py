"""
Estructuras que comparten los módulos.

Los módulos de percepción (ojos, boca, cabeza) entregan una Medicion.
La capa temporal convierte mediciones en estados y los estados en eventos.
"""

from dataclasses import dataclass

# Nombres de los estados de cada señal.
ABIERTO = "ABIERTO"        # ojos
CERRADO = "CERRADO"        # ojos
CERRADA = "CERRADA"        # boca
ABIERTA = "ABIERTA"        # boca
ATENTO = "ATENTO"          # cabeza
DISTRAIDO = "DISTRAIDO"    # cabeza
SIN_DATO = "SIN_DATO"      # no se pudo medir en este cuadro

# Tipos de evento.
PARPADEO = "parpadeo"
BOSTEZO = "bostezo"
DISTRACCION = "distraccion"


@dataclass
class Medicion:
    """Lo que entrega un módulo de percepción en un cuadro."""
    t: float        # marca de tiempo en segundos
    valor: float    # entre 0 y 1
    valido: bool    # False si no se pudo medir en este cuadro


@dataclass
class Evento:
    """Un evento ya terminado y clasificado."""
    tipo: str         # PARPADEO, BOSTEZO o DISTRACCION
    inicio: float     # segundos
    fin: float        # segundos
    duracion: float   # fin - inicio, redondeada a milésimas
    categoria: str    # "normal", "lento", "microsueno", "bostezo" o la banda ("0.5", "1.0", ...)
