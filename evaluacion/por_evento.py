"""
Evaluación por evento: compara lo que detectó el sistema contra lo que
anotó una persona en el mismo video.

Uso, desde la raíz del repositorio:

    python -m evaluacion.por_evento anotaciones.csv bitacora.csv
    python -m evaluacion.por_evento anotaciones.csv bitacora.csv mediciones.csv

    anotaciones.csv   eventos reales del video, anotados a mano
                      (formato en datos/README.md)
    bitacora.csv      eventos que detectó el sistema
                      (lo genera somnolencia.principal)
    mediciones.csv    opcional. Mediciones cuadro por cuadro, para comparar
                      PERCLOS (lo genera somnolencia.principal --mediciones)

Qué calcula:

  - Por tipo de evento: cuántos se anotaron, cuántos se detectaron,
    precisión, recall y error medio de duración.
  - Confusión entre categorías de parpadeo (normal, lento, microsueño).
  - Con el archivo de mediciones: error de PERCLOS y en qué fracción del
    tiempo coincide su nivel.

Cómo se decide que un evento detectado corresponde a uno anotado: deben
ser del mismo tipo y sus intervalos de tiempo deben traslaparse. Cada
evento anotado se empareja con uno detectado a lo más, y al revés.

Definiciones:
    precisión   de los eventos que detectó el sistema, qué fracción era real
    recall      de los eventos reales, qué fracción detectó el sistema
"""

import csv
import sys

from somnolencia import config
from somnolencia.tipos import Evento, PARPADEO, BOSTEZO, DISTRACCION
from somnolencia.temporal.eventos import clasificar_parpadeo, banda_de_distraccion
from somnolencia.temporal.perclos import calcular_perclos

TIPOS = (PARPADEO, BOSTEZO, DISTRACCION)
CATEGORIAS_DE_PARPADEO = ("normal", "lento", "microsueno")


# ----- Lectura ------------------------------------------------------------------

def categoria_de(tipo, duracion):
    """
    Categoría de un evento según su duración, con las mismas reglas que usa
    el sistema. Entrega None si el evento es tan corto que no se cuenta
    (una distracción menor a la primera banda).
    """
    if tipo == PARPADEO:
        return clasificar_parpadeo(duracion)
    if tipo == DISTRACCION:
        banda = banda_de_distraccion(duracion)
        return None if banda is None else str(banda)
    return "bostezo"


def crear_evento(tipo, inicio, fin):
    """Arma un Evento con su duración y su categoría. Entrega None si no se cuenta."""
    duracion = round(fin - inicio, 3)
    categoria = categoria_de(tipo, duracion)
    if categoria is None:
        return None
    return Evento(tipo, inicio, fin, duracion, categoria)


def leer_eventos(ruta):
    """
    Lee un archivo de anotaciones o una bitácora. Los dos tienen las
    columnas tipo, inicio_s y fin_s. La categoría se vuelve a calcular a
    partir de la duración, para que anotaciones y bitácora usen la misma regla.
    """
    eventos = []
    with open(ruta, newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            evento = crear_evento(fila["tipo"].strip(), float(fila["inicio_s"]), float(fila["fin_s"]))
            if evento is not None:
                eventos.append(evento)
    return eventos


# ----- Emparejamiento ---------------------------------------------------------------

def traslape(a, b):
    """Segundos en que dos eventos ocurren al mismo tiempo (0 si no se tocan)."""
    return max(0.0, min(a.fin, b.fin) - max(a.inicio, b.inicio))


def emparejar(anotados, detectados):
    """
    Empareja eventos anotados con eventos detectados.

    Se listan todas las parejas posibles (mismo tipo y con traslape), se
    ordenan de mayor a menor traslape y se van aceptando en ese orden,
    siempre que ninguno de los dos eventos esté ya emparejado.

    Entrega tres listas:
        parejas        (anotado, detectado)
        sin_detectar   anotados que nadie detectó   (falsos negativos)
        de_mas         detectados que no eran reales (falsos positivos)
    """
    posibles = []
    for i, anotado in enumerate(anotados):
        for j, detectado in enumerate(detectados):
            if anotado.tipo == detectado.tipo:
                segundos = traslape(anotado, detectado)
                if segundos > 0:
                    posibles.append((segundos, i, j))
    posibles.sort(reverse=True)

    anotados_usados, detectados_usados, parejas = set(), set(), []
    for _, i, j in posibles:
        if i not in anotados_usados and j not in detectados_usados:
            anotados_usados.add(i)
            detectados_usados.add(j)
            parejas.append((anotados[i], detectados[j]))

    sin_detectar = [e for i, e in enumerate(anotados) if i not in anotados_usados]
    de_mas = [e for j, e in enumerate(detectados) if j not in detectados_usados]
    return parejas, sin_detectar, de_mas


# ----- Métricas ------------------------------------------------------------------------

def metricas_por_tipo(parejas, sin_detectar, de_mas):
    """
    Entrega un diccionario por tipo de evento con: anotados, detectados,
    aciertos, precision, recall, error_de_duracion (promedio del valor
    absoluto, en segundos) y misma_categoria (fracción de aciertos en que
    la categoría también coincide). Lo que no se puede calcular queda en None.
    """
    resultado = {}
    for tipo in TIPOS:
        del_tipo = [(a, d) for a, d in parejas if a.tipo == tipo]
        aciertos = len(del_tipo)
        anotados = aciertos + sum(1 for e in sin_detectar if e.tipo == tipo)
        detectados = aciertos + sum(1 for e in de_mas if e.tipo == tipo)
        errores = [abs(d.duracion - a.duracion) for a, d in del_tipo]
        iguales = [a.categoria == d.categoria for a, d in del_tipo]
        resultado[tipo] = {
            "anotados": anotados,
            "detectados": detectados,
            "aciertos": aciertos,
            "precision": aciertos / detectados if detectados else None,
            "recall": aciertos / anotados if anotados else None,
            "error_de_duracion": sum(errores) / aciertos if aciertos else None,
            "misma_categoria": sum(iguales) / aciertos if aciertos else None,
        }
    return resultado


def confusion_de_parpadeos(parejas):
    """
    Tabla que cuenta, para los parpadeos emparejados, qué categoría se
    anotó y cuál detectó el sistema. Se consulta como
    tabla[categoria_anotada][categoria_detectada].
    """
    tabla = {a: {d: 0 for d in CATEGORIAS_DE_PARPADEO} for a in CATEGORIAS_DE_PARPADEO}
    for anotado, detectado in parejas:
        if anotado.tipo == PARPADEO:
            tabla[anotado.categoria][detectado.categoria] += 1
    return tabla


# ----- PERCLOS ---------------------------------------------------------------------------

def comparar_perclos(ruta_de_mediciones, anotados):
    """
    Compara el PERCLOS que reportó el sistema en cada cuadro con el que
    sale de las anotaciones en ese mismo instante.

    El PERCLOS de referencia se calcula con la misma función que usa el
    sistema (calcular_perclos), pero a partir de las anotaciones:

      - Los parpadeos anotados son los cierres de ojos.
      - Las distracciones anotadas son tramos sin dato. Mientras la persona
        no mira al frente no se le ven los ojos, y ese tiempo no cuenta
        para PERCLOS. Es la misma regla que aplica el sistema.

    Entrega un diccionario con:
        cuadros            cuántos cuadros se compararon
        error_medio        promedio de |sistema - referencia|, como fracción
        error_maximo       el mayor de esos errores
        mismo_nivel        fracción de cuadros en que coincide el nivel
    o None si no hay cuadros que comparar.
    """
    cierres = [(e.inicio, e.fin) for e in anotados if e.tipo == PARPADEO]
    giros = [(e.inicio, e.fin) for e in anotados if e.tipo == DISTRACCION]
    t_inicio = None
    errores, niveles_iguales = [], 0

    with open(ruta_de_mediciones, newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["fase"] != "vigilando":
                continue
            t = float(fila["t"])
            if t_inicio is None:
                t_inicio = t            # la vigilancia empieza al terminar la calibración
            if fila["perclos"] == "":
                continue                # el sistema todavía no reportaba PERCLOS
            # Cierres y giros anotados que ya empezaron. El que sigue abierto
            # cuenta hasta t.
            cierres_hasta_t = [(inicio, min(fin, t)) for inicio, fin in cierres if inicio < t]
            giros_hasta_t = [(inicio, min(fin, t)) for inicio, fin in giros if inicio < t]
            referencia, nivel_ref = calcular_perclos(t, t_inicio, cierres_hasta_t, giros_hasta_t)
            if referencia is None:
                continue
            errores.append(abs(float(fila["perclos"]) - referencia))
            niveles_iguales += fila["nivel_perclos"] == nivel_ref

    if not errores:
        return None
    return {
        "cuadros": len(errores),
        "error_medio": sum(errores) / len(errores),
        "error_maximo": max(errores),
        "mismo_nivel": niveles_iguales / len(errores),
    }


# ----- Reporte -------------------------------------------------------------------------------

def _texto(valor, formato="%.2f"):
    return "-" if valor is None else formato % valor


def imprimir_reporte(anotados, detectados, ruta_de_mediciones=None):
    parejas, sin_detectar, de_mas = emparejar(anotados, detectados)

    print("%-12s %9s %11s %9s %10s %7s %14s %16s"
          % ("Tipo", "Anotados", "Detectados", "Aciertos", "Precisión", "Recall",
             "Error dur. (s)", "Misma categoría"))
    for tipo, m in metricas_por_tipo(parejas, sin_detectar, de_mas).items():
        print("%-12s %9d %11d %9d %10s %7s %14s %16s"
              % (tipo, m["anotados"], m["detectados"], m["aciertos"],
                 _texto(m["precision"]), _texto(m["recall"]),
                 _texto(m["error_de_duracion"], "%.3f"), _texto(m["misma_categoria"])))

    print()
    print("Parpadeos: categoría anotada (renglón) contra detectada (columna)")
    tabla = confusion_de_parpadeos(parejas)
    print("%-12s %8s %8s %12s" % (("",) + CATEGORIAS_DE_PARPADEO))
    for anotada in CATEGORIAS_DE_PARPADEO:
        print("%-12s %8d %8d %12d" % ((anotada,) + tuple(tabla[anotada][d] for d in CATEGORIAS_DE_PARPADEO)))

    if sin_detectar:
        print()
        print("Anotados que el sistema no detectó:")
        for e in sin_detectar:
            print("  %-12s de %.2f a %.2f s (%s)" % (e.tipo, e.inicio, e.fin, e.categoria))
    if de_mas:
        print()
        print("Detectados que no estaban anotados:")
        for e in de_mas:
            print("  %-12s de %.2f a %.2f s (%s)" % (e.tipo, e.inicio, e.fin, e.categoria))

    if ruta_de_mediciones:
        print()
        resultado = comparar_perclos(ruta_de_mediciones, anotados)
        if resultado is None:
            print("PERCLOS: no hubo cuadros que comparar.")
        else:
            print("PERCLOS, sobre %d cuadros:" % resultado["cuadros"])
            print("  error medio:   %.1f puntos porcentuales" % (100 * resultado["error_medio"]))
            print("  error máximo:  %.1f puntos porcentuales" % (100 * resultado["error_maximo"]))
            print("  mismo nivel:   %.0f%% del tiempo" % (100 * resultado["mismo_nivel"]))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python -m evaluacion.por_evento anotaciones.csv bitacora.csv [mediciones.csv]")
        sys.exit(1)
    imprimir_reporte(leer_eventos(sys.argv[1]), leer_eventos(sys.argv[2]),
                     sys.argv[3] if len(sys.argv) > 3 else None)
