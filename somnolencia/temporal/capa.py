"""
La capa temporal completa en un solo objeto.

Junta los tres actualizadores de estado, el rastreador de eventos, PERCLOS
y las alertas. El ciclo principal solo tiene que llamar a actualizar() una
vez por cuadro con las tres mediciones.
"""

from somnolencia.temporal.estados import (
    crear_actualizador_ojos, crear_actualizador_boca, crear_actualizador_cabeza,
)
from somnolencia.temporal.eventos import RastreadorDeEventos
from somnolencia.temporal.perclos import calcular_perclos
from somnolencia.temporal.alertas import nivel_de_alerta


class CapaTemporal:

    def __init__(self):
        self.actualizador_ojos = crear_actualizador_ojos()
        self.actualizador_boca = crear_actualizador_boca()
        self.actualizador_cabeza = crear_actualizador_cabeza()
        self.rastreador = RastreadorDeEventos()
        self.t_inicio = None    # marca de tiempo del primer cuadro

    def actualizar(self, t, medicion_ojos, medicion_boca, medicion_cabeza):
        """
        Recibe el tiempo y las tres mediciones de un cuadro.
        Entrega un diccionario con todo lo que la interfaz necesita mostrar.
        """
        if self.t_inicio is None:
            self.t_inicio = t

        # 1. De mediciones a estados.
        estado_ojos = self.actualizador_ojos.actualizar(medicion_ojos)
        estado_boca = self.actualizador_boca.actualizar(medicion_boca)
        estado_cabeza = self.actualizador_cabeza.actualizar(medicion_cabeza)

        # 2. De estados a eventos.
        eventos_nuevos = self.rastreador.actualizar(
            t, estado_ojos, estado_boca, estado_cabeza)

        # 3. PERCLOS sobre los últimos 30 s.
        valor_perclos, nivel_perclos = calcular_perclos(
            t, self.t_inicio,
            self.rastreador.cierres_para_perclos(t),
            self.rastreador.huecos_para_perclos(t))

        # 4. Alerta, con lo que está en curso en este momento.
        cierre_s = self.rastreador.cierre_en_curso(t)
        distraccion_s = self.rastreador.distraccion_en_curso(t)
        alerta, motivo = nivel_de_alerta(cierre_s, distraccion_s, nivel_perclos)

        return {
            "t": t,
            "estado_ojos": estado_ojos,
            "estado_boca": estado_boca,
            "estado_cabeza": estado_cabeza,
            "eventos_nuevos": eventos_nuevos,
            "contadores": dict(self.rastreador.contadores),
            "cierre_en_curso_s": cierre_s,
            "bostezo_en_curso_s": self.rastreador.bostezo_en_curso(t),
            "distraccion_en_curso_s": distraccion_s,
            "perclos": valor_perclos,
            "nivel_perclos": nivel_perclos,
            "alerta": alerta,
            "motivo_alerta": motivo,
        }

    def terminar(self, t):
        """Al acabarse el video: cierra lo que quedó abierto y entrega esos eventos."""
        return self.rastreador.cerrar_todo(t)
