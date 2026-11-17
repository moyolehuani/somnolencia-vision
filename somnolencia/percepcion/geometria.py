"""
Recorte y cambio de tamaño con mapeo inverso (práctica 3).

Sirve para llevar el rostro, que en cada cuadro tiene una posición y un
tamaño distintos, a una imagen de tamaño fijo. Así los ojos y la boca
caen siempre en los mismos renglones.

Mapeo inverso quiere decir que se recorre la imagen de SALIDA y, para cada
uno de sus pixeles, se calcula de qué punto de la imagen original viene.
Si se hiciera al revés, recorriendo la original, quedarían huecos en la
salida. Como el punto de origen casi nunca cae exactamente sobre un pixel,
su valor se interpola entre los cuatro pixeles vecinos.
"""

import numpy as np

from somnolencia import config


def recortar_y_escalar(img, caja, ancho_salida, alto_salida):
    """
    Toma la región "caja" de la imagen y la entrega con el tamaño pedido.

    caja   (x, y, ancho, alto) de la región, en pixeles de la imagen
           original. Puede llevar decimales.

    La transformación solo escala y traslada, sin girar. Por eso la
    coordenada x de origen depende solo de la columna de salida, y la
    coordenada y solo del renglón. Se calculan una vez por columna y una
    vez por renglón, sin ciclos por pixel.
    """
    x0, y0, ancho, alto = caja
    alto_img, ancho_img = img.shape

    # Cuántos pixeles de la original corresponden a uno de la salida.
    escala_x = ancho / ancho_salida
    escala_y = alto / alto_salida

    # Coordenada de origen de cada columna y de cada renglón de la salida.
    # El 0.5 hace que se alineen los centros de los pixeles y no sus esquinas.
    x = x0 + (np.arange(ancho_salida) + 0.5) * escala_x - 0.5
    y = y0 + (np.arange(alto_salida) + 0.5) * escala_y - 0.5

    # Si la caja se sale de la imagen, se usa el pixel de la orilla.
    x = np.clip(x, 0, ancho_img - 1)
    y = np.clip(y, 0, alto_img - 1)

    # Vecinos de cada coordenada y qué tan cerca queda del segundo vecino.
    x_izq = np.floor(x).astype(int)
    x_der = np.minimum(x_izq + 1, ancho_img - 1)
    peso_x = (x - x_izq).astype(np.float32)

    y_arr = np.floor(y).astype(int)
    y_aba = np.minimum(y_arr + 1, alto_img - 1)
    peso_y = (y - y_arr).astype(np.float32)

    # Interpolación bilineal en dos pasos.
    # Paso 1: a lo ancho, en el renglón de arriba y en el de abajo.
    renglones_arr = img[y_arr, :]
    renglones_aba = img[y_aba, :]
    arriba = renglones_arr[:, x_izq] * (1 - peso_x) + renglones_arr[:, x_der] * peso_x
    abajo = renglones_aba[:, x_izq] * (1 - peso_x) + renglones_aba[:, x_der] * peso_x
    # Paso 2: a lo alto, entre los dos resultados.
    salida = arriba * (1 - peso_y)[:, np.newaxis] + abajo * peso_y[:, np.newaxis]
    return salida.astype(np.float32)


def normalizar_rostro(img, caja):
    """Lleva la caja del rostro al tamaño fijo de config.py (128 x 160)."""
    return recortar_y_escalar(img, caja, config.ROSTRO_ANCHO, config.ROSTRO_ALTO)


def recortes_de_ojos(rostro):
    """
    Entrega los recortes de los dos ojos a partir del rostro normalizado.

    El rostro normalizado mide 128 de ancho. Cada mitad contiene un ojo y
    mide 64, que es el ancho con el que se validó la medida de ojos. Los
    renglones salen de config.py y son provisionales: hay que ajustarlos
    viendo los recortes en la vista de depuración.

    Entrega (mitad izquierda de la imagen, mitad derecha de la imagen).
    """
    alto, ancho = rostro.shape
    r0 = int(config.OJOS_FILA_INICIAL * alto)
    r1 = int(config.OJOS_FILA_FINAL * alto)
    mitad = ancho // 2
    return rostro[r0:r1, :mitad], rostro[r0:r1, mitad:]
