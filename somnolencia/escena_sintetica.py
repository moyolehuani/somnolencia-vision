"""
Escena sintética: un video dibujado, sin ninguna persona.

Dibuja una "cara" muy simple (un rectángulo con dos ojos, cejas, nariz y
boca) que se mueve despacio sobre un fondo. Según un guion, la cara cierra
los ojos, abre la boca o se da vuelta.

Sirve para dos cosas:

  - Probar que todas las piezas del sistema están bien conectadas, de
    principio a fin, sin cámara y sin videos de personas.
  - Ver el sistema funcionando en pantalla:
        python -m somnolencia.principal --fuente escena

No sirve para saber qué tan bien funciona el sistema con caras reales. Un
dibujo es mucho más fácil que una persona. Eso solo se mide con videos.
"""

import numpy as np

from somnolencia import config
from somnolencia.percepcion.preproceso import suavizar_binomial

ANCHO, ALTO = config.TRABAJO_ANCHO, config.TRABAJO_ALTO
CARA_ANCHO, CARA_ALTO = config.RECUADRO_ANCHO, config.RECUADRO_ALTO
CARA_X = (ANCHO - CARA_ANCHO) // 2      # posición de reposo de la cara: centrada,
CARA_Y = (ALTO - CARA_ALTO) // 2        # justo donde va el recuadro de calibración

# Guion: (inicio, fin, qué pasa). Los primeros 5 s son la calibración.
GUION = [
    (3.0, 5.0, "ojos_cerrados"),     # calibración: paso de ojos cerrados
    (8.0, 8.3, "ojos_cerrados"),     # parpadeo normal
    (11.0, 14.0, "ojos_cerrados"),   # cierre de 3 s: parpadeo lento
    (18.0, 20.5, "giro"),            # giro de 2.5 s: distracción, banda 2.0
    (24.0, 27.0, "boca_abierta"),    # bostezo de 3 s
    (31.0, 39.5, "ojos_cerrados"),   # cierre de 8.5 s: microsueño
]
DURACION = 45.0

# Lo que el sistema debe reportar al procesar este guion.
EVENTOS_ESPERADOS = {
    "parpadeo:normal": 1,
    "parpadeo:lento": 1,
    "parpadeo:microsueno": 1,
    "bostezo:bostezo": 1,
    "distraccion:2.0": 1,
}


def anotaciones():
    """
    Entrega los eventos del guion como una lista de (tipo, inicio, fin),
    igual que un archivo de anotaciones hecho a mano. No incluye la
    calibración, que no se anota.
    """
    tipo_de = {"ojos_cerrados": "parpadeo", "boca_abierta": "bostezo", "giro": "distraccion"}
    fin_de_calibracion = config.CALIBRACION_ABIERTOS_S + config.CALIBRACION_CERRADOS_S
    return [(tipo_de[que], inicio, fin) for inicio, fin, que in GUION
            if inicio >= fin_de_calibracion]


def _textura(alto, ancho, semilla, minimo, maximo):
    """Ruido suavizado con valores entre minimo y maximo."""
    generador = np.random.default_rng(semilla)
    img = generador.random((alto, ancho)).astype(np.float32)
    for _ in range(3):
        img = suavizar_binomial(img)
    img = (img - img.min()) / (img.max() - img.min())
    return minimo + img * (maximo - minimo)


FONDO = _textura(ALTO, ANCHO, 1, 60, 150)
PIEL = _textura(CARA_ALTO, CARA_ANCHO, 2, 160, 185)
DE_LADO = _textura(CARA_ALTO, CARA_ANCHO, 3, 90, 185)    # lo que se ve durante un giro


def _pasa(t, que):
    """True si en el instante t el guion marca ese suceso."""
    return any(inicio <= t < fin and nombre == que for inicio, fin, nombre in GUION)


def _dibujar_cara(ojos_cerrados, boca_abierta):
    """Dibuja la cara de frente, de CARA_ANCHO x CARA_ALTO."""
    cara = PIEL.copy()
    y, x = np.mgrid[0:CARA_ALTO, 0:CARA_ANCHO]

    for centro_x in (30, 80):
        cara[34:38, centro_x - 14:centro_x + 14] = 70             # ceja
        if ojos_cerrados:
            cara[54:57, centro_x - 11:centro_x + 11] = 60         # línea de pestañas
        else:
            cara[(x - centro_x) ** 2 + (y - 55) ** 2 <= 7 ** 2] = 45   # iris

    cara[66:92, 54:56] = 140                                       # nariz
    if boca_abierta:
        cara[((x - 55) / 15.0) ** 2 + ((y - 113) / 19.0) ** 2 <= 1] = 30   # boca abierta
    else:
        cara[112:114, 40:70] = 90                                  # labios cerrados
    return cara


def cuadro(t, numero=0):
    """Entrega el cuadro en grises (640x360) del instante t."""
    img = FONDO.copy()
    # La cara se mece despacio, como una persona que no está del todo quieta.
    x = CARA_X + int(round(20 * np.sin(2 * np.pi * t / 8)))
    y = CARA_Y + int(round(6 * np.sin(2 * np.pi * t / 5)))
    if _pasa(t, "giro"):
        cara = DE_LADO
    else:
        cara = _dibujar_cara(_pasa(t, "ojos_cerrados"), _pasa(t, "boca_abierta"))
    img[y:y + CARA_ALTO, x:x + CARA_ANCHO] = cara
    # Un poco de ruido distinto en cada cuadro, como el de una cámara.
    ruido = np.random.default_rng(1000 + numero).normal(0, 2, img.shape)
    return np.clip(img + ruido, 0, 255).astype(np.float32)


def caja_inicial():
    """Caja de la cara en el primer cuadro: la del recuadro de calibración."""
    return (CARA_X, CARA_Y, CARA_ANCHO, CARA_ALTO)


def generar(fps=15, duracion=DURACION):
    """Entrega (t, cuadro en grises) cuadro por cuadro."""
    for numero in range(int(duracion * fps) + 1):
        t = round(numero / fps, 6)
        yield t, cuadro(t, numero)
