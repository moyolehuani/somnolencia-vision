"""Pruebas de las alertas (somnolencia/temporal/alertas.py)."""

from somnolencia.temporal import perclos
from somnolencia.temporal.alertas import (
    nivel_de_alerta, NINGUNA, AVISO, ALERTA, CRITICA,
)


def test_sin_nada_en_curso_no_hay_alerta():
    assert nivel_de_alerta(0.0, 0.0, perclos.NORMAL)[0] == NINGUNA


def test_cierre_de_1_4_s_todavia_no_alerta():
    assert nivel_de_alerta(1.4, 0.0, perclos.NORMAL)[0] == NINGUNA


def test_cierre_de_1_5_s_da_alerta():
    assert nivel_de_alerta(1.5, 0.0, perclos.NORMAL)[0] == ALERTA


def test_cierre_de_exactamente_7_s_sigue_en_alerta():
    assert nivel_de_alerta(7.0, 0.0, perclos.NORMAL)[0] == ALERTA


def test_cierre_de_7_1_s_es_critica():
    assert nivel_de_alerta(7.1, 0.0, perclos.NORMAL)[0] == CRITICA


def test_distraccion_de_1_s_da_aviso_y_de_2_s_da_alerta():
    assert nivel_de_alerta(0.0, 0.9, perclos.NORMAL)[0] == NINGUNA
    assert nivel_de_alerta(0.0, 1.0, perclos.NORMAL)[0] == AVISO
    assert nivel_de_alerta(0.0, 2.0, perclos.NORMAL)[0] == ALERTA


def test_niveles_de_perclos():
    assert nivel_de_alerta(0.0, 0.0, perclos.ALERTA)[0] == AVISO
    assert nivel_de_alerta(0.0, 0.0, perclos.FATIGA)[0] == ALERTA
    assert nivel_de_alerta(0.0, 0.0, perclos.SOMNOLENCIA)[0] == CRITICA


def test_mientras_perclos_calienta_no_hay_alerta_por_perclos():
    assert nivel_de_alerta(0.0, 0.0, perclos.CALENTANDO)[0] == NINGUNA


def test_gana_la_alerta_mas_grave():
    # PERCLOS en alerta (aviso) y además un cierre en curso de 2 s (alerta).
    nivel, motivo = nivel_de_alerta(2.0, 0.0, perclos.ALERTA)
    assert nivel == ALERTA
    assert motivo == "ojos cerrados"
