"""
Controles: deslizadores para cambiar umbrales mientras el sistema corre.

Los deslizadores viven en una ventana aparte, llamada "Controles", junto
con una leyenda que explica qué hace cada uno. Así no empujan el video
hacia abajo en la ventana principal.

Cada deslizador va de 0 a 100 y representa un umbral entre 0.00 y 1.00.
Al moverlo cambia el valor en config (para que el tablero dibuje la marca
amarilla en su nuevo lugar) y en el objeto que decide el estado de esa
señal.

Los cambios duran lo que dura la sesión. No se escriben en config.py.

Los umbrales de duración del enunciado (0.5 s, 7 s, PERCLOS) no tienen
deslizador: son parte de la especificación y no se ajustan.

Sobre los nombres. En Windows, OpenCV recorta el nombre de un deslizador
cuando pasa de 10 letras y lo muestra con puntos suspensivos. Por eso los
nombres son cortos y la explicación completa va en la leyenda. Hay una
prueba automática que revisa que ningún nombre pase de 10 letras.
"""

import cv2
import numpy as np

from somnolencia import config

VENTANA_CONTROLES = "Controles"
LARGO_MAXIMO_DE_NOMBRE = 10

# (nombre corto, nombre en config, señal, atributo del actualizador, explicación)
DESLIZADORES = [
    ("Ojo cierra", "OJOS_UMBRAL_CIERRE", "ojos", "umbral_entrada",
     "los ojos cuentan como cerrados si su barra baja de este valor"),
    ("Ojo abre", "OJOS_UMBRAL_REAPERTURA", "ojos", "umbral_salida",
     "vuelven a contar como abiertos si su barra sube de este valor"),
    ("Boca abre", "BOCA_UMBRAL_APERTURA", "boca", "umbral_entrada",
     "la boca cuenta como abierta si su barra sube de este valor"),
    ("Cabeza", "CABEZA_UMBRAL_DISTRAIDO", "cabeza", "umbral_entrada",
     "cuenta como distraido si la barra de cabeza baja de este valor"),
]


def imagen_de_leyenda():
    """
    Arma la imagen con la explicación de cada deslizador y de las teclas.
    Los textos van sin acentos porque las letras de OpenCV no los tienen.
    """
    lineas = ["Cada deslizador va de 0 a 100 y equivale a un umbral de 0.00 a 1.00.", ""]
    for nombre, _, _, _, explicacion in DESLIZADORES:
        lineas.append("%-10s  %s." % (nombre, explicacion))
    lineas += [
        "",
        "Las marcas amarillas del tablero se mueven con los deslizadores.",
        "Los cambios duran solo esta sesion. No se guardan en config.py.",
        "",
        "Teclas:  q salir   r reiniciar contadores   d vista de depuracion",
        "         c recalibrar (solo con camara)",
    ]
    alto_de_linea = 20
    img = np.full((alto_de_linea * len(lineas) + 16, 640, 3), 30, dtype=np.uint8)
    for numero, linea in enumerate(lineas):
        cv2.putText(img, linea, (10, 22 + alto_de_linea * numero),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (235, 235, 235), 1, cv2.LINE_AA)
    return img


def crear_deslizadores():
    """Abre la ventana de controles con los deslizadores en su valor actual y la leyenda."""
    cv2.namedWindow(VENTANA_CONTROLES)
    for nombre, nombre_en_config, _, _, _ in DESLIZADORES:
        valor = int(round(100 * getattr(config, nombre_en_config)))
        cv2.createTrackbar(nombre, VENTANA_CONTROLES, valor, 100, lambda _: None)
    cv2.imshow(VENTANA_CONTROLES, imagen_de_leyenda())


def aplicar_deslizadores(capa):
    """Lee los deslizadores y pasa sus valores a config y a la capa temporal."""
    actualizadores = {
        "ojos": capa.actualizador_ojos,
        "boca": capa.actualizador_boca,
        "cabeza": capa.actualizador_cabeza,
    }
    for nombre, nombre_en_config, senal, atributo, _ in DESLIZADORES:
        valor = cv2.getTrackbarPos(nombre, VENTANA_CONTROLES) / 100.0
        setattr(config, nombre_en_config, valor)
        setattr(actualizadores[senal], atributo, valor)
