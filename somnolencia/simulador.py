"""
Simulador de mediciones.

Genera mediciones inventadas con la misma forma que las que entregarán los
módulos de percepción. Sirve para desarrollar y probar la capa temporal y
la interfaz sin cámara y sin esperar a que la percepción esté lista.

Un guion es una lista de tramos. Cada tramo dice qué valor toma una señal
entre dos instantes:

    (inicio, fin, señal, valor)

La señal es "ojos", "boca" o "cabeza". El valor es un número entre 0 y 1, o
None para simular que no se pudo medir. Fuera de los tramos, cada señal
toma su valor de reposo: ojos abiertos, boca cerrada, cabeza de frente.
"""

from somnolencia.tipos import Medicion

# Valores de reposo: ojos abiertos, boca cerrada, cabeza de frente.
REPOSO = {"ojos": 0.90, "boca": 0.02, "cabeza": 0.90}

# Guion de ejemplo. Dura 60 s y debe producir exactamente:
#   1 parpadeo normal, 1 parpadeo lento, 1 microsueño,
#   1 bostezo y 1 distracción en la banda 2.0.
GUION_DE_EJEMPLO = [
    (5.00, 5.30, "ojos", 0.05),      # parpadeo normal de 0.3 s
    (10.00, 13.00, "ojos", 0.05),    # cierre de 3 s: parpadeo lento
    (18.00, 21.00, "boca", 0.40),    # boca abierta 3 s: bostezo
    (24.00, 24.80, "boca", 0.30),    # boca abierta 0.8 s: hablar, no cuenta
    (28.00, 30.50, "cabeza", 0.20),  # giro de 2.5 s: distracción, banda 2.0
    (28.00, 30.50, "ojos", None),    # durante el giro no se ven los ojos
    (28.00, 30.50, "boca", None),    # ni la boca
    (40.00, 48.00, "ojos", 0.05),    # cierre de 8 s: microsueño
]
DURACION_DE_EJEMPLO = 60.0


def valor_en(t, guion, senal):
    """Valor de una señal en el instante t según el guion."""
    for inicio, fin, nombre, valor in guion:
        if nombre == senal and inicio <= t < fin:
            return valor
    return REPOSO[senal]


def generar(guion=GUION_DE_EJEMPLO, duracion=DURACION_DE_EJEMPLO, fps=15):
    """
    Entrega, cuadro por cuadro, (t, medicion_ojos, medicion_boca, medicion_cabeza).

    El tiempo de cada cuadro es su número dividido entre los cuadros por
    segundo, igual que al leer un archivo de video.
    """
    total_de_cuadros = int(duracion * fps)
    for numero in range(total_de_cuadros + 1):
        t = round(numero / fps, 6)
        mediciones = []
        for senal in ("ojos", "boca", "cabeza"):
            valor = valor_en(t, guion, senal)
            if valor is None:
                mediciones.append(Medicion(t, 0.0, False))
            else:
                mediciones.append(Medicion(t, valor, True))
        yield t, mediciones[0], mediciones[1], mediciones[2]
