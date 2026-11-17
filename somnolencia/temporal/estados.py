"""
De una medición a un estado.

Cada señal (ojos, boca, cabeza) tiene un estado de reposo y un estado activo:

    señal    reposo     activo
    ojos     ABIERTO    CERRADO
    boca     CERRADA    ABIERTA
    cabeza   ATENTO     DISTRAIDO

El estado activo es el que abre un evento (un cierre de ojos, un bostezo,
una distracción).

Para decidir el estado se usa un umbral doble. Hay un umbral para entrar al
estado activo y otro distinto para salir. Si la medición queda entre los
dos, el estado no cambia. Así una medición que oscila cerca del límite no
produce cambios de estado falsos.
"""

from somnolencia import config
from somnolencia.tipos import (
    ABIERTO, CERRADO, CERRADA, ABIERTA, ATENTO, DISTRAIDO, SIN_DATO,
)


class ActualizadorDeEstado:
    """Convierte las mediciones de una señal en su estado, cuadro por cuadro."""

    def __init__(self, estado_reposo, estado_activo,
                 umbral_entrada, umbral_salida, activo_si_baja):
        # Nombres de los dos estados de esta señal.
        self.estado_reposo = estado_reposo
        self.estado_activo = estado_activo
        # Umbral para entrar al estado activo y umbral para salir de él.
        self.umbral_entrada = umbral_entrada
        self.umbral_salida = umbral_salida
        # True si el estado activo ocurre cuando el valor BAJA (ojos, cabeza).
        # False si ocurre cuando el valor SUBE (boca).
        self.activo_si_baja = activo_si_baja
        # Último estado conocido. Se empieza en reposo.
        self.estado = estado_reposo

    def actualizar(self, medicion):
        """Recibe una Medicion y entrega el estado de la señal en ese cuadro."""
        # Sin dato válido no se decide nada. Se conserva el último estado
        # conocido para cuando el dato regrese, pero se reporta SIN_DATO.
        if not medicion.valido:
            return SIN_DATO

        valor = medicion.valor

        if self.estado == self.estado_reposo:
            # Estando en reposo, solo se revisa el umbral de entrada.
            if self.activo_si_baja:
                entra = valor < self.umbral_entrada
            else:
                entra = valor > self.umbral_entrada
            if entra:
                self.estado = self.estado_activo
        else:
            # Estando activo, solo se revisa el umbral de salida.
            if self.activo_si_baja:
                sale = valor > self.umbral_salida
            else:
                sale = valor < self.umbral_salida
            if sale:
                self.estado = self.estado_reposo

        return self.estado


def crear_actualizador_ojos():
    """Ojos: CERRADO al bajar de 0.20, ABIERTO de nuevo al subir de 0.35."""
    return ActualizadorDeEstado(
        estado_reposo=ABIERTO, estado_activo=CERRADO,
        umbral_entrada=config.OJOS_UMBRAL_CIERRE,
        umbral_salida=config.OJOS_UMBRAL_REAPERTURA,
        activo_si_baja=True,
    )


def crear_actualizador_boca():
    """Boca: ABIERTA al subir de 0.20, CERRADA de nuevo al bajar de 0.14."""
    return ActualizadorDeEstado(
        estado_reposo=CERRADA, estado_activo=ABIERTA,
        umbral_entrada=config.BOCA_UMBRAL_APERTURA,
        umbral_salida=config.BOCA_UMBRAL_CIERRE,
        activo_si_baja=False,
    )


def crear_actualizador_cabeza():
    """Cabeza: DISTRAIDO al bajar de 0.50, ATENTO de nuevo al subir de 0.60."""
    return ActualizadorDeEstado(
        estado_reposo=ATENTO, estado_activo=DISTRAIDO,
        umbral_entrada=config.CABEZA_UMBRAL_DISTRAIDO,
        umbral_salida=config.CABEZA_UMBRAL_ATENTO,
        activo_si_baja=True,
    )
