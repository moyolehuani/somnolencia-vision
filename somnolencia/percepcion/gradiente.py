"""
Gradientes y la medida de bordes que usan los ojos.

Idea de la medida. En un ojo abierto se ve el iris, que es un disco oscuro.
Sus lados izquierdo y derecho son bordes verticales, y un borde vertical
aparece en el gradiente HORIZONTAL. En un ojo cerrado solo queda la línea
de las pestañas, que es un borde horizontal y aparece en el gradiente
VERTICAL. Entonces el cociente

    razón = suma de |gradiente horizontal| / suma de |gradiente vertical|

calculado alrededor de la zona más oscura del ojo, es alto con el ojo
abierto y bajo con el ojo cerrado.

Resultado medido sobre los 1452 recortes de ojos del dataset de Kaggle
(726 abiertos y 726 cerrados, sin calibración): mediana de 0.72 en
abiertos y de 0.41 en cerrados. Ver docs/evaluacion.md.

La primera idea del proyecto era medir la separación entre los bordes de
los párpados en el perfil del gradiente vertical. Se probó con las mismas
imágenes y no distingue abierto de cerrado, así que se descartó.
"""

import numpy as np

from somnolencia import config
from somnolencia.percepcion.preproceso import filtrar_1d

# Núcleos de Sobel, separados en sus dos partes (práctica 5).
SOBEL_SUAVIZADO = (1, 2, 1)     # suaviza en la dirección perpendicular a la derivada
SOBEL_DERIVADA = (-1, 0, 1)     # diferencia entre el pixel siguiente y el anterior


def gradiente_vertical(img):
    """
    Derivada en dirección vertical (Sobel). Responde a bordes horizontales,
    como la línea de las pestañas.
    """
    return filtrar_1d(filtrar_1d(img, SOBEL_SUAVIZADO, eje=1), SOBEL_DERIVADA, eje=0)


def gradiente_horizontal(img):
    """
    Derivada en dirección horizontal (Sobel). Responde a bordes verticales,
    como los lados del iris.
    """
    return filtrar_1d(filtrar_1d(img, SOBEL_SUAVIZADO, eje=0), SOBEL_DERIVADA, eje=1)


def banda_mas_oscura(img, columnas, alto_de_banda):
    """
    Encuentra el grupo de renglones seguidos más oscuro de la imagen.

    En un ojo, lo más oscuro es el iris o la línea de las pestañas, así que
    esta banda cae sobre el ojo y no sobre el párpado o la mejilla.

    columnas        (inicio, fin) de las columnas que se toman en cuenta
    alto_de_banda   cuántos renglones seguidos forman la banda

    Entrega el número del primer renglón de la banda.
    """
    c0, c1 = columnas
    # Brillo promedio de cada renglón, solo en las columnas centrales.
    brillo_por_renglon = img[:, c0:c1].mean(axis=1)
    # Promedio de cada grupo de renglones seguidos (promedio móvil).
    ventana = np.ones(alto_de_banda) / alto_de_banda
    brillo_por_banda = np.convolve(brillo_por_renglon, ventana, mode="valid")
    return int(brillo_por_banda.argmin())


def razon_de_bordes(ojo):
    """
    Entrega la razón entre bordes verticales y bordes horizontales alrededor
    de la banda más oscura de un recorte de ojo ya suavizado.

    ojo   imagen en grises de un solo ojo, sin la ceja, de unos 64 pixeles
          de ancho, que es el tamaño con el que se validó la medida

    Valores altos indican ojo abierto y valores bajos, ojo cerrado.
    """
    alto, ancho = ojo.shape
    # Columnas centrales: se dejan fuera las orillas del recorte.
    c0 = int(config.OJOS_COLUMNA_INICIAL * ancho)
    c1 = int(config.OJOS_COLUMNA_FINAL * ancho)

    # 1. Ubicar el ojo: la banda de renglones más oscura.
    primer_renglon = banda_mas_oscura(ojo, (c0, c1), config.OJOS_ALTO_DE_BANDA)

    # 2. Tomar esa banda más unos renglones de margen arriba y abajo.
    r0 = max(0, primer_renglon - config.OJOS_MARGEN_DE_BANDA)
    r1 = min(alto, primer_renglon + config.OJOS_ALTO_DE_BANDA + config.OJOS_MARGEN_DE_BANDA)

    # 3. Sumar la magnitud de cada gradiente dentro de esa zona.
    bordes_verticales = np.abs(gradiente_horizontal(ojo))[r0:r1, c0:c1].sum()
    bordes_horizontales = np.abs(gradiente_vertical(ojo))[r0:r1, c0:c1].sum()

    # El 1e-6 evita dividir entre cero en una imagen completamente lisa.
    return float(bordes_verticales / (bordes_horizontales + 1e-6))
