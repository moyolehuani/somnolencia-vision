"""
Lo que se dibuja en pantalla.

dibujar() arma la imagen principal: a la izquierda el video con la caja
del rostro y la alerta, y a la derecha un tablero con las mediciones, los
estados, PERCLOS y los contadores.

vista_de_depuracion() arma una segunda imagen con el rostro normalizado y
las franjas donde se miden los ojos y la boca. Sirve para explicar de
dónde sale cada número.

Los textos van sin acentos porque las letras de OpenCV no los tienen.
"""

import cv2
import numpy as np

from somnolencia import config

ANCHO_TABLERO = 300
LETRA = cv2.FONT_HERSHEY_SIMPLEX

# Colores en orden azul, verde, rojo, que es como los usa OpenCV.
BLANCO = (235, 235, 235)
GRIS = (150, 150, 150)
VERDE = (90, 200, 90)
AMARILLO = (60, 220, 240)
NARANJA = (40, 150, 255)
ROJO = (60, 60, 235)
COLOR_DE_ALERTA = {"ninguna": VERDE, "aviso": AMARILLO, "alerta": NARANJA, "critica": ROJO}


def _texto(img, texto, x, y, color=BLANCO, tamano=0.45):
    cv2.putText(img, texto, (x, y), LETRA, tamano, color, 1, cv2.LINE_AA)


def _barra(img, y, nombre, valor, estado, umbrales):
    """Renglón del tablero: nombre, barra de 0 a 1 con sus umbrales, y estado."""
    x0, ancho, alto = 78, 120, 10
    _texto(img, nombre, 10, y + 9)
    cv2.rectangle(img, (x0, y), (x0 + ancho, y + alto), GRIS, 1)
    if valor is not None:
        cv2.rectangle(img, (x0, y), (x0 + int(ancho * valor), y + alto), BLANCO, -1)
    for umbral in umbrales:
        x = x0 + int(ancho * umbral)
        cv2.line(img, (x, y - 3), (x, y + alto + 3), AMARILLO, 1)
    _texto(img, estado, x0 + ancho + 8, y + 9, GRIS if estado == "SIN_DATO" else BLANCO, 0.4)


def dibujar(gris, resumen, fps=None):
    """Entrega la imagen a color con el video anotado y el tablero."""
    alto, ancho = gris.shape
    video = cv2.cvtColor(np.clip(gris, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    tablero = np.full((alto, ANCHO_TABLERO, 3), 30, dtype=np.uint8)

    # --- Video: caja del rostro ------------------------------------------------
    x, y, w, h = resumen["caja"]
    de_frente = resumen["valor_cabeza"] >= config.CABEZA_UMBRAL_DISTRAIDO
    cv2.rectangle(video, (x, y), (x + w, y + h), VERDE if de_frente else ROJO, 2)

    # --- Durante la calibración solo se muestra la instrucción -------------------
    if resumen["fase"] == "calibrando":
        cv2.rectangle(video, (0, 0), (ancho, 30), (60, 60, 60), -1)
        _texto(video, "CALIBRANDO: " + resumen["instruccion"], 10, 20, BLANCO, 0.55)
        _texto(tablero, "Calibrando...", 10, 24, BLANCO, 0.55)
        return np.hstack([video, tablero])

    # --- Video: alerta -------------------------------------------------------------
    alerta = resumen["alerta"]
    if alerta != "ninguna":
        cv2.rectangle(video, (0, 0), (ancho, 30), COLOR_DE_ALERTA[alerta], -1)
        _texto(video, "%s: %s" % (alerta.upper(), resumen["motivo_alerta"]), 10, 21, (20, 20, 20), 0.6)

    # --- Tablero: mediciones y estados ------------------------------------------------
    _barra(tablero, 14, "Ojos", resumen["valor_ojos"], resumen["estado_ojos"],
           (config.OJOS_UMBRAL_CIERRE, config.OJOS_UMBRAL_REAPERTURA))
    _barra(tablero, 38, "Boca", resumen["valor_boca"], resumen["estado_boca"],
           (config.BOCA_UMBRAL_CIERRE, config.BOCA_UMBRAL_APERTURA))
    _barra(tablero, 62, "Cabeza", resumen["valor_cabeza"], resumen["estado_cabeza"],
           (config.CABEZA_UMBRAL_DISTRAIDO, config.CABEZA_UMBRAL_ATENTO))

    # --- Tablero: PERCLOS -----------------------------------------------------------------
    if resumen["perclos"] is None:
        _texto(tablero, "PERCLOS 30 s: %s" % resumen["nivel_perclos"], 10, 104, GRIS)
    else:
        color = {"normal": VERDE, "alerta": AMARILLO, "fatiga": NARANJA, "somnolencia": ROJO}[resumen["nivel_perclos"]]
        _texto(tablero, "PERCLOS 30 s: %4.1f%%  %s" % (100 * resumen["perclos"], resumen["nivel_perclos"]),
               10, 104, color)

    # --- Tablero: contadores -------------------------------------------------------------------
    c = resumen["contadores"]
    _texto(tablero, "Parpadeos", 10, 136, GRIS)
    _texto(tablero, "normal %d   lento %d   microsueno %d"
           % (c.get("parpadeo:normal", 0), c.get("parpadeo:lento", 0), c.get("parpadeo:microsueno", 0)), 10, 154)
    _texto(tablero, "Bostezos", 10, 182, GRIS)
    _texto(tablero, "%d" % c.get("bostezo:bostezo", 0), 90, 182)
    _texto(tablero, "Distraccion por banda", 10, 210, GRIS)
    _texto(tablero, "0.5: %d   1.0: %d   1.5: %d   2.0: %d"
           % tuple(c.get("distraccion:%s" % banda, 0) for banda in config.BANDAS_DISTRACCION_S), 10, 228)

    # --- Tablero: lo que está en curso -------------------------------------------------------------
    _texto(tablero, "En curso", 10, 260, GRIS)
    en_curso = []
    if resumen["cierre_en_curso_s"] > 0:
        en_curso.append("ojos cerrados %.1f s" % resumen["cierre_en_curso_s"])
    if resumen["bostezo_en_curso_s"] > 0:
        en_curso.append("boca abierta %.1f s" % resumen["bostezo_en_curso_s"])
    if resumen["distraccion_en_curso_s"] > 0:
        en_curso.append("sin mirar al frente %.1f s" % resumen["distraccion_en_curso_s"])
    for numero, linea in enumerate(en_curso or ["nada"]):
        _texto(tablero, linea, 10, 278 + 18 * numero)

    pie = "t = %.1f s" % resumen["t"]
    if fps is not None:
        pie += "    %.0f cuadros/s" % fps
    _texto(tablero, pie, 10, alto - 12, GRIS, 0.4)
    if resumen["aviso"]:
        _texto(tablero, resumen["aviso"][:44], 10, alto - 30, AMARILLO, 0.35)

    return np.hstack([video, tablero])


def vista_de_depuracion(resumen):
    """
    Imagen con el rostro normalizado al doble de tamaño y las franjas donde
    se miden los ojos (verde) y la boca (amarillo). Entrega None si en este
    cuadro el rostro no estaba de frente.
    """
    rostro = resumen.get("rostro")
    if rostro is None:
        return None
    alto, ancho = rostro.shape
    img = cv2.cvtColor(np.clip(rostro, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    img = cv2.resize(img, (2 * ancho, 2 * alto), interpolation=cv2.INTER_NEAREST)

    # Franja de ojos: dos mitades. La línea punteada marca hasta dónde se
    # descarta la parte de la ceja.
    r0, r1 = int(config.OJOS_FILA_INICIAL * alto), int(config.OJOS_FILA_FINAL * alto)
    sin_ceja = r0 + int(config.OJOS_FRACCION_SIN_CEJA * (r1 - r0))
    cv2.rectangle(img, (0, 2 * r0), (ancho - 1, 2 * r1), VERDE, 1)
    cv2.rectangle(img, (ancho, 2 * r0), (2 * ancho - 1, 2 * r1), VERDE, 1)
    for x in range(0, 2 * ancho, 8):
        cv2.line(img, (x, 2 * sin_ceja), (x + 3, 2 * sin_ceja), VERDE, 1)

    # Franja de boca.
    b0, b1 = int(config.BOCA_FILA_INICIAL * alto), int(config.BOCA_FILA_FINAL * alto)
    c0, c1 = int(config.BOCA_COLUMNA_INICIAL * ancho), int(config.BOCA_COLUMNA_FINAL * ancho)
    cv2.rectangle(img, (2 * c0, 2 * b0), (2 * c1, 2 * b1 - 1), AMARILLO, 1)

    if resumen.get("razon_ojos") is not None:
        _texto(img, "razon de bordes: %.2f" % resumen["razon_ojos"], 6, 16, VERDE, 0.45)
    return img
