"""
Captura: de la cámara, de un archivo de video o de la escena sintética.

Entrega cada cuadro en grises, ya en el tamaño de trabajo, junto con su
marca de tiempo en segundos.

La marca de tiempo depende de la fuente:
  - Con cámara es el reloj de la computadora al leer el cuadro.
  - Con un archivo es el número de cuadro dividido entre los cuadros por
    segundo del video. Así el resultado es el mismo sin importar qué tan
    rápido procese la computadora, y la evaluación se puede repetir.

Leer la cámara o un video y pasar a grises son adquisición y conversión de
formato, que el enunciado permite hacer con biblioteca. El cambio de
tamaño sí se hace con los algoritmos propios.
"""

import time

import cv2

from somnolencia import config
from somnolencia.percepcion.preproceso import a_grises
from somnolencia.percepcion.piramide import reducir
from somnolencia.percepcion.geometria import recortar_y_escalar


def a_tamano_de_trabajo(gris):
    """Lleva un cuadro en grises al tamaño de trabajo (640 de ancho)."""
    alto, ancho = gris.shape
    if ancho == config.TRABAJO_ANCHO:
        resultado = gris
    elif ancho == 2 * config.TRABAJO_ANCHO:
        # Caso normal con los videos de 1280x720: se reduce a la mitad
        # con la pirámide.
        resultado = reducir(gris)
    else:
        # Cualquier otro tamaño: se escala con mapeo inverso, conservando
        # la proporción.
        alto_nuevo = int(round(alto * config.TRABAJO_ANCHO / ancho))
        resultado = recortar_y_escalar(gris, (0, 0, ancho, alto),
                                       config.TRABAJO_ANCHO, alto_nuevo)
    # Si quedó más alto que el tamaño de trabajo (cámaras 4:3), se
    # conserva la franja central.
    sobra = resultado.shape[0] - config.TRABAJO_ALTO
    if sobra > 0:
        resultado = resultado[sobra // 2: sobra // 2 + config.TRABAJO_ALTO, :]
    return resultado


class Captura:

    def __init__(self, fuente):
        """fuente: "0" o "1" para una cámara, "escena", o la ruta de un video."""
        self.fuente = str(fuente)
        self.es_camara = self.fuente.isdigit()
        self.es_escena = self.fuente == "escena"
        self.numero_de_cuadro = 0
        self._escena = None
        self._video = None

        if self.es_escena:
            from somnolencia import escena_sintetica
            self._escena = escena_sintetica.generar()
            self.fps = 15.0
        else:
            self._video = cv2.VideoCapture(int(self.fuente) if self.es_camara else self.fuente)
            if not self._video.isOpened():
                raise RuntimeError("No se pudo abrir la fuente: %s" % self.fuente)
            if self.es_camara:
                # Se le pide a la cámara un tamaño cercano al de trabajo.
                self._video.set(cv2.CAP_PROP_FRAME_WIDTH, config.GRABACION_ANCHO)
                self._video.set(cv2.CAP_PROP_FRAME_HEIGHT, config.GRABACION_ALTO)
            self.fps = self._video.get(cv2.CAP_PROP_FPS) or 30.0
            self._t_inicio = time.monotonic()

    def leer(self):
        """Entrega (gris en tamaño de trabajo, t), o None cuando ya no hay cuadros."""
        if self.es_escena:
            siguiente = next(self._escena, None)
            if siguiente is None:
                return None
            t, gris = siguiente
            return gris, t

        hay_cuadro, cuadro = self._video.read()
        if not hay_cuadro:
            return None
        if self.es_camara:
            t = time.monotonic() - self._t_inicio
        else:
            t = self.numero_de_cuadro / self.fps
        self.numero_de_cuadro += 1
        return a_tamano_de_trabajo(a_grises(cuadro)), t

    def cerrar(self):
        if self._video is not None:
            self._video.release()
