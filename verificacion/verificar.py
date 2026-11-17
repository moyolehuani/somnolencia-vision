"""
Compara cada algoritmo propio contra la función equivalente de OpenCV.

Uso, desde la raíz del repositorio:

    python -m verificacion.verificar

Imprime una tabla con la diferencia entre el resultado propio y el de
OpenCV, y cuánto tarda cada uno. Las imágenes de prueba son texturas
generadas con números al azar (con semilla fija, para que el resultado se
pueda repetir). No se usa ninguna imagen de un rostro.

Los tamaños de imagen son los que usa el sistema: 640x360 para el cuadro,
128x160 para el rostro normalizado y 160x90 para el nivel más pequeño de
la pirámide.
"""

import time

import cv2
import numpy as np

from somnolencia.percepcion.preproceso import (
    suavizar_binomial, histograma_acumulado, especificar_histograma,
)
from somnolencia.percepcion.gradiente import gradiente_vertical, gradiente_horizontal
from somnolencia.percepcion.piramide import reducir, piramide_gaussiana
from somnolencia.percepcion.correlacion import (
    correlacion_normalizada, posicion_del_maximo, correlacion_de_fase,
)
from somnolencia.percepcion.geometria import recortar_y_escalar

GENERADOR = np.random.default_rng(2027)


def textura(alto, ancho):
    """Imagen de prueba: ruido suavizado, con valores entre 0 y 255."""
    img = (GENERADOR.random((alto, ancho)) * 255).astype(np.float32)
    for _ in range(3):
        img = suavizar_binomial(img)
    img = (img - img.min()) / (img.max() - img.min()) * 255
    return img.astype(np.float32)


def milisegundos(funcion, repeticiones=20):
    """Tiempo promedio de una llamada, en milisegundos."""
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        funcion()
    return (time.perf_counter() - inicio) / repeticiones * 1000


def renglon(nombre, referencia, medida, valor, ms_propio, ms_opencv):
    print("%-28s %-22s %-34s %-12s %8.2f %8.2f"
          % (nombre, referencia, medida, valor, ms_propio, ms_opencv))


def principal():
    cuadro = textura(360, 640)                      # tamaño de trabajo
    rostro = cuadro[100:260, 200:328].copy()        # 128 x 160

    print("%-28s %-22s %-34s %-12s %8s %8s"
          % ("Algoritmo propio", "Referencia", "Medida", "Resultado", "ms prop", "ms cv2"))
    print("-" * 118)

    # --- Suavizado binomial ---------------------------------------------------
    # Con tamaño 5 y sigma 0, GaussianBlur usa el núcleo (1, 4, 6, 4, 1) / 16.
    diferencia = np.abs(suavizar_binomial(cuadro) - cv2.GaussianBlur(cuadro, (5, 5), 0)).max()
    renglon("suavizar_binomial", "cv2.GaussianBlur", "dif. máxima (niveles de gris)", "%.5f" % diferencia,
            milisegundos(lambda: suavizar_binomial(cuadro)),
            milisegundos(lambda: cv2.GaussianBlur(cuadro, (5, 5), 0)))

    # --- Gradientes -----------------------------------------------------------
    diferencia = np.abs(gradiente_vertical(cuadro) - cv2.Sobel(cuadro, cv2.CV_32F, 0, 1, ksize=3)).max()
    renglon("gradiente_vertical", "cv2.Sobel (dy)", "dif. máxima", "%.5f" % diferencia,
            milisegundos(lambda: gradiente_vertical(cuadro)),
            milisegundos(lambda: cv2.Sobel(cuadro, cv2.CV_32F, 0, 1, ksize=3)))

    diferencia = np.abs(gradiente_horizontal(cuadro) - cv2.Sobel(cuadro, cv2.CV_32F, 1, 0, ksize=3)).max()
    renglon("gradiente_horizontal", "cv2.Sobel (dx)", "dif. máxima", "%.5f" % diferencia,
            milisegundos(lambda: gradiente_horizontal(cuadro)),
            milisegundos(lambda: cv2.Sobel(cuadro, cv2.CV_32F, 1, 0, ksize=3)))

    # --- Pirámide ---------------------------------------------------------------
    diferencia = np.abs(reducir(cuadro) - cv2.pyrDown(cuadro)).max()
    renglon("reducir (pirámide)", "cv2.pyrDown", "dif. máxima (niveles de gris)", "%.5f" % diferencia,
            milisegundos(lambda: piramide_gaussiana(cuadro, 3)),
            milisegundos(lambda: cv2.pyrDown(cv2.pyrDown(cuadro))))

    # --- Especificación de histograma ---------------------------------------------
    # Caso 1: referencia uniforme. Especificar contra un histograma uniforme
    # es ecualizar, así que debe coincidir con equalizeHist.
    rostro_entero = np.rint(rostro).astype(np.uint8)
    uniforme = np.arange(1, 257) / 256
    diferencia = np.abs(especificar_histograma(rostro, uniforme) - cv2.equalizeHist(rostro_entero)).max()
    renglon("especificar_histograma", "cv2.equalizeHist", "dif. máxima (niveles de gris)", "%.0f" % diferencia,
            milisegundos(lambda: especificar_histograma(rostro, uniforme)),
            milisegundos(lambda: cv2.equalizeHist(rostro_entero)))

    # Caso 2: el uso real. Una versión oscurecida del rostro se lleva al
    # histograma del rostro original, y se comparan los acumulados.
    oscuro = np.clip(rostro * 0.6 + 10, 0, 255)
    acumulado_ref = histograma_acumulado(rostro)
    antes = np.abs(histograma_acumulado(oscuro) - acumulado_ref).max()
    corregido = especificar_histograma(oscuro, acumulado_ref)
    despues = np.abs(histograma_acumulado(corregido) - acumulado_ref).max()
    renglon("especificar_histograma", "acumulado objetivo", "dif. entre acumulados, antes -> después",
            "%.3f -> %.3f" % (antes, despues), 0.0, 0.0)

    # --- Correlación normalizada ----------------------------------------------------
    chica = piramide_gaussiana(cuadro, 3)[2]                 # 160 x 90
    plantilla = chica[30:68, 70:100].copy()                  # 30 x 38
    ventana = chica[22:22 + 38 + 16, 62:62 + 30 + 16]        # deja 17 x 17 posiciones
    mapa = correlacion_normalizada(chica, plantilla)
    referencia = cv2.matchTemplate(chica, plantilla, cv2.TM_CCOEFF_NORMED)
    y, x, _ = posicion_del_maximo(mapa)
    _, _, _, (x_cv, y_cv) = cv2.minMaxLoc(referencia)
    renglon("correlacion_normalizada", "cv2.matchTemplate", "dif. máxima del mapa (escala -1 a 1)",
            "%.6f" % np.abs(mapa - referencia).max(),
            milisegundos(lambda: correlacion_normalizada(ventana, plantilla)),
            milisegundos(lambda: cv2.matchTemplate(ventana, plantilla, cv2.TM_CCOEFF_NORMED)))
    renglon("correlacion_normalizada", "cv2.matchTemplate", "posición del máximo (x, y)",
            "%s / %s" % ((x, y), (x_cv, y_cv)), 0.0, 0.0)

    # --- Correlación de fase ---------------------------------------------------------
    grande = textura(300, 300)
    anterior = grande[100:260, 100:228]                      # 128 x 160
    ventana_cv = cv2.createHanningWindow((128, 160), cv2.CV_64F)
    peor_propio, peor_cv = 0.0, 0.0
    for dx, dy in [(5, 3), (-7, 2), (0, 0), (12, -9), (1, -1)]:
        # El contenido de "actual" está movido dx a la derecha y dy hacia abajo.
        actual = grande[100 - dy:260 - dy, 100 - dx:228 - dx]
        dx_p, dy_p, _ = correlacion_de_fase(anterior, actual)
        (dx_cv, dy_cv), _ = cv2.phaseCorrelate(anterior.astype(np.float64),
                                               actual.astype(np.float64), ventana_cv)
        peor_propio = max(peor_propio, abs(dx_p - dx), abs(dy_p - dy))
        peor_cv = max(peor_cv, abs(dx_p - dx_cv), abs(dy_p - dy_cv))
    actual = grande[97:257, 95:223]
    renglon("correlacion_de_fase", "desplazamiento conocido", "error máximo (pixeles)", "%.0f" % peor_propio,
            milisegundos(lambda: correlacion_de_fase(anterior, actual)),
            milisegundos(lambda: cv2.phaseCorrelate(anterior.astype(np.float64),
                                                    actual.astype(np.float64), ventana_cv)))
    renglon("correlacion_de_fase", "cv2.phaseCorrelate", "dif. máxima (pixeles)", "%.2f" % peor_cv, 0.0, 0.0)

    # --- Mapeo inverso -------------------------------------------------------------------
    peor = 0.0
    for caja in [(200.0, 100.0, 96.0, 120.0), (210.3, 95.7, 150.0, 190.0), (50.0, 40.0, 128.0, 160.0)]:
        x0, y0, ancho, alto = caja
        ex, ey = ancho / 128, alto / 160
        # La misma transformación, escrita como matriz para warpAffine.
        matriz = np.array([[ex, 0, x0 + 0.5 * ex - 0.5],
                           [0, ey, y0 + 0.5 * ey - 0.5]], dtype=np.float64)
        referencia = cv2.warpAffine(cuadro, matriz, (128, 160),
                                    flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                    borderMode=cv2.BORDER_REPLICATE)
        peor = max(peor, np.abs(recortar_y_escalar(cuadro, caja, 128, 160) - referencia).max())
    caja = (210.3, 95.7, 150.0, 190.0)
    renglon("recortar_y_escalar", "cv2.warpAffine", "dif. máxima (niveles de gris)", "%.5f" % peor,
            milisegundos(lambda: recortar_y_escalar(cuadro, caja, 128, 160)),
            milisegundos(lambda: cv2.warpAffine(cuadro, matriz, (128, 160),
                                                flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                                borderMode=cv2.BORDER_REPLICATE)))

    print()
    print("Los tiempos en 0.00 son renglones que solo reportan una segunda medida.")
    print("Los tiempos dependen de la computadora. Hay que repetirlos en el equipo de la demo.")


if __name__ == "__main__":
    principal()
