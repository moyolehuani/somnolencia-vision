"""
Programa principal.

Ejemplos, desde la raíz del repositorio:

    python -m somnolencia.principal --fuente escena
    python -m somnolencia.principal --fuente 0
    python -m somnolencia.principal --fuente datos/videos/P01_G2_01.mp4
    python -m somnolencia.principal --fuente video.mp4 --sin-ventana --caja 265,111,110,138

Fuentes:
    escena     una cara dibujada que sigue un guion. No necesita cámara.
    0, 1, ...  una cámara.
    una ruta   un archivo de video.

Opciones:
    --caja x,y,ancho,alto   caja del rostro en el primer cuadro, en pixeles
                            del tamaño de trabajo (640x360). Si no se da,
                            con ventana se pide marcarla y sin ventana se
                            usa el recuadro central.
    --sin-calibracion       empieza a vigilar de inmediato, con las
                            referencias generales de ojos.
    --sin-ventana           no abre ventanas. Sirve para evaluar videos.
    --mediciones            guarda además un CSV con una fila por cuadro: las
                            mediciones, los estados, PERCLOS y la alerta.
    --salida carpeta        dónde se guarda la bitácora (por omisión, salidas).

Teclas con ventana:  q salir   r reiniciar contadores   d vista de depuración
                     c recalibrar (solo con cámara)

Este archivo no contiene algoritmos. Solo conecta la captura, el sistema,
la interfaz y la bitácora.
"""

import argparse
import time

import cv2

from somnolencia import config
from somnolencia.percepcion.captura import Captura
from somnolencia.sistema import Sistema
from somnolencia.temporal.capa import CapaTemporal
from somnolencia.interfaz.bitacora import Bitacora, BitacoraDeMediciones
from somnolencia.interfaz import overlay, controles

VENTANA = "Somnolencia y distraccion"
VENTANA_DEPURACION = "Depuracion"


def recuadro_central():
    """Caja centrada donde la persona coloca la cara al calibrar."""
    x = (config.TRABAJO_ANCHO - config.RECUADRO_ANCHO) // 2
    y = (config.TRABAJO_ALTO - config.RECUADRO_ALTO) // 2
    return (x, y, config.RECUADRO_ANCHO, config.RECUADRO_ALTO)


def a_color(gris):
    return cv2.cvtColor(gris.clip(0, 255).astype("uint8"), cv2.COLOR_GRAY2BGR)


def esperar_cara_en_recuadro(captura):
    """
    Con cámara: muestra el recuadro hasta que la persona pulsa la barra
    espaciadora. Entrega (gris, t) del cuadro en que se pulsó, o None si
    se pulsó q.
    """
    x, y, w, h = recuadro_central()
    while True:
        lectura = captura.leer()
        if lectura is None:
            return None
        gris, t = lectura
        img = a_color(gris)
        cv2.rectangle(img, (x, y), (x + w, y + h), (90, 200, 90), 2)
        cv2.putText(img, "Coloca la cara en el recuadro y pulsa ESPACIO", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (235, 235, 235), 1, cv2.LINE_AA)
        cv2.imshow(VENTANA, img)
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord(" "):
            return gris, t
        if tecla == ord("q"):
            return None


def elegir_caja(argumentos, captura, gris, con_ventana):
    """Decide la caja del rostro para el primer cuadro."""
    if argumentos.caja:
        return tuple(int(v) for v in argumentos.caja.split(","))
    if captura.es_escena:
        from somnolencia import escena_sintetica
        return escena_sintetica.caja_inicial()
    if con_ventana and not captura.es_camara:
        # Con un archivo de video: se marca el rostro con el ratón.
        print("Marca el rostro con el ratón y pulsa ENTER.")
        caja = cv2.selectROI(VENTANA, a_color(gris), showCrosshair=False)
        if caja[2] > 0 and caja[3] > 0:
            return tuple(int(v) for v in caja)
    return recuadro_central()


def principal():
    lector = argparse.ArgumentParser(description="Detección de somnolencia y distracción")
    lector.add_argument("--fuente", default="0")
    lector.add_argument("--caja", default="")
    lector.add_argument("--sin-calibracion", action="store_true")
    lector.add_argument("--sin-ventana", action="store_true")
    lector.add_argument("--mediciones", action="store_true")
    lector.add_argument("--salida", default="salidas")
    argumentos = lector.parse_args()

    con_ventana = not argumentos.sin_ventana
    captura = Captura(argumentos.fuente)
    bitacora = Bitacora(argumentos.salida, argumentos.fuente)
    mediciones = None
    if argumentos.mediciones:
        mediciones = BitacoraDeMediciones(argumentos.salida, bitacora.marca)
    sistema = Sistema()
    ver_depuracion = False

    if con_ventana:
        cv2.namedWindow(VENTANA)
        controles.crear_deslizadores()      # en su propia ventana, con leyenda

    # --- Primer cuadro: se fija el rostro de referencia ---------------------------
    if con_ventana and captura.es_camara and not argumentos.caja:
        lectura = esperar_cara_en_recuadro(captura)
    else:
        lectura = captura.leer()
    if lectura is None:
        print("No hay cuadros que procesar.")
        return
    gris, t = lectura
    sistema.iniciar(gris, elegir_caja(argumentos, captura, gris, con_ventana), t,
                    con_calibracion=not argumentos.sin_calibracion)

    # --- Ciclo principal --------------------------------------------------------------
    cuadros, tiempo_de_proceso = 0, 0.0
    reloj_inicio, t_primero = time.monotonic(), t
    while lectura is not None:
        gris, t = lectura

        inicio = time.perf_counter()
        resumen = sistema.procesar(gris, t)
        tiempo_de_proceso += time.perf_counter() - inicio
        cuadros += 1

        bitacora.guardar(resumen.get("eventos_nuevos", []))
        if mediciones is not None:
            mediciones.guardar(resumen)

        if con_ventana:
            controles.aplicar_deslizadores(sistema.capa)
            fps = cuadros / max(time.monotonic() - reloj_inicio, 1e-6)
            cv2.imshow(VENTANA, overlay.dibujar(gris, resumen, fps))
            if ver_depuracion:
                vista = overlay.vista_de_depuracion(resumen)
                if vista is not None:
                    cv2.imshow(VENTANA_DEPURACION, vista)

            # Con un video o con la escena se espera lo necesario para que
            # avance a su velocidad real. Con cámara no hace falta.
            espera_ms = 1
            if not captura.es_camara:
                adelanto = (t - t_primero) - (time.monotonic() - reloj_inicio)
                espera_ms = max(1, int(1000 * adelanto))
            tecla = cv2.waitKey(espera_ms) & 0xFF

            if tecla == ord("q"):
                break
            if tecla == ord("r"):
                sistema.capa = CapaTemporal()       # contadores y PERCLOS en cero
            if tecla == ord("d"):
                ver_depuracion = not ver_depuracion
                if not ver_depuracion:
                    cv2.destroyWindow(VENTANA_DEPURACION)
            if tecla == ord("c") and captura.es_camara:
                lectura = esperar_cara_en_recuadro(captura)
                if lectura is None:
                    break
                sistema = Sistema()
                sistema.iniciar(lectura[0], recuadro_central(), lectura[1],
                                con_calibracion=not argumentos.sin_calibracion)
                continue

        lectura = captura.leer()

    # --- Cierre -----------------------------------------------------------------------------
    bitacora.guardar(sistema.terminar(t))
    bitacora.cerrar()
    if mediciones is not None:
        mediciones.cerrar()
    captura.cerrar()
    if con_ventana:
        cv2.destroyAllWindows()

    print()
    print("Cuadros procesados: %d" % cuadros)
    print("Tiempo de proceso por cuadro: %.1f ms" % (1000 * tiempo_de_proceso / max(cuadros, 1)))
    if sistema.calibracion.aviso:
        print("Aviso:", sistema.calibracion.aviso)
    print("Eventos:")
    contadores = sistema.capa.rastreador.contadores
    for clave in sorted(contadores):
        print("  %-22s %d" % (clave, contadores[clave]))
    if not contadores:
        print("  ninguno")
    print("Bitácora guardada en", bitacora.ruta)
    if mediciones is not None:
        print("Mediciones guardadas en", mediciones.ruta)


if __name__ == "__main__":
    principal()
