"""
Pruebas del rastreador de eventos (somnolencia/temporal/eventos.py).

Las entradas son estados escritos a mano, cuadro por cuadro. Decir "ojos
cerrados de 10.0 a 10.5 s" significa que el primer cuadro cerrado tiene
t = 10.0 y el primer cuadro abierto tiene t = 10.5. Así se prueba la regla
de clasificación sin que el muestreo de la cámara mueva los límites.
"""

from somnolencia.tipos import (
    ABIERTO, CERRADO, CERRADA, ABIERTA, ATENTO, DISTRAIDO, SIN_DATO,
)
from somnolencia.temporal.eventos import RastreadorDeEventos


def dentro(t, tramos):
    """True si t cae en alguno de los tramos (inicio incluido, fin excluido)."""
    for inicio, fin in tramos:
        if inicio <= t < fin:
            return True
    return False


def correr(ojos=(), boca=(), cabeza=(), sin_dato_ojos=(), abiertos_sueltos=(),
           hasta=40.0, paso=0.1):
    """
    Arma una secuencia de cuadros y la pasa por un rastreador nuevo.

    ojos, boca, cabeza   tramos en que cada señal está en su estado activo
    sin_dato_ojos        tramos en que los ojos no se pueden medir
    abiertos_sueltos     instantes en que un cuadro suelto sale abierto (ruido)
    """
    rastreador = RastreadorDeEventos()
    for numero in range(round(hasta / paso) + 1):
        t = round(numero * paso, 3)
        estado_ojos = CERRADO if dentro(t, ojos) else ABIERTO
        if dentro(t, sin_dato_ojos):
            estado_ojos = SIN_DATO
        if t in abiertos_sueltos:
            estado_ojos = ABIERTO
        estado_boca = ABIERTA if dentro(t, boca) else CERRADA
        estado_cabeza = DISTRAIDO if dentro(t, cabeza) else ATENTO
        rastreador.actualizar(t, estado_ojos, estado_boca, estado_cabeza)
    return rastreador


def categorias(rastreador):
    return [(evento.tipo, evento.categoria) for evento in rastreador.eventos]


# ----- Parpadeos: Tabla 1 del enunciado -------------------------------------

def test_cierre_de_0_3_s_es_parpadeo_normal():
    r = correr(ojos=[(10.0, 10.3)])
    assert categorias(r) == [("parpadeo", "normal")]
    assert r.eventos[0].duracion == 0.3


def test_cierre_de_exactamente_0_5_s_es_normal():
    r = correr(ojos=[(10.0, 10.5)])
    assert categorias(r) == [("parpadeo", "normal")]
    assert r.eventos[0].duracion == 0.5


def test_cierre_de_0_6_s_es_lento():
    r = correr(ojos=[(10.0, 10.6)])
    assert categorias(r) == [("parpadeo", "lento")]


def test_cierre_de_exactamente_7_s_es_lento():
    r = correr(ojos=[(10.0, 17.0)])
    assert categorias(r) == [("parpadeo", "lento")]
    assert r.eventos[0].duracion == 7.0


def test_cierre_de_7_1_s_es_microsueno():
    r = correr(ojos=[(10.0, 17.1)])
    assert categorias(r) == [("parpadeo", "microsueno")]


def test_inicio_y_fin_del_evento_son_los_del_primer_cuadro_de_cada_cambio():
    r = correr(ojos=[(10.0, 13.0)])
    assert r.eventos[0].inicio == 10.0
    assert r.eventos[0].fin == 13.0


# ----- Antirrebote -----------------------------------------------------------

def test_un_cuadro_abierto_suelto_no_parte_un_microsueno():
    # Cierre de 8 s con un solo cuadro mal clasificado como abierto a los 14 s.
    r = correr(ojos=[(10.0, 18.0)], abiertos_sueltos=[14.0])
    assert categorias(r) == [("parpadeo", "microsueno")]
    assert r.eventos[0].duracion == 8.0


def test_dos_parpadeos_separados_medio_segundo_son_dos():
    r = correr(ojos=[(10.0, 10.3), (10.8, 11.1)])
    assert categorias(r) == [("parpadeo", "normal"), ("parpadeo", "normal")]


# ----- Sin dato --------------------------------------------------------------

def test_sin_dato_breve_dentro_de_un_cierre_no_lo_interrumpe():
    r = correr(ojos=[(10.0, 12.0)], sin_dato_ojos=[(10.5, 10.7)])
    assert categorias(r) == [("parpadeo", "lento")]
    assert r.eventos[0].duracion == 2.0


def test_sin_dato_largo_deja_el_cierre_indeterminado():
    r = correr(ojos=[(10.0, 10.5)], sin_dato_ojos=[(10.5, 12.0)])
    assert categorias(r) == []                 # no se cuenta ningún parpadeo
    assert r.indeterminados == 1
    assert r.huecos_de_ojos == [(10.5, 12.0)]  # ese tramo queda como sin dato


def test_sin_dato_fuera_de_un_cierre_se_anota_como_hueco():
    r = correr(sin_dato_ojos=[(20.0, 22.0)])
    assert categorias(r) == []
    assert r.huecos_de_ojos == [(20.0, 22.0)]


# ----- Bostezos --------------------------------------------------------------

def test_boca_abierta_0_8_s_no_es_bostezo():
    r = correr(boca=[(20.0, 20.8)])
    assert categorias(r) == []


def test_boca_abierta_3_s_es_un_bostezo():
    r = correr(boca=[(20.0, 23.0)])
    assert categorias(r) == [("bostezo", "bostezo")]
    assert r.contadores["bostezo:bostezo"] == 1


# ----- Distracción -----------------------------------------------------------

def test_giro_de_0_4_s_no_se_cuenta():
    r = correr(cabeza=[(30.0, 30.4)])
    assert categorias(r) == []


def test_giro_de_0_5_s_cae_en_la_banda_0_5():
    r = correr(cabeza=[(30.0, 30.5)])
    assert categorias(r) == [("distraccion", "0.5")]


def test_giro_de_1_2_s_cae_en_la_banda_1_0():
    r = correr(cabeza=[(30.0, 31.2)])
    assert categorias(r) == [("distraccion", "1.0")]


def test_giro_de_1_7_s_cae_en_la_banda_1_5():
    r = correr(cabeza=[(30.0, 31.7)])
    assert categorias(r) == [("distraccion", "1.5")]


def test_giro_de_3_s_cae_en_la_banda_2_0():
    r = correr(cabeza=[(30.0, 33.0)])
    assert categorias(r) == [("distraccion", "2.0")]


# ----- El resultado depende del tiempo, no del número de cuadros -------------

def test_mismo_cierre_a_10_y_a_25_cuadros_por_segundo():
    lento = correr(ojos=[(10.03, 13.02)], paso=0.1)     # 10 cuadros por segundo
    rapido = correr(ojos=[(10.03, 13.02)], paso=0.04)   # 25 cuadros por segundo
    assert categorias(lento) == [("parpadeo", "lento")]
    assert categorias(rapido) == [("parpadeo", "lento")]
    # Las duraciones medidas difieren en menos de un cuadro del video más lento.
    assert abs(lento.eventos[0].duracion - rapido.eventos[0].duracion) < 0.1


# ----- Contadores, eventos en curso y fin del video ---------------------------

def test_contadores_por_categoria():
    r = correr(ojos=[(5.0, 5.3), (10.0, 13.0), (20.0, 20.2)])
    assert r.contadores == {"parpadeo:normal": 2, "parpadeo:lento": 1}


def test_duracion_del_cierre_en_curso():
    rastreador = RastreadorDeEventos()
    for numero in range(31):
        t = round(numero * 0.1, 3)
        estado = CERRADO if t >= 1.0 else ABIERTO
        rastreador.actualizar(t, estado, CERRADA, ATENTO)
    # Se cerró en t = 1.0 y el último cuadro es t = 3.0.
    assert round(rastreador.cierre_en_curso(3.0), 3) == 2.0
    assert rastreador.eventos == []     # todavía no termina


def test_al_acabarse_el_video_se_cierra_lo_que_quedo_abierto():
    rastreador = RastreadorDeEventos()
    for numero in range(31):
        t = round(numero * 0.1, 3)
        estado = CERRADO if t >= 1.0 else ABIERTO
        rastreador.actualizar(t, estado, CERRADA, ATENTO)
    nuevos = rastreador.cerrar_todo(3.0)
    assert [(e.tipo, e.categoria, e.duracion) for e in nuevos] == [("parpadeo", "lento", 2.0)]
