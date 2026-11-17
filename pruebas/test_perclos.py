"""Pruebas de PERCLOS (somnolencia/temporal/perclos.py)."""

from somnolencia import config
from somnolencia.temporal.perclos import (
    calcular_perclos, tiempo_dentro,
    NORMAL, ALERTA, FATIGA, SOMNOLENCIA, CALENTANDO, SIN_DATO,
)


def test_tiempo_dentro_de_la_ventana():
    assert tiempo_dentro(7.0, 12.0, 10.0, 40.0) == 2.0    # empezó antes de la ventana
    assert tiempo_dentro(15.0, 18.0, 10.0, 40.0) == 3.0   # todo dentro
    assert tiempo_dentro(2.0, 5.0, 10.0, 40.0) == 0.0     # todo fuera


def test_30_s_con_ojos_abiertos_da_cero():
    valor, nivel = calcular_perclos(30.0, 0.0, cierres=[], huecos=[])
    assert valor == 0.0
    assert nivel == NORMAL


def test_ejemplo_del_readme_da_12_5_por_ciento():
    # Ventana de 40 a 70 s: un parpadeo normal, dos cierres largos y 2 s sin dato.
    cierres = [(45.0, 45.3), (50.0, 52.0), (60.0, 61.5)]
    huecos = [(65.0, 67.0)]
    valor, nivel = calcular_perclos(70.0, 0.0, cierres, huecos)
    assert valor == 0.125          # 3.5 s cerrados entre 28 s válidos
    assert nivel == ALERTA


def diez_parpadeos_de_0_3_s():
    return [(float(k), k + 0.3) for k in range(2, 30, 3)]   # 10 parpadeos en 30 s


def test_parpadeos_normales_no_cuentan_con_el_interruptor_apagado(monkeypatch):
    monkeypatch.setattr(config, "PERCLOS_CUENTA_PARPADEOS_NORMALES", False)
    valor, nivel = calcular_perclos(30.0, 0.0, diez_parpadeos_de_0_3_s(), [])
    assert valor == 0.0
    assert nivel == NORMAL


def test_parpadeos_normales_cuentan_con_el_interruptor_encendido(monkeypatch):
    monkeypatch.setattr(config, "PERCLOS_CUENTA_PARPADEOS_NORMALES", True)
    valor, nivel = calcular_perclos(30.0, 0.0, diez_parpadeos_de_0_3_s(), [])
    assert valor == 0.1            # 3 s cerrados entre 30 s
    assert nivel == ALERTA         # una persona despierta ya queda en alerta


def test_cierre_que_cruza_el_borde_de_la_ventana_cuenta_solo_lo_de_dentro():
    # En t = 40 la ventana va de 10 a 40. El cierre fue de 7 a 12: cuentan 2 s.
    valor, _ = calcular_perclos(40.0, 0.0, cierres=[(7.0, 12.0)], huecos=[])
    assert valor == round(2.0 / 30.0, 4)


def test_cierre_en_curso_cuenta_hasta_el_momento_actual():
    # El rastreador entrega el cierre abierto como (inicio, t).
    valor, nivel = calcular_perclos(30.0, 0.0, cierres=[(24.0, 30.0)], huecos=[])
    assert valor == 0.2
    assert nivel == FATIGA


def test_con_solo_5_s_de_sesion_esta_calentando():
    valor, nivel = calcular_perclos(5.0, 0.0, cierres=[(1.0, 3.0)], huecos=[])
    assert valor is None
    assert nivel == CALENTANDO


def test_ventana_casi_sin_datos_validos():
    # 30 s de sesión pero 25 s sin dato: quedan 5 s válidos, menos del mínimo.
    valor, nivel = calcular_perclos(30.0, 0.0, cierres=[], huecos=[(2.0, 27.0)])
    assert valor is None
    assert nivel == SIN_DATO


def test_limites_de_los_niveles():
    # 2.4 s de 30 s es exactamente 8%: ya es alerta.
    assert calcular_perclos(30.0, 0.0, [(10.0, 12.4)], []) == (0.08, ALERTA)
    # 4.5 s de 30 s es exactamente 15%: ya es fatiga.
    assert calcular_perclos(30.0, 0.0, [(10.0, 14.5)], []) == (0.15, FATIGA)
    # 9 s de 30 s es exactamente 30%: ya es somnolencia.
    assert calcular_perclos(30.0, 0.0, [(10.0, 19.0)], []) == (0.3, SOMNOLENCIA)
    # 2.3 s de 30 s es 7.67%: todavía normal.
    assert calcular_perclos(30.0, 0.0, [(10.0, 12.3)], [])[1] == NORMAL


def test_la_ventana_olvida_lo_que_paso_hace_mas_de_30_s():
    # Un cierre de 5 s entre 10 y 15. En t = 50 la ventana va de 20 a 50.
    valor, nivel = calcular_perclos(50.0, 0.0, cierres=[(10.0, 15.0)], huecos=[])
    assert valor == 0.0
    assert nivel == NORMAL
