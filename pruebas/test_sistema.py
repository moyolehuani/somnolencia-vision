"""
Pruebas del sistema completo y del seguimiento del rostro.

Se usa la escena sintética: una cara dibujada que sigue un guion. Estas
pruebas comprueban que todas las piezas están bien conectadas, del cuadro
a la bitácora. No dicen qué tan bien funciona el sistema con personas.
"""

import numpy as np

from somnolencia import config
from somnolencia import escena_sintetica as escena
from somnolencia.sistema import Sistema
from somnolencia.percepcion.piramide import piramide_gaussiana
from somnolencia.percepcion.rostro import SeguidorDeRostro
from somnolencia.percepcion.captura import a_tamano_de_trabajo
from somnolencia.interfaz.overlay import dibujar, vista_de_depuracion

# La escena se procesa una sola vez, en escena_procesada.py, y las pruebas
# de abajo revisan ese mismo resultado.
from escena_procesada import SISTEMA, RESUMENES


def resumen_en(t):
    for gris, resumen in RESUMENES:
        if resumen["t"] >= t:
            return gris, resumen


def test_la_escena_produce_los_eventos_del_guion():
    assert SISTEMA.capa.rastreador.contadores == escena.EVENTOS_ESPERADOS
    assert SISTEMA.capa.rastreador.indeterminados == 0


def test_las_duraciones_medidas_coinciden_con_el_guion():
    esperadas = {"normal": 0.3, "lento": 3.0, "microsueno": 8.5, "bostezo": 3.0, "2.0": 2.5}
    for evento in SISTEMA.capa.rastreador.eventos:
        # A 15 cuadros por segundo un cuadro dura 0.067 s.
        assert abs(evento.duracion - esperadas[evento.categoria]) <= 0.07


def test_la_calibracion_aprende_las_referencias_de_ojos():
    cal = SISTEMA.calibracion
    assert cal.aviso == ""
    assert cal.razon_abierto - cal.razon_cerrado > config.CALIBRACION_DIFERENCIA_MINIMA


def test_durante_la_calibracion_no_se_cuentan_eventos():
    # El guion cierra los ojos de 3 a 5 s, dentro de la calibración.
    _, resumen = resumen_en(4.0)
    assert resumen["fase"] == "calibrando"
    assert all(evento.inicio >= 5.0 for evento in SISTEMA.capa.rastreador.eventos)


def test_durante_el_giro_los_ojos_quedan_sin_dato():
    _, resumen = resumen_en(19.0)
    assert resumen["estado_cabeza"] == "DISTRAIDO"
    assert resumen["estado_ojos"] == "SIN_DATO"
    assert resumen["rostro"] is None


def test_el_rostro_se_reencuentra_despues_del_giro():
    _, resumen = resumen_en(21.5)
    assert resumen["estado_cabeza"] == "ATENTO"
    assert resumen["estado_ojos"] == "ABIERTO"


def test_la_caja_sigue_a_la_cara():
    # La cara se mece hasta 20 pixeles a cada lado. La caja debe ir con ella.
    for t in (6.0, 10.0, 16.0, 29.0):
        _, resumen = resumen_en(t)
        x_real = escena.CARA_X + int(round(20 * np.sin(2 * np.pi * resumen["t"] / 8)))
        assert abs(resumen["caja"][0] - x_real) <= 2


def test_el_bostezo_no_se_confunde_con_distraccion():
    _, resumen = resumen_en(25.0)
    assert resumen["estado_boca"] == "ABIERTA"
    assert resumen["estado_cabeza"] == "ATENTO"


def test_la_interfaz_dibuja_sin_fallar_en_todas_las_fases():
    for t in (1.0, 12.6, 19.0, 25.0, 38.0):
        gris, resumen = resumen_en(t)
        imagen = dibujar(gris, resumen, fps=15)
        assert imagen.shape == (360, 640 + 300, 3)
    _, resumen = resumen_en(12.6)
    assert vista_de_depuracion(resumen).shape == (320, 256, 3)
    _, resumen = resumen_en(19.0)
    assert vista_de_depuracion(resumen) is None


def test_sin_calibracion_se_vigila_desde_el_primer_cuadro():
    sistema = Sistema()
    t, gris = next(escena.generar())
    sistema.iniciar(gris, escena.caja_inicial(), t, con_calibracion=False)
    resumen = sistema.procesar(gris, t)
    assert resumen["fase"] == "vigilando"
    assert sistema.calibracion.razon_abierto == config.OJOS_RAZON_ABIERTO


# ----- Seguimiento del rostro -------------------------------------------------

def seguir_cara_desplazada(dx):
    """Fija el rostro en un cuadro y lo busca en otro con la cara movida dx pixeles."""
    base = escena.cuadro(0.0)
    seguidor = SeguidorDeRostro(piramide_gaussiana(base, 3), escena.caja_inicial())
    movido = escena.FONDO.copy()
    x = escena.CARA_X + dx
    movido[escena.CARA_Y:escena.CARA_Y + escena.CARA_ALTO, x:x + escena.CARA_ANCHO] = \
        base[escena.CARA_Y:escena.CARA_Y + escena.CARA_ALTO,
             escena.CARA_X:escena.CARA_X + escena.CARA_ANCHO]
    return seguidor.seguir(piramide_gaussiana(movido, 3))


def test_el_seguidor_encuentra_una_cara_que_se_movio_poco():
    caja, puntaje, _ = seguir_cara_desplazada(12)
    assert abs(caja[0] - (escena.CARA_X + 12)) <= 2
    assert puntaje > 0.8


def test_la_prediccion_de_movimiento_alcanza_una_cara_que_se_movio_mucho():
    # 48 pixeles son 12 en el nivel más pequeño, más que la ventana de
    # búsqueda de 8. Sin la correlación de fase no se alcanzaría.
    caja, puntaje, movimiento = seguir_cara_desplazada(48)
    assert abs(movimiento[0] - 48) <= 4
    assert abs(caja[0] - (escena.CARA_X + 48)) <= 2
    assert puntaje > 0.8


def test_si_la_cara_desaparece_la_caja_se_queda_donde_estaba():
    base = escena.cuadro(0.0)
    seguidor = SeguidorDeRostro(piramide_gaussiana(base, 3), escena.caja_inicial())
    caja, puntaje, _ = seguidor.seguir(piramide_gaussiana(escena.FONDO.copy(), 3))
    assert caja == escena.caja_inicial()
    assert puntaje < config.CABEZA_UMBRAL_DISTRAIDO


# ----- Tamaño de trabajo --------------------------------------------------------

def test_a_tamano_de_trabajo():
    assert a_tamano_de_trabajo(np.zeros((360, 640), np.float32)).shape == (360, 640)
    assert a_tamano_de_trabajo(np.zeros((720, 1280), np.float32)).shape == (360, 640)
    assert a_tamano_de_trabajo(np.zeros((1080, 1920), np.float32)).shape == (360, 640)
    assert a_tamano_de_trabajo(np.zeros((480, 640), np.float32)).shape == (360, 640)


def test_la_captura_de_la_escena_entrega_cuadro_y_tiempo():
    from somnolencia.percepcion.captura import Captura
    captura = Captura("escena")
    gris, t = captura.leer()
    assert gris.shape == (360, 640)
    assert t == 0.0


# ----- Controles ------------------------------------------------------------------

def test_los_nombres_de_los_deslizadores_caben_sin_recortarse():
    # En Windows, OpenCV recorta los nombres de más de 10 letras.
    from somnolencia.interfaz import controles
    for nombre, nombre_en_config, _, _, _ in controles.DESLIZADORES:
        assert len(nombre) <= controles.LARGO_MAXIMO_DE_NOMBRE
        assert hasattr(config, nombre_en_config)


def test_la_leyenda_de_los_controles_se_dibuja():
    from somnolencia.interfaz import controles
    leyenda = controles.imagen_de_leyenda()
    assert leyenda.shape[1] == 640 and leyenda.shape[2] == 3
