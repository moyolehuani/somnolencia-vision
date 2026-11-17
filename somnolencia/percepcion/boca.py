"""
Apertura de la boca.

ATENCIÓN: esta medida NO está validada con imágenes reales (decisión D31).
Funciona con la escena sintética de prueba, pero eso no dice nada sobre
bocas de verdad. Hay que probarla con los videos del guion G3 antes de
darla por buena, como se hizo con la medida de ojos.

Idea. Al abrir la boca aparece una zona oscura, y su alto crece con la
apertura. En la franja de la boca se cuenta, columna por columna, cuántos
pixeles son más oscuros que un umbral, y se toma el alto típico de las
columnas más altas. Ese alto se divide entre el alto del rostro.

El umbral de "oscuro" es un nivel de gris fijo que se toma en la
calibración. Por eso la franja debe venir del rostro con el histograma ya
especificado: así el mismo nivel de gris significa lo mismo aunque cambie
la luz.
"""

import numpy as np

from somnolencia import config
from somnolencia.tipos import Medicion


def franja_de_boca(rostro):
    """Recorta la zona de la boca del rostro normalizado."""
    alto, ancho = rostro.shape
    r0 = int(config.BOCA_FILA_INICIAL * alto)
    r1 = int(config.BOCA_FILA_FINAL * alto)
    c0 = int(config.BOCA_COLUMNA_INICIAL * ancho)
    c1 = int(config.BOCA_COLUMNA_FINAL * ancho)
    return rostro[r0:r1, c0:c1]


def umbral_oscuro_en_reposo(rostro):
    """
    Nivel de gris que separa "oscuro" de "piel", medido con la boca cerrada.
    Es el punto medio entre lo más oscuro de la franja (la línea de los
    labios) y su nivel típico (la piel).
    """
    franja = franja_de_boca(rostro)
    return float((np.percentile(franja, 2) + np.median(franja)) / 2)


def medida_de_boca(rostro, umbral_oscuro):
    """
    Alto de la zona oscura de la boca, como fracción del alto del rostro.

    En cada columna se cuentan los pixeles oscuros. Se ordenan las columnas
    por ese conteo y se toma la mediana de la cuarta parte más alta, para
    que una sola columna con ruido no decida el resultado.
    """
    franja = franja_de_boca(rostro)
    oscuros_por_columna = np.sort((franja < umbral_oscuro).sum(axis=0))
    cuarta_parte = max(1, len(oscuros_por_columna) // 4)
    alto_oscuro = np.median(oscuros_por_columna[-cuarta_parte:])
    return float(alto_oscuro / rostro.shape[0])


def medir_boca(rostro, t, umbral_oscuro, medida_en_reposo):
    """Entrega la Medicion de apertura de la boca: la medida menos su valor en reposo."""
    apertura = medida_de_boca(rostro, umbral_oscuro) - medida_en_reposo
    return Medicion(t, min(1.0, max(0.0, apertura)), True)
