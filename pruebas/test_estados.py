"""Pruebas del umbral doble (somnolencia/temporal/estados.py)."""

from somnolencia.tipos import (
    Medicion, ABIERTO, CERRADO, CERRADA, ABIERTA, ATENTO, DISTRAIDO, SIN_DATO,
)
from somnolencia.temporal.estados import (
    crear_actualizador_ojos, crear_actualizador_boca, crear_actualizador_cabeza,
)


def estados_de(actualizador, valores):
    """Pasa una lista de valores por el actualizador y entrega los estados."""
    estados = []
    for numero, valor in enumerate(valores):
        estados.append(actualizador.actualizar(Medicion(numero * 0.1, valor, True)))
    return estados


def test_ojos_umbral_doble_con_apertura_que_oscila():
    # La apertura oscila cerca del límite. Con umbral doble sale un solo cierre.
    valores = [0.80, 0.22, 0.18, 0.27, 0.23, 0.28, 0.40]
    esperado = [ABIERTO, ABIERTO, CERRADO, CERRADO, CERRADO, CERRADO, ABIERTO]
    assert estados_de(crear_actualizador_ojos(), valores) == esperado


def test_ojos_entre_los_dos_umbrales_no_cambia():
    # 0.25 está entre 0.20 y 0.35: estando abierto se queda abierto.
    assert estados_de(crear_actualizador_ojos(), [0.80, 0.25, 0.25]) == [ABIERTO] * 3


def test_boca_se_abre_al_subir_y_se_cierra_al_bajar():
    valores = [0.02, 0.18, 0.25, 0.16, 0.10]
    esperado = [CERRADA, CERRADA, ABIERTA, ABIERTA, CERRADA]
    assert estados_de(crear_actualizador_boca(), valores) == esperado


def test_cabeza_se_distrae_al_bajar_y_regresa_al_subir():
    valores = [0.90, 0.55, 0.45, 0.55, 0.65]
    esperado = [ATENTO, ATENTO, DISTRAIDO, DISTRAIDO, ATENTO]
    assert estados_de(crear_actualizador_cabeza(), valores) == esperado


def test_medicion_no_valida_da_sin_dato():
    actualizador = crear_actualizador_ojos()
    assert actualizador.actualizar(Medicion(0.0, 0.0, False)) == SIN_DATO


def test_despues_de_sin_dato_se_conserva_el_ultimo_estado():
    actualizador = crear_actualizador_ojos()
    actualizador.actualizar(Medicion(0.0, 0.10, True))      # se cierra
    actualizador.actualizar(Medicion(0.1, 0.00, False))     # sin dato
    # 0.30 no supera el umbral de reapertura, así que sigue cerrado.
    assert actualizador.actualizar(Medicion(0.2, 0.30, True)) == CERRADO
