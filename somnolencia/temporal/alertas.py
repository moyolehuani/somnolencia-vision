"""
Qué alerta mostrar en cada cuadro.

La alerta se decide con lo que está pasando AHORA: cuánto lleva el cierre
de ojos en curso, cuánto lleva la distracción en curso y en qué nivel está
PERCLOS. No se espera a que el evento termine, porque avisar después de un
microsueño ya no sirve (decisión D12).

Se entrega la alerta más grave que se cumpla.
"""

from somnolencia import config
from somnolencia.temporal import perclos

# Niveles de alerta, del más leve al más grave.
NINGUNA = "ninguna"
AVISO = "aviso"
ALERTA = "alerta"
CRITICA = "critica"


def nivel_de_alerta(cierre_en_curso_s, distraccion_en_curso_s, nivel_perclos):
    """
    cierre_en_curso_s        segundos que lleva el cierre de ojos abierto (0 si no hay)
    distraccion_en_curso_s   segundos que lleva la distracción abierta (0 si no hay)
    nivel_perclos            nivel que entrega calcular_perclos

    Entrega (nivel, motivo). El motivo es un texto corto para la interfaz.
    """
    # --- Crítica -----------------------------------------------------------
    # Más de 7 s con los ojos cerrados es la banda de microsueño.
    if cierre_en_curso_s > config.PARPADEO_LENTO_MAX_S:
        return CRITICA, "ojos cerrados mas de 7 s"
    if nivel_perclos == perclos.SOMNOLENCIA:
        return CRITICA, "PERCLOS en somnolencia"

    # --- Alerta ------------------------------------------------------------
    # 1.5 s de cierre es el umbral de alerta de la referencia [1] del enunciado.
    if cierre_en_curso_s >= config.AVISO_CIERRE_EN_CURSO_S:
        return ALERTA, "ojos cerrados"
    if nivel_perclos == perclos.FATIGA:
        return ALERTA, "PERCLOS en fatiga"
    if distraccion_en_curso_s >= config.ALERTA_DISTRACCION_ALERTA_S:
        return ALERTA, "mirada fuera del frente"

    # --- Aviso -------------------------------------------------------------
    if nivel_perclos == perclos.ALERTA:
        return AVISO, "PERCLOS en alerta"
    if distraccion_en_curso_s >= config.ALERTA_DISTRACCION_AVISO_S:
        return AVISO, "mirada fuera del frente"

    return NINGUNA, ""
