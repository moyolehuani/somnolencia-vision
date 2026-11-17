"""
PERCLOS: porcentaje del tiempo con los ojos cerrados en los últimos 30 s.

              tiempo cerrado que cuenta, dentro de la ventana
    PERCLOS = -----------------------------------------------
              tiempo con dato válido, dentro de la ventana

Se calcula a partir de dos listas de tramos que lleva el rastreador de
eventos: los cierres de ojos y los tramos sin dato. Cada tramo es una
pareja (inicio, fin) en segundos.

Ejemplo. La ventana va de 40 a 70 s y en ella hubo:
    un parpadeo de 45.0 a 45.3 s   dura 0.3 s, es normal, no cuenta
    un cierre de 50.0 a 52.0 s     cuenta 2.0 s
    un cierre de 60.0 a 61.5 s     cuenta 1.5 s
    sin dato de 65.0 a 67.0 s      se quita del tiempo válido
Tiempo cerrado 3.5 s, tiempo válido 30 - 2 = 28 s, PERCLOS = 3.5 / 28 = 12.5%.
"""

from somnolencia import config

# Niveles posibles.
NORMAL = "normal"
ALERTA = "alerta"
FATIGA = "fatiga"
SOMNOLENCIA = "somnolencia"
CALENTANDO = "calentando"   # todavía no hay suficientes segundos de sesión
SIN_DATO = "sin dato"       # la ventana casi no tiene datos válidos


def tiempo_dentro(inicio, fin, a, b):
    """Cuántos segundos del tramo (inicio, fin) caen dentro de la ventana (a, b)."""
    return max(0.0, min(fin, b) - max(inicio, a))


def nivel_de_perclos(valor):
    """Nivel que corresponde a un PERCLOS dado como fracción (0.125 es 12.5%)."""
    if valor >= config.PERCLOS_SOMNOLENCIA:
        return SOMNOLENCIA
    if valor >= config.PERCLOS_FATIGA:
        return FATIGA
    if valor >= config.PERCLOS_ALERTA:
        return ALERTA
    return NORMAL


def calcular_perclos(t, t_inicio, cierres, huecos):
    """
    Calcula PERCLOS en el instante t.

    t          tiempo actual, en segundos
    t_inicio   tiempo en que empezó la sesión
    cierres    lista de (inicio, fin) de los cierres de ojos, incluido el
               que siga abierto, contado hasta t
    huecos     lista de (inicio, fin) de los tramos sin dato de los ojos

    Entrega (valor, nivel). El valor es una fracción entre 0 y 1, o None
    cuando todavía no se puede calcular.
    """
    # La ventana son los últimos 30 s, o menos si la sesión es más corta.
    a = max(t_inicio, t - config.PERCLOS_VENTANA_S)
    b = t

    tiempo_cerrado = 0.0
    for inicio, fin in cierres:
        duracion = round(fin - inicio, 3)
        # Decisión D09: un parpadeo normal cuenta o no según el interruptor.
        # Un cierre más largo cuenta siempre, y cuenta completo desde su inicio.
        es_parpadeo_normal = duracion <= config.PARPADEO_NORMAL_MAX_S
        if es_parpadeo_normal and not config.PERCLOS_CUENTA_PARPADEOS_NORMALES:
            continue
        # Solo cuenta la parte del cierre que cae dentro de la ventana.
        tiempo_cerrado += tiempo_dentro(inicio, fin, a, b)

    tiempo_sin_dato = 0.0
    for inicio, fin in huecos:
        tiempo_sin_dato += tiempo_dentro(inicio, fin, a, b)

    tiempo_valido = (b - a) - tiempo_sin_dato

    # Con muy pocos segundos de datos el porcentaje no significa nada.
    if tiempo_valido < config.PERCLOS_TIEMPO_MINIMO_S:
        if (t - t_inicio) < config.PERCLOS_TIEMPO_MINIMO_S:
            return None, CALENTANDO
        return None, SIN_DATO

    # Se redondea para que 2.4 / 30 dé exactamente 0.08 y no 0.0800000001.
    valor = round(tiempo_cerrado / tiempo_valido, 4)
    return valor, nivel_de_perclos(valor)
