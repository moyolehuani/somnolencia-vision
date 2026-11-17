"""
Frontalidad de la cabeza.

La medición sale del seguimiento del rostro: es el puntaje de parecido
entre lo que se ve y la plantilla de la cara de frente. Vale cerca de 1
con la cabeza de frente y baja cuando la persona voltea.

A diferencia de los ojos y la boca, esta medición siempre es válida. Si el
rostro no aparece, el valor es bajo y eso cuenta como distracción
(decisión D14).
"""

from somnolencia.tipos import Medicion


def medir_cabeza(puntaje, t):
    """Lleva el puntaje del seguimiento (entre -1 y 1) a una Medicion entre 0 y 1."""
    return Medicion(t, min(1.0, max(0.0, puntaje)), True)
