"""Pruebas de la evaluación por evento y de la bitácora de mediciones."""

import csv

from somnolencia import escena_sintetica as escena
from somnolencia.interfaz.bitacora import Bitacora, BitacoraDeMediciones, COLUMNAS_DE_MEDICIONES
from evaluacion.por_evento import (
    crear_evento, leer_eventos, emparejar, metricas_por_tipo,
    confusion_de_parpadeos, comparar_perclos,
)
from escena_procesada import SISTEMA, RESUMENES


def eventos(*ternas):
    return [crear_evento(tipo, inicio, fin) for tipo, inicio, fin in ternas]


# ----- Categorías -------------------------------------------------------------

def test_la_categoria_se_calcula_con_las_reglas_del_sistema():
    assert crear_evento("parpadeo", 10.0, 10.5).categoria == "normal"
    assert crear_evento("parpadeo", 10.0, 13.0).categoria == "lento"
    assert crear_evento("parpadeo", 10.0, 18.0).categoria == "microsueno"
    assert crear_evento("distraccion", 30.0, 31.2).categoria == "1.0"
    assert crear_evento("bostezo", 20.0, 23.0).categoria == "bostezo"


def test_una_distraccion_menor_a_la_primera_banda_no_se_cuenta():
    assert crear_evento("distraccion", 30.0, 30.4) is None


# ----- Emparejamiento ------------------------------------------------------------

def test_un_evento_detectado_con_un_cuadro_de_retraso_es_acierto():
    anotados = eventos(("parpadeo", 10.0, 13.0))
    detectados = eventos(("parpadeo", 10.07, 13.13))
    parejas, sin_detectar, de_mas = emparejar(anotados, detectados)
    assert len(parejas) == 1 and not sin_detectar and not de_mas
    m = metricas_por_tipo(parejas, sin_detectar, de_mas)["parpadeo"]
    assert m["precision"] == 1.0 and m["recall"] == 1.0
    assert abs(m["error_de_duracion"] - 0.06) < 1e-6
    assert m["misma_categoria"] == 1.0


def test_un_anotado_sin_detectar_baja_el_recall():
    parejas, sin_detectar, de_mas = emparejar(eventos(("parpadeo", 10.0, 13.0)), [])
    m = metricas_por_tipo(parejas, sin_detectar, de_mas)["parpadeo"]
    assert m["recall"] == 0.0
    assert m["precision"] is None       # no hubo detectados: no se puede calcular


def test_un_detectado_de_mas_baja_la_precision():
    parejas, sin_detectar, de_mas = emparejar([], eventos(("bostezo", 20.0, 23.0)))
    m = metricas_por_tipo(parejas, sin_detectar, de_mas)["bostezo"]
    assert m["precision"] == 0.0
    assert m["recall"] is None


def test_un_cierre_largo_partido_en_dos_da_un_acierto_y_uno_de_mas():
    anotados = eventos(("parpadeo", 10.0, 18.0))
    detectados = eventos(("parpadeo", 10.0, 13.0), ("parpadeo", 13.5, 18.0))
    parejas, sin_detectar, de_mas = emparejar(anotados, detectados)
    assert len(parejas) == 1 and len(de_mas) == 1
    # Se empareja con el pedazo que más se traslapa, el de 4.5 s.
    assert parejas[0][1].inicio == 13.5
    # Y la categoría no coincide: se anotó microsueño y se detectó lento.
    tabla = confusion_de_parpadeos(parejas)
    assert tabla["microsueno"]["lento"] == 1


def test_eventos_de_distinto_tipo_no_se_emparejan():
    parejas, sin_detectar, de_mas = emparejar(eventos(("parpadeo", 10.0, 13.0)),
                                               eventos(("bostezo", 10.0, 13.0)))
    assert not parejas and len(sin_detectar) == 1 and len(de_mas) == 1


def test_eventos_que_no_se_tocan_no_se_emparejan():
    parejas, _, _ = emparejar(eventos(("parpadeo", 10.0, 10.3)), eventos(("parpadeo", 11.0, 11.3)))
    assert not parejas


# ----- Con archivos, usando la escena sintética --------------------------------------

def escribir_anotaciones(ruta):
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["tipo", "inicio_s", "fin_s", "notas"])
        for tipo, inicio, fin in escena.anotaciones():
            escritor.writerow([tipo, inicio, fin, "guion de la escena"])


def test_la_bitacora_de_la_escena_coincide_con_sus_anotaciones(tmp_path):
    escribir_anotaciones(tmp_path / "anotaciones.csv")
    bitacora = Bitacora(str(tmp_path))
    bitacora.guardar(SISTEMA.capa.rastreador.eventos)
    bitacora.cerrar()

    anotados = leer_eventos(tmp_path / "anotaciones.csv")
    detectados = leer_eventos(bitacora.ruta)
    assert len(anotados) == 5 and len(detectados) == 5

    parejas, sin_detectar, de_mas = emparejar(anotados, detectados)
    assert len(parejas) == 5 and not sin_detectar and not de_mas
    for m in metricas_por_tipo(parejas, sin_detectar, de_mas).values():
        assert m["precision"] == 1.0 and m["recall"] == 1.0
        assert m["error_de_duracion"] <= 0.07       # un cuadro a 15 cuadros por segundo
        assert m["misma_categoria"] == 1.0


def test_la_bitacora_de_mediciones_guarda_una_fila_por_cuadro(tmp_path):
    mediciones = BitacoraDeMediciones(str(tmp_path), "prueba")
    for _, resumen in RESUMENES:
        mediciones.guardar(resumen)
    mediciones.cerrar()

    with open(mediciones.ruta, newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert len(filas) == len(RESUMENES) == 676
    assert list(filas[0].keys()) == COLUMNAS_DE_MEDICIONES
    # Durante la calibración no hay estados.
    assert filas[0]["fase"] == "calibrando" and filas[0]["estado_ojos"] == ""
    # Durante el giro (t = 19 s) los ojos quedan sin valor.
    fila = [f for f in filas if abs(float(f["t"]) - 19.0) < 0.01][0]
    assert fila["valor_ojos"] == "" and fila["estado_ojos"] == "SIN_DATO"


def test_el_perclos_del_sistema_coincide_con_el_de_las_anotaciones(tmp_path):
    escribir_anotaciones(tmp_path / "anotaciones.csv")
    mediciones = BitacoraDeMediciones(str(tmp_path), "prueba")
    for _, resumen in RESUMENES:
        mediciones.guardar(resumen)
    mediciones.cerrar()

    resultado = comparar_perclos(mediciones.ruta, leer_eventos(tmp_path / "anotaciones.csv"))
    assert resultado["cuadros"] > 400
    # Las diferencias que quedan vienen de que el sistema mide cada evento
    # con un error de hasta un cuadro.
    assert resultado["error_medio"] < 0.005
    assert resultado["mismo_nivel"] > 0.95
