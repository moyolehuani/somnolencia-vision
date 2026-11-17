"""
Evaluación por cuadro de la medida de ojos, con imágenes sueltas.

Recorre las carpetas Open y Closed del dataset de Kaggle, calcula la razón
de bordes de cada imagen y mide qué tan bien separa ojos abiertos de ojos
cerrados con un umbral fijo.

Uso, desde la raíz del repositorio:

    python -m evaluacion.por_cuadro datos/kaggle/drowsiness-dataset/train

Para no hacer trampa, las imágenes se dividen en dos mitades fijas (por
orden de nombre: una sí y una no). El umbral se elige con una mitad y los
resultados se reportan con la otra. Después se repite al revés.

Aquí sí se usa cv2.resize para llevar cada recorte a 64 pixeles de ancho.
Esta carpeta no es parte del sistema, así que no rompe la regla de los
algoritmos propios.
"""

import csv
import os
import sys

import cv2
import numpy as np

from somnolencia import config
from somnolencia.percepcion.ojos import razon_de_un_ojo


def cargar_recorte(ruta):
    """Lee una imagen de un ojo y la lleva a grises y a 64 pixeles de ancho."""
    imagen = cv2.imread(ruta)
    if imagen is None:
        return None
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY).astype(np.float32)
    ancho = config.OJOS_ANCHO_DE_RECORTE
    alto = max(32, int(round(gris.shape[0] * ancho / gris.shape[1])))
    return cv2.resize(gris, (ancho, alto), interpolation=cv2.INTER_AREA)


def medir_carpeta(carpeta):
    """Entrega la lista de (nombre, razón) de todas las imágenes de una carpeta."""
    resultados = []
    for nombre in sorted(os.listdir(carpeta)):
        recorte = cargar_recorte(os.path.join(carpeta, nombre))
        if recorte is not None:
            resultados.append((nombre, razon_de_un_ojo(recorte)))
    return resultados


def mejor_umbral(abiertos, cerrados):
    """
    Umbral que mejor separa los dos grupos: abierto si la razón lo supera.
    Se prueba cada punto medio entre valores vecinos y se elige el que da
    el mayor promedio de aciertos en abiertos y aciertos en cerrados.
    """
    valores = np.unique(np.concatenate([abiertos, cerrados]))
    mejor_acierto, mejor = -1.0, None
    for i in range(len(valores) - 1):
        umbral = (valores[i] + valores[i + 1]) / 2
        acierto = ((abiertos > umbral).mean() + (cerrados <= umbral).mean()) / 2
        if acierto > mejor_acierto:
            mejor_acierto, mejor = acierto, umbral
    return mejor


def metricas(abiertos, cerrados, umbral):
    """Matriz de confusión y precisión, recall y F1 de la clase "cerrado"."""
    cerrados_bien = int((cerrados <= umbral).sum())    # verdaderos positivos
    cerrados_mal = int((cerrados > umbral).sum())      # falsos negativos
    abiertos_mal = int((abiertos <= umbral).sum())     # falsos positivos
    abiertos_bien = int((abiertos > umbral).sum())
    precision = cerrados_bien / max(cerrados_bien + abiertos_mal, 1)
    recall = cerrados_bien / max(cerrados_bien + cerrados_mal, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    return {
        "cerrados_bien": cerrados_bien, "cerrados_mal": cerrados_mal,
        "abiertos_bien": abiertos_bien, "abiertos_mal": abiertos_mal,
        "precision": precision, "recall": recall, "f1": f1,
    }


def principal(raiz, salida="evaluacion/resultados/por_cuadro_ojos.csv"):
    abiertos = medir_carpeta(os.path.join(raiz, "Open"))
    cerrados = medir_carpeta(os.path.join(raiz, "Closed"))
    valores_ab = np.array([razon for _, razon in abiertos])
    valores_ce = np.array([razon for _, razon in cerrados])

    print("Imágenes: %d abiertos, %d cerrados" % (len(valores_ab), len(valores_ce)))
    print("Mediana de la razón: %.3f en abiertos, %.3f en cerrados"
          % (np.median(valores_ab), np.median(valores_ce)))
    print()

    # Mitad A: posiciones pares. Mitad B: posiciones impares.
    mitades = {
        "umbral con A, reporte en B": (valores_ab[0::2], valores_ce[0::2],
                                       valores_ab[1::2], valores_ce[1::2]),
        "umbral con B, reporte en A": (valores_ab[1::2], valores_ce[1::2],
                                       valores_ab[0::2], valores_ce[0::2]),
    }
    for nombre, (ab_ajuste, ce_ajuste, ab_reporte, ce_reporte) in mitades.items():
        umbral = mejor_umbral(ab_ajuste, ce_ajuste)
        m = metricas(ab_reporte, ce_reporte, umbral)
        print(nombre)
        print("  umbral elegido: %.3f" % umbral)
        print("  cerrados: %d bien, %d mal    abiertos: %d bien, %d mal"
              % (m["cerrados_bien"], m["cerrados_mal"], m["abiertos_bien"], m["abiertos_mal"]))
        print("  precisión %.2f   recall %.2f   F1 %.2f" % (m["precision"], m["recall"], m["f1"]))
        print()

    # Se guarda la razón de cada imagen para poder revisar las que fallan.
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with open(salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["clase", "imagen", "razon"])
        for nombre, razon in abiertos:
            escritor.writerow(["Open", nombre, "%.4f" % razon])
        for nombre, razon in cerrados:
            escritor.writerow(["Closed", nombre, "%.4f" % razon])
    print("Razón de cada imagen guardada en", salida)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m evaluacion.por_cuadro <carpeta con Open y Closed>")
        sys.exit(1)
    principal(sys.argv[1])
