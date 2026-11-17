"""
De estados a eventos.

Un evento es un tramo de tiempo en que una señal estuvo en su estado activo:
un cierre de ojos, la boca abierta o la cabeza girada. Este módulo decide
cuándo empieza y termina cada evento, cuánto duró y a qué categoría
pertenece.

Las duraciones se calculan con las marcas de tiempo de los cuadros, nunca
contando cuadros, porque la cámara no entrega los cuadros a intervalos
exactos.

Hay dos clases:

  SeguidorDeEvento     sigue una sola señal y dice cuándo se cierra un evento.
  RastreadorDeEventos  junta tres seguidores (ojos, boca, cabeza), clasifica
                       los eventos cerrados y lleva los contadores.
"""

from somnolencia import config
from somnolencia.tipos import (
    CERRADO, ABIERTA, DISTRAIDO, SIN_DATO,
    PARPADEO, BOSTEZO, DISTRACCION, Evento,
)

# Resultados posibles al cerrarse un evento.
CERRADO_NORMALMENTE = "cerrado"
INDETERMINADO = "indeterminado"


def clasificar_parpadeo(duracion):
    """Tabla 1 del enunciado. Los límites son exactos: 0.5 s es normal y 7 s es lento."""
    if duracion <= config.PARPADEO_NORMAL_MAX_S:
        return "normal"
    if duracion <= config.PARPADEO_LENTO_MAX_S:
        return "lento"
    return "microsueno"


def banda_de_distraccion(duracion):
    """
    Entrega la banda a la que pertenece un episodio de distracción, o None
    si es tan corto que no se cuenta.

    Las bandas empiezan en 0.5, 1.0, 1.5 y 2.0 s. Un episodio pertenece a
    la banda más alta cuyo inicio alcanza. Ejemplo: 1.2 s cae en la banda 1.0.
    """
    banda = None
    for inicio_de_banda in config.BANDAS_DISTRACCION_S:
        if duracion >= inicio_de_banda:
            banda = inicio_de_banda
    return banda


class SeguidorDeEvento:
    """
    Sigue una señal y avisa cuando un evento termina.

    Reglas:
      - El evento empieza en el primer cuadro en estado activo.
      - Antirrebote: si en medio del evento aparecen hasta ANTIRREBOTE_CUADROS
        cuadros seguidos en reposo, se ignoran y el evento continúa. Solo se
        cierra cuando el reposo se sostiene más cuadros que ese número.
      - Al cerrarse, el fin del evento es la marca de tiempo del PRIMER
        cuadro en reposo, no la del cuadro en que se confirmó.
      - Si se pierde el dato durante el evento por más de
        SIN_DATO_TOLERANCIA_S, el evento se cierra como indeterminado.
    """

    def __init__(self, estado_activo):
        self.estado_activo = estado_activo
        self.antirrebote = config.ANTIRREBOTE_CUADROS
        self.tolerancia_sin_dato = config.SIN_DATO_TOLERANCIA_S

        self.en_curso = False        # hay un evento abierto
        self.inicio = None           # cuándo empezó el evento abierto
        self.cuadros_en_reposo = 0   # cuadros seguidos en reposo dentro del evento
        self.t_primer_reposo = None  # marca de tiempo del primero de esos cuadros
        self.t_sin_dato = None       # desde cuándo no hay dato dentro del evento

    def actualizar(self, t, estado):
        """
        Recibe el tiempo y el estado de la señal en un cuadro.

        Entrega None si no se cerró nada, o una terna (resultado, inicio, fin)
        cuando un evento termina en este cuadro.
        """
        # --- Cuadro en estado activo ---------------------------------------
        if estado == self.estado_activo:
            if not self.en_curso:
                self.en_curso = True
                self.inicio = t
            # El evento sigue vivo: se olvidan los cuadros de reposo o sin
            # dato que hubiera en medio.
            self.cuadros_en_reposo = 0
            self.t_primer_reposo = None
            self.t_sin_dato = None
            return None

        # Si no hay evento abierto, un cuadro en reposo o sin dato no hace nada.
        if not self.en_curso:
            return None

        # --- Cuadro sin dato dentro de un evento ---------------------------
        if estado == SIN_DATO:
            if self.t_sin_dato is None:
                self.t_sin_dato = t
            if t - self.t_sin_dato > self.tolerancia_sin_dato:
                # Se perdió el dato demasiado tiempo. No se sabe cómo terminó.
                inicio, desde = self.inicio, self.t_sin_dato
                self._reiniciar()
                return (INDETERMINADO, inicio, desde)
            return None

        # --- Cuadro en reposo dentro de un evento --------------------------
        self.t_sin_dato = None
        self.cuadros_en_reposo += 1
        if self.cuadros_en_reposo == 1:
            self.t_primer_reposo = t
        if self.cuadros_en_reposo > self.antirrebote:
            # El reposo se sostuvo: el evento terminó en el primer cuadro en reposo.
            inicio, fin = self.inicio, self.t_primer_reposo
            self._reiniciar()
            return (CERRADO_NORMALMENTE, inicio, fin)
        return None

    def duracion_en_curso(self, t):
        """Cuánto lleva el evento abierto, o 0.0 si no hay ninguno."""
        if not self.en_curso:
            return 0.0
        return t - self.inicio

    def cerrar_ahora(self, t):
        """Cierra el evento abierto al acabarse el video. Entrega la terna o None."""
        if not self.en_curso:
            return None
        inicio = self.inicio
        # Si ya había cuadros en reposo sin confirmar, el evento terminó ahí.
        fin = self.t_primer_reposo if self.t_primer_reposo is not None else t
        self._reiniciar()
        return (CERRADO_NORMALMENTE, inicio, fin)

    def _reiniciar(self):
        self.en_curso = False
        self.inicio = None
        self.cuadros_en_reposo = 0
        self.t_primer_reposo = None
        self.t_sin_dato = None


class RastreadorDeEventos:
    """Junta los tres seguidores, clasifica los eventos y lleva los contadores."""

    def __init__(self):
        self.seguidor_ojos = SeguidorDeEvento(CERRADO)
        self.seguidor_boca = SeguidorDeEvento(ABIERTA)
        self.seguidor_cabeza = SeguidorDeEvento(DISTRAIDO)

        self.eventos = []            # todos los eventos cerrados, en orden
        self.contadores = {}         # "tipo:categoria" -> cuántos van
        self.indeterminados = 0      # eventos que no se pudieron clasificar

        # Para PERCLOS: todos los cierres de ojos terminados, como (inicio, fin),
        # y los tramos en que no hubo dato de los ojos.
        self.cierres_de_ojos = []
        self.huecos_de_ojos = []
        self._hueco_inicio = None    # inicio del tramo sin dato que sigue abierto

    def actualizar(self, t, estado_ojos, estado_boca, estado_cabeza):
        """
        Recibe el tiempo y los tres estados de un cuadro.
        Entrega la lista de eventos que se cerraron en este cuadro.
        """
        nuevos = []

        cierre = self.seguidor_ojos.actualizar(t, estado_ojos)
        self._procesar_ojos(cierre, nuevos)
        self._seguir_huecos(t, estado_ojos)

        cierre = self.seguidor_boca.actualizar(t, estado_boca)
        self._procesar_boca(cierre, nuevos)

        cierre = self.seguidor_cabeza.actualizar(t, estado_cabeza)
        self._procesar_cabeza(cierre, nuevos)

        return nuevos

    def cerrar_todo(self, t):
        """Al acabarse el video, cierra y clasifica lo que quedó abierto."""
        nuevos = []
        self._procesar_ojos(self.seguidor_ojos.cerrar_ahora(t), nuevos)
        self._procesar_boca(self.seguidor_boca.cerrar_ahora(t), nuevos)
        self._procesar_cabeza(self.seguidor_cabeza.cerrar_ahora(t), nuevos)
        if self._hueco_inicio is not None:
            self.huecos_de_ojos.append((self._hueco_inicio, t))
            self._hueco_inicio = None
        return nuevos

    # ----- Consultas para la interfaz, PERCLOS y las alertas ----------------

    def cierre_en_curso(self, t):
        """Segundos que lleva el cierre de ojos abierto (0.0 si no hay)."""
        return self.seguidor_ojos.duracion_en_curso(t)

    def bostezo_en_curso(self, t):
        return self.seguidor_boca.duracion_en_curso(t)

    def distraccion_en_curso(self, t):
        return self.seguidor_cabeza.duracion_en_curso(t)

    def cierres_para_perclos(self, t):
        """Cierres terminados más el que sigue abierto, contado hasta ahora."""
        cierres = list(self.cierres_de_ojos)
        if self.seguidor_ojos.en_curso:
            cierres.append((self.seguidor_ojos.inicio, t))
        return cierres

    def huecos_para_perclos(self, t):
        """Tramos sin dato terminados más el que sigue abierto."""
        huecos = list(self.huecos_de_ojos)
        if self._hueco_inicio is not None:
            huecos.append((self._hueco_inicio, t))
        return huecos

    # ----- Clasificación ------------------------------------------------------

    def _procesar_ojos(self, cierre, nuevos):
        if cierre is None:
            return
        resultado, inicio, fin = cierre
        if resultado == INDETERMINADO:
            # No se sabe cuándo se abrieron los ojos. No se cuenta como
            # parpadeo, y desde que se perdió el dato cuenta como tramo sin dato.
            self.indeterminados += 1
            self._hueco_inicio = fin
            return
        duracion = self._duracion(inicio, fin)
        self.cierres_de_ojos.append((inicio, fin))
        self._registrar(Evento(PARPADEO, inicio, fin, duracion,
                               clasificar_parpadeo(duracion)), nuevos)

    def _procesar_boca(self, cierre, nuevos):
        if cierre is None:
            return
        resultado, inicio, fin = cierre
        if resultado == INDETERMINADO:
            self.indeterminados += 1
            return
        duracion = self._duracion(inicio, fin)
        # Una apertura corta (hablar, reír) no es un bostezo.
        if duracion >= config.BOSTEZO_MIN_S:
            self._registrar(Evento(BOSTEZO, inicio, fin, duracion, "bostezo"), nuevos)

    def _procesar_cabeza(self, cierre, nuevos):
        if cierre is None:
            return
        resultado, inicio, fin = cierre
        duracion = self._duracion(inicio, fin)
        banda = banda_de_distraccion(duracion)
        # Un giro menor a la primera banda no se cuenta.
        if banda is not None:
            self._registrar(Evento(DISTRACCION, inicio, fin, duracion, str(banda)), nuevos)

    def _duracion(self, inicio, fin):
        # Se redondea a milésimas para que una resta como 10.6 - 10.0 no dé
        # 0.5999999 por la aritmética de punto flotante y cambie de categoría.
        return round(fin - inicio, 3)

    def _registrar(self, evento, nuevos):
        self.eventos.append(evento)
        clave = evento.tipo + ":" + evento.categoria
        self.contadores[clave] = self.contadores.get(clave, 0) + 1
        nuevos.append(evento)

    def _seguir_huecos(self, t, estado_ojos):
        """Lleva la cuenta de los tramos en que no hubo dato de los ojos."""
        if estado_ojos == SIN_DATO:
            # Dentro de un cierre abierto, la falta de dato se tolera un
            # momento y no se anota como hueco.
            if not self.seguidor_ojos.en_curso and self._hueco_inicio is None:
                self._hueco_inicio = t
        else:
            if self._hueco_inicio is not None:
                self.huecos_de_ojos.append((self._hueco_inicio, t))
                self._hueco_inicio = None
