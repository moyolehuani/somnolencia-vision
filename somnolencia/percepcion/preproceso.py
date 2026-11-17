"""
Preprocesamiento: grises y filtrado espacial.

Aquí está la pieza básica de todos los filtros del sistema: filtrar_1d,
que aplica un núcleo de una dimensión a lo largo de los renglones o de las
columnas. Un filtro separable de dos dimensiones se obtiene aplicándola dos
veces, una por dirección. Es lo que se hizo en la práctica 5.

También está la especificación de histograma de la práctica 4, que iguala
la iluminación de una imagen a la de una imagen de referencia.
"""

import cv2
import numpy as np

from somnolencia import config


def a_grises(cuadro):
    """
    Convierte un cuadro BGR de OpenCV a grises, como arreglo de flotantes.

    Es una conversión de formato, que el enunciado permite hacer con
    biblioteca. Se trabaja en flotantes para no perder precisión al filtrar.
    """
    return cv2.cvtColor(cuadro, cv2.COLOR_BGR2GRAY).astype(np.float32)


def filtrar_1d(img, nucleo, eje):
    """
    Aplica un núcleo de una dimensión a lo largo de un eje de la imagen.

    eje = 0   el núcleo recorre la imagen de arriba hacia abajo
    eje = 1   el núcleo recorre la imagen de izquierda a derecha

    En vez de recorrer pixel por pixel, se suman copias desplazadas de la
    imagen, cada una multiplicada por un peso del núcleo. Con un núcleo de
    5 elementos son 5 sumas de arreglos completos, que NumPy hace rápido.

    En las orillas la imagen se extiende reflejándola, sin repetir el pixel
    del borde. Es el mismo tratamiento que usa OpenCV por omisión, y por
    eso el resultado coincide exactamente con el suyo al verificar.
    """
    radio = len(nucleo) // 2
    relleno = [(0, 0), (0, 0)]
    relleno[eje] = (radio, radio)
    extendida = np.pad(img, relleno, mode="reflect")

    largo = img.shape[eje]
    salida = np.zeros(img.shape, dtype=np.float32)
    for desplazamiento, peso in enumerate(nucleo):
        if eje == 0:
            salida += peso * extendida[desplazamiento:desplazamiento + largo, :]
        else:
            salida += peso * extendida[:, desplazamiento:desplazamiento + largo]
    return salida


def suavizar_binomial(img):
    """
    Filtro pasabajas binomial de 5x5, aplicado de forma separable.

    El núcleo de una dimensión es (1, 4, 6, 4, 1) / 16. Aplicarlo por
    renglones y luego por columnas equivale al núcleo de 5x5 que resulta de
    multiplicar el vector por sí mismo, pero cuesta 10 sumas en vez de 25.
    """
    nucleo = np.array(config.NUCLEO_BINOMIAL, dtype=np.float32)
    nucleo = nucleo / nucleo.sum()
    return filtrar_1d(filtrar_1d(img, nucleo, eje=1), nucleo, eje=0)


def histograma_acumulado(img):
    """
    Histograma acumulado normalizado de una imagen en grises.

    Entrega un arreglo de 256 valores. El valor en la posición g es la
    fracción de pixeles con nivel de gris menor o igual a g. Empieza cerca
    de 0 y termina en 1.
    """
    # Los niveles se redondean a enteros entre 0 y 255.
    niveles = np.clip(np.rint(img), 0, 255).astype(np.uint8)
    # Cuántos pixeles hay de cada nivel.
    histograma = np.bincount(niveles.ravel(), minlength=256)
    # Suma acumulada, dividida entre el total de pixeles.
    return np.cumsum(histograma) / niveles.size


def tabla_de_especificacion(img, acumulado_ref):
    """
    Arma la tabla de 256 entradas que lleva los niveles de gris de img a
    los de la referencia (práctica 4).

    Para cada nivel g de la imagen se busca el nivel r cuyo acumulado de
    referencia es el más cercano al acumulado de g en la imagen.

    Ejemplo: si el 30% de los pixeles de la imagen tiene nivel 80 o menos,
    y en la referencia el 30% de los pixeles tiene nivel 120 o menos, la
    tabla manda el nivel 80 al 120.
    """
    acumulado_img = histograma_acumulado(img)
    # Matriz de 256 x 256 con la distancia entre cada acumulado de la imagen
    # (renglones) y cada acumulado de la referencia (columnas).
    distancia = np.abs(acumulado_ref[np.newaxis, :] - acumulado_img[:, np.newaxis])
    # Para cada nivel de la imagen, el nivel de referencia más cercano.
    return distancia.argmin(axis=1)


def aplicar_tabla(img, tabla):
    """Reemplaza cada pixel por el valor que la tabla da a su nivel de gris."""
    niveles = np.clip(np.rint(img), 0, 255).astype(np.uint8)
    return tabla[niveles].astype(np.float32)


def especificar_histograma(img, acumulado_ref):
    """
    Cambia los niveles de gris de img para que su histograma acumulado se
    parezca al de referencia: arma la tabla con la propia imagen y la aplica.

    Cuidado: esto supone que la imagen y la referencia muestran lo mismo y
    solo cambió la luz. Si cambió el contenido (por ejemplo, la boca se
    abrió y hay más pixeles oscuros), la especificación "corrige" ese
    cambio como si fuera de luz. Por eso el sistema arma la tabla con una
    zona del rostro que no cambia y la aplica al resto con aplicar_tabla.
    """
    return aplicar_tabla(img, tabla_de_especificacion(img, acumulado_ref))
