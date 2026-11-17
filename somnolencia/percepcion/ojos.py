"""
Apertura de los ojos.

Recibe el recorte de cada ojo y entrega una Medicion con valor entre 0
(cerrado) y 1 (abierto). La medida es la razón de bordes de gradiente.py.

Los recortes deben llegar en grises y con OJOS_ANCHO_DE_RECORTE pixeles de
ancho. Dentro del sistema los prepara geometria.py a partir del rostro
normalizado (pendiente). En la evaluación con imágenes sueltas los prepara
evaluacion/por_cuadro.py.
"""

from somnolencia import config
from somnolencia.tipos import Medicion
from somnolencia.percepcion.preproceso import suavizar_binomial
from somnolencia.percepcion.gradiente import razon_de_bordes


def razon_de_un_ojo(ojo_gris):
    """
    Razón de bordes de un recorte de un solo ojo.

    Pasos:
      1. Se descarta la parte superior del recorte, donde suele estar la
         ceja. La ceja es oscura y horizontal, y confundiría la medida.
      2. Se suaviza con el filtro binomial para quitar ruido.
      3. Se calcula la razón entre bordes verticales y horizontales
         alrededor de la banda más oscura.
    """
    alto = ojo_gris.shape[0]
    primer_renglon = int(config.OJOS_FRACCION_SIN_CEJA * alto)
    sin_ceja = ojo_gris[primer_renglon:, :]
    suavizado = suavizar_binomial(sin_ceja)
    return razon_de_bordes(suavizado)


def apertura_desde_razon(razon, razon_abierto, razon_cerrado):
    """
    Lleva la razón de bordes a una apertura entre 0 y 1.

    razon_abierto y razon_cerrado son los valores de referencia: los de la
    calibración de la persona, o los de config.py si no hay calibración.

    Ejemplo con las referencias 0.74 (abierto) y 0.39 (cerrado):
        razón 0.74  ->  apertura 1.0
        razón 0.60  ->  apertura (0.60 - 0.39) / (0.74 - 0.39) = 0.60
        razón 0.39  ->  apertura 0.0
    """
    rango = razon_abierto - razon_cerrado
    if rango <= 0:
        # Referencias inservibles: la calibración falló y hay que repetirla.
        return 0.0
    apertura = (razon - razon_cerrado) / rango
    return min(1.0, max(0.0, apertura))


def medir_ojos(ojo_izquierdo, ojo_derecho, t,
               razon_abierto=config.OJOS_RAZON_ABIERTO,
               razon_cerrado=config.OJOS_RAZON_CERRADO):
    """
    Entrega la Medicion de apertura de los ojos en el instante t.

    Se mide cada ojo por separado y se promedian las dos aperturas. Si no
    se pasan referencias de calibración, se usan las de config.py.
    """
    aperturas = []
    for ojo in (ojo_izquierdo, ojo_derecho):
        razon = razon_de_un_ojo(ojo)
        aperturas.append(apertura_desde_razon(razon, razon_abierto, razon_cerrado))
    return Medicion(t, sum(aperturas) / len(aperturas), True)
