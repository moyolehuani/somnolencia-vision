"""
Corre el sistema completo sobre la escena sintética, una sola vez.

Procesar la escena tarda unos segundos. Varias pruebas necesitan el
resultado, así que se calcula aquí al importar este archivo y todas lo
comparten.

    SISTEMA     el objeto Sistema después de procesar toda la escena
    RESUMENES   lista de (cuadro en grises, resumen) de cada cuadro
"""

from somnolencia import escena_sintetica as escena
from somnolencia.sistema import Sistema


def correr_escena():
    sistema = Sistema()
    resumenes = []
    for t, gris in escena.generar():
        if sistema.seguidor is None:
            sistema.iniciar(gris, escena.caja_inicial(), t)
        resumenes.append((gris, sistema.procesar(gris, t)))
    sistema.terminar(t)
    return sistema, resumenes


SISTEMA, RESUMENES = correr_escena()
