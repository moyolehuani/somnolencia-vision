"""
Dos formas de comparar imágenes.

correlacion_normalizada   busca una plantilla dentro de una imagen. Se usa
                          para seguir el rostro y para medir qué tan de
                          frente está.

correlacion_de_fase       mide cuánto se desplazó una imagen respecto a
                          otra del mismo tamaño, con la transformada de
                          Fourier (práctica 6). Se usa para medir el
                          movimiento de la cabeza entre dos cuadros.
"""

import numpy as np


def correlacion_normalizada(imagen, plantilla):
    """
    Desliza la plantilla sobre la imagen y entrega un mapa con un valor
    entre -1 y 1 por cada posición. El valor 1 significa que el trozo de
    imagen en esa posición es idéntico a la plantilla, salvo por brillo y
    contraste.

    En cada posición el valor es

                  suma de (I - media de I) * (P - media de P)
        -----------------------------------------------------------
        raíz( suma de (I - media de I)^2 * suma de (P - media de P)^2 )

    donde I es el trozo de imagen bajo la plantilla y P es la plantilla.
    Restar las medias quita el efecto del brillo. Dividir entre las normas
    quita el efecto del contraste.

    El mapa mide (alto de imagen - alto de plantilla + 1) por
    (ancho de imagen - ancho de plantilla + 1). La posición (y, x) del mapa
    corresponde a colocar la esquina superior izquierda de la plantilla en
    el pixel (y, x) de la imagen.

    Costo. Hay un ciclo por posición, así que conviene pasarle solo la
    zona de la imagen donde puede estar la plantilla. Al seguir el rostro
    se busca en una ventana de 17 x 17 posiciones y tarda unos 3 ms. Buscar
    en toda la imagen pequeña tarda cerca de 80 ms, y solo se hace cuando
    el rostro se perdió.
    """
    alto_p, ancho_p = plantilla.shape
    alto_mapa = imagen.shape[0] - alto_p + 1
    ancho_mapa = imagen.shape[1] - ancho_p + 1

    # Se trabaja en doble precisión para no perder decimales en las sumas.
    imagen = imagen.astype(np.float64)
    p = plantilla.astype(np.float64)
    p = p - p.mean()                       # plantilla sin su media
    norma_p = np.sqrt((p * p).sum())

    mapa = np.zeros((alto_mapa, ancho_mapa))
    for y in range(alto_mapa):
        for x in range(ancho_mapa):
            # Trozo de imagen que queda debajo de la plantilla en esta posición.
            trozo = imagen[y:y + alto_p, x:x + ancho_p]
            t = trozo - trozo.mean()       # trozo sin su media
            denominador = norma_p * np.sqrt((t * t).sum())
            # En una zona completamente lisa el denominador es cero. Ahí se deja 0.
            if denominador > 1e-6:
                mapa[y, x] = (t * p).sum() / denominador
    return mapa.astype(np.float32)


def posicion_del_maximo(mapa):
    """Entrega (y, x, valor) del punto más alto de un mapa."""
    y, x = np.unravel_index(int(mapa.argmax()), mapa.shape)
    return int(y), int(x), float(mapa[y, x])


def correlacion_de_fase(anterior, actual):
    """
    Mide cuánto se desplazó el contenido de "actual" respecto a "anterior".
    Las dos imágenes deben medir lo mismo.

    Entrega (dx, dy, pico):
        dx     pixeles hacia la derecha (negativo: hacia la izquierda)
        dy     pixeles hacia abajo (negativo: hacia arriba)
        pico   qué tan nítido fue el resultado, entre 0 y 1. Un valor bajo
               significa que las imágenes no son una desplazada de la otra.

    Por qué funciona. Desplazar una imagen no cambia la magnitud de su
    transformada de Fourier, solo su fase, y la cambia en proporción al
    desplazamiento. Si se multiplica una transformada por el conjugado de
    la otra y se divide entre la magnitud, queda solo esa diferencia de
    fase. Su transformada inversa es una imagen casi vacía con un pico, y
    la posición del pico es el desplazamiento.
    """
    alto, ancho = anterior.shape

    # 1. Ventana que atenúa las imágenes hacia sus orillas. Fourier supone
    #    que la imagen se repite, y sin ventana el salto entre una orilla y
    #    la opuesta ensucia el resultado.
    ventana = np.outer(np.hanning(alto), np.hanning(ancho))

    # 2. Transformadas de Fourier de las dos imágenes.
    f_anterior = np.fft.fft2(anterior * ventana)
    f_actual = np.fft.fft2(actual * ventana)

    # 3. Espectro cruzado, y se conserva solo su fase.
    cruzado = np.conj(f_anterior) * f_actual
    cruzado = cruzado / (np.abs(cruzado) + 1e-9)

    # 4. De regreso al espacio de la imagen.
    respuesta = np.real(np.fft.ifft2(cruzado))

    # 5. El pico marca el desplazamiento.
    y, x, pico = posicion_del_maximo(respuesta)

    # 6. Un pico en la segunda mitad del arreglo es un desplazamiento
    #    negativo: con 64 columnas, la posición 62 significa -2.
    dy = y - alto if y > alto // 2 else y
    dx = x - ancho if x > ancho // 2 else x
    return dx, dy, pico
