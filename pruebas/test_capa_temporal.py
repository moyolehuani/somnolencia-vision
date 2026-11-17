"""
Prueba de conjunto de la capa temporal.

Se pasa el guion de ejemplo del simulador por la capa temporal completa
(estados, eventos, PERCLOS y alertas) y se comprueba que salga exactamente
lo que el guion dice que debe salir.
"""

import pytest

from somnolencia import simulador
from somnolencia.temporal.capa import CapaTemporal
from somnolencia.temporal import alertas, perclos

ESPERADO = {
    "parpadeo:normal": 1,
    "parpadeo:lento": 1,
    "parpadeo:microsueno": 1,
    "bostezo:bostezo": 1,
    "distraccion:2.0": 1,
}


def correr_guion(fps):
    """Corre el guion de ejemplo y entrega la capa y el resumen de cada cuadro."""
    capa = CapaTemporal()
    resumenes = []
    for t, ojos, boca, cabeza in simulador.generar(fps=fps):
        resumenes.append(capa.actualizar(t, ojos, boca, cabeza))
    capa.terminar(resumenes[-1]["t"])
    return capa, resumenes


def resumen_en(resumenes, t):
    """El resumen del primer cuadro cuyo tiempo es t o posterior."""
    for resumen in resumenes:
        if resumen["t"] >= t:
            return resumen
    raise ValueError("no hay cuadro en t = %s" % t)


@pytest.mark.parametrize("fps", [10, 15, 25, 30])
def test_el_guion_produce_los_eventos_esperados(fps):
    capa, _ = correr_guion(fps)
    assert capa.rastreador.contadores == ESPERADO
    assert capa.rastreador.indeterminados == 0


def test_durante_el_giro_los_ojos_quedan_sin_dato_y_no_abren_parpadeo():
    capa, resumenes = correr_guion(15)
    resumen = resumen_en(resumenes, 29.0)
    assert resumen["estado_ojos"] == "SIN_DATO"
    assert resumen["estado_cabeza"] == "DISTRAIDO"
    assert resumen["cierre_en_curso_s"] == 0.0
    # El giro queda anotado como tramo sin dato de los ojos.
    assert len(capa.rastreador.huecos_de_ojos) == 1


def test_la_alerta_suena_durante_el_cierre_y_no_al_terminar():
    _, resumenes = correr_guion(15)
    # Cierre de 10 a 13 s. Al segundo de cierre todavía no suena la alerta
    # por ojos cerrados (puede haber un aviso por PERCLOS, que es otra regla).
    assert resumen_en(resumenes, 11.0)["motivo_alerta"] != "ojos cerrados"
    # A los 2 s de cierre ya hay alerta, y el evento todavía no termina.
    resumen = resumen_en(resumenes, 12.0)
    assert resumen["alerta"] == alertas.ALERTA
    assert resumen["motivo_alerta"] == "ojos cerrados"
    assert resumen["contadores"].get("parpadeo:lento", 0) == 0


def test_el_microsueno_escala_a_critica():
    _, resumenes = correr_guion(15)
    # Cierre de 40 a 48 s. A los 7.5 s de cierre la alerta es crítica.
    assert resumen_en(resumenes, 47.5)["alerta"] == alertas.CRITICA


def test_perclos_despues_del_microsueno():
    _, resumenes = correr_guion(15)
    resumen = resumen_en(resumenes, 50.0)
    # Ventana de 20 a 50 s: 8 s cerrados (el microsueño) y unos 2.5 s sin
    # dato (el giro). 8 / 27.5 es cerca de 29%, nivel de fatiga.
    assert 0.28 < resumen["perclos"] < 0.30
    assert resumen["nivel_perclos"] == perclos.FATIGA


def test_perclos_calienta_al_principio():
    _, resumenes = correr_guion(15)
    assert resumen_en(resumenes, 5.0)["nivel_perclos"] == perclos.CALENTANDO
    assert resumen_en(resumenes, 10.0)["nivel_perclos"] != perclos.CALENTANDO
