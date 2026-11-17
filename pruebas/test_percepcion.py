"""
Pruebas de los algoritmos de percepción ya escritos.

Aquí sí se usa OpenCV, como referencia: cada filtro propio debe dar lo
mismo que la función equivalente de OpenCV. Es la versión corta de los
cuadernos de verificacion/.
"""

import cv2
import numpy as np

from somnolencia.percepcion.preproceso import filtrar_1d, suavizar_binomial
from somnolencia.percepcion.gradiente import (
    gradiente_vertical, gradiente_horizontal, banda_mas_oscura, razon_de_bordes,
)
from somnolencia.percepcion.ojos import razon_de_un_ojo, apertura_desde_razon, medir_ojos


def imagen_de_prueba():
    """Imagen sintética con rampas y ruido fijo. No es un rostro."""
    generador = np.random.default_rng(7)
    y, x = np.mgrid[0:48, 0:64]
    return (2.0 * x + 1.5 * y + 30 * generador.random((48, 64))).astype(np.float32)


# ----- Filtros contra OpenCV --------------------------------------------------

def test_suavizado_binomial_coincide_con_gaussianblur():
    img = imagen_de_prueba()
    # Con tamaño 5 y sigma 0, OpenCV usa el núcleo (1, 4, 6, 4, 1) / 16.
    referencia = cv2.GaussianBlur(img, (5, 5), 0)
    assert np.abs(suavizar_binomial(img) - referencia).max() < 1e-3


def test_gradiente_vertical_coincide_con_sobel():
    img = imagen_de_prueba()
    referencia = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
    assert np.abs(gradiente_vertical(img) - referencia).max() < 1e-3


def test_gradiente_horizontal_coincide_con_sobel():
    img = imagen_de_prueba()
    referencia = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    assert np.abs(gradiente_horizontal(img) - referencia).max() < 1e-3


def test_suavizar_una_imagen_constante_la_deja_igual():
    img = np.full((20, 30), 100.0, dtype=np.float32)
    assert np.abs(suavizar_binomial(img) - img).max() < 1e-4


def test_gradiente_de_una_rampa_vertical_es_constante():
    # Cada renglón vale 3 más que el anterior. Sobel da 3 * 2 * 4 = 24:
    # diferencia entre renglones a distancia 2, por la suma del suavizado (1+2+1).
    y = np.arange(20, dtype=np.float32).reshape(-1, 1)
    rampa = np.repeat(3.0 * y, 30, axis=1)
    interior = gradiente_vertical(rampa)[2:-2, 2:-2]
    assert np.abs(interior - 24.0).max() < 1e-3
    assert np.abs(gradiente_horizontal(rampa)).max() < 1e-3


def test_filtrar_1d_no_cambia_el_tamano():
    img = imagen_de_prueba()
    assert filtrar_1d(img, (1, 2, 1), eje=0).shape == img.shape
    assert filtrar_1d(img, (1, 2, 1), eje=1).shape == img.shape


# ----- Medida de ojos con dibujos sintéticos ------------------------------------

def ojo_abierto_sintetico():
    """Fondo claro con un disco oscuro en el centro, como un iris."""
    img = np.full((48, 64), 200.0, dtype=np.float32)
    y, x = np.mgrid[0:48, 0:64]
    img[(x - 32) ** 2 + (y - 26) ** 2 <= 9 ** 2] = 40.0
    return img


def ojo_cerrado_sintetico():
    """Fondo claro con una línea oscura horizontal, como las pestañas."""
    img = np.full((48, 64), 200.0, dtype=np.float32)
    img[25:28, 8:56] = 40.0
    return img


def test_la_banda_mas_oscura_cae_sobre_la_linea():
    primer_renglon = banda_mas_oscura(ojo_cerrado_sintetico(), (12, 52), 5)
    assert 22 <= primer_renglon <= 26


def test_la_razon_es_mayor_con_el_disco_que_con_la_linea():
    abierto = razon_de_bordes(suavizar_binomial(ojo_abierto_sintetico()))
    cerrado = razon_de_bordes(suavizar_binomial(ojo_cerrado_sintetico()))
    # La banda cae a media altura del disco. Ahí solo se ven sus dos lados,
    # que son bordes verticales, así que la razón sale mayor que 1.
    assert abierto > 1.0
    # La línea casi no tiene bordes verticales en las columnas centrales.
    assert cerrado < 0.1


def test_razon_de_un_ojo_tambien_los_distingue():
    assert razon_de_un_ojo(ojo_abierto_sintetico()) > razon_de_un_ojo(ojo_cerrado_sintetico())


def test_apertura_desde_razon():
    assert apertura_desde_razon(0.74, 0.74, 0.39) == 1.0
    assert apertura_desde_razon(0.39, 0.74, 0.39) == 0.0
    assert abs(apertura_desde_razon(0.60, 0.74, 0.39) - 0.60) < 1e-6
    assert apertura_desde_razon(2.00, 0.74, 0.39) == 1.0     # se recorta por arriba
    assert apertura_desde_razon(0.10, 0.74, 0.39) == 0.0     # y por abajo
    assert apertura_desde_razon(0.50, 0.40, 0.40) == 0.0     # referencias inservibles


def test_medir_ojos_entrega_una_medicion():
    abierta = medir_ojos(ojo_abierto_sintetico(), ojo_abierto_sintetico(), 1.5)
    cerrada = medir_ojos(ojo_cerrado_sintetico(), ojo_cerrado_sintetico(), 1.6)
    assert abierta.t == 1.5 and abierta.valido
    assert abierta.valor > 0.8
    assert cerrada.valor < 0.2


# ----- Pirámide, histograma, correlaciones y mapeo inverso contra OpenCV ----------

from somnolencia.percepcion.preproceso import histograma_acumulado, especificar_histograma
from somnolencia.percepcion.piramide import reducir, piramide_gaussiana, banda_laplaciana
from somnolencia.percepcion.correlacion import (
    correlacion_normalizada, posicion_del_maximo, correlacion_de_fase,
)
from somnolencia.percepcion.geometria import (
    recortar_y_escalar, normalizar_rostro, recortes_de_ojos,
)


def textura(alto, ancho, semilla=11):
    """Ruido suavizado entre 0 y 255. Se parece más a una foto que el ruido puro."""
    generador = np.random.default_rng(semilla)
    img = (generador.random((alto, ancho)) * 255).astype(np.float32)
    for _ in range(3):
        img = suavizar_binomial(img)
    img = (img - img.min()) / (img.max() - img.min()) * 255
    return img.astype(np.float32)


def test_reducir_coincide_con_pyrdown():
    img = textura(90, 160)
    assert np.abs(reducir(img) - cv2.pyrDown(img)).max() < 1e-3
    # También con tamaños impares.
    impar = textura(91, 161)
    assert reducir(impar).shape == cv2.pyrDown(impar).shape
    assert np.abs(reducir(impar) - cv2.pyrDown(impar)).max() < 1e-3


def test_piramide_de_tres_niveles():
    niveles = piramide_gaussiana(textura(360, 640), 3)
    assert [nivel.shape for nivel in niveles] == [(360, 640), (180, 320), (90, 160)]


def test_banda_laplaciana_de_una_imagen_lisa_es_cero():
    img = np.full((20, 30), 80.0, dtype=np.float32)
    assert np.abs(banda_laplaciana(img)).max() < 1e-4


def test_especificar_contra_el_propio_histograma_no_cambia_la_imagen():
    img = textura(160, 128)
    salida = especificar_histograma(img, histograma_acumulado(img))
    assert np.abs(salida - np.rint(img)).max() == 0


def test_especificar_contra_histograma_uniforme_es_ecualizar():
    img = textura(160, 128)
    uniforme = np.arange(1, 257) / 256
    referencia = cv2.equalizeHist(np.rint(img).astype(np.uint8))
    # Las dos redondean distinto, así que pueden diferir en un nivel de gris.
    assert np.abs(especificar_histograma(img, uniforme) - referencia).max() <= 1


def test_especificar_corrige_una_imagen_oscurecida():
    img = textura(160, 128)
    oscura = np.clip(img * 0.6 + 10, 0, 255)
    acumulado_ref = histograma_acumulado(img)
    antes = np.abs(histograma_acumulado(oscura) - acumulado_ref).max()
    despues = np.abs(histograma_acumulado(especificar_histograma(oscura, acumulado_ref)) - acumulado_ref).max()
    assert antes > 0.3
    assert despues < 0.03


def test_correlacion_normalizada_coincide_con_matchtemplate():
    img = textura(90, 160)
    plantilla = img[30:68, 70:100].copy()
    mapa = correlacion_normalizada(img, plantilla)
    referencia = cv2.matchTemplate(img, plantilla, cv2.TM_CCOEFF_NORMED)
    assert mapa.shape == referencia.shape
    assert np.abs(mapa - referencia).max() < 1e-3
    # El máximo vale 1 y cae donde se recortó la plantilla.
    y, x, valor = posicion_del_maximo(mapa)
    assert (y, x) == (30, 70)
    assert abs(valor - 1.0) < 1e-4


def test_correlacion_normalizada_no_cambia_con_brillo_ni_contraste():
    img = textura(60, 80)
    plantilla = img[20:40, 30:50].copy()
    _, _, valor = posicion_del_maximo(correlacion_normalizada(img * 0.5 + 40, plantilla))
    assert abs(valor - 1.0) < 1e-4


def test_correlacion_normalizada_en_zona_lisa_da_cero():
    lisa = np.full((30, 30), 50.0, dtype=np.float32)
    assert np.abs(correlacion_normalizada(lisa, textura(10, 10))).max() == 0


def test_correlacion_de_fase_recupera_desplazamientos_conocidos():
    grande = textura(300, 300)
    anterior = grande[100:260, 100:228]
    for dx, dy in [(5, 3), (-7, 2), (0, 0), (12, -9)]:
        # El contenido de "actual" está movido dx a la derecha y dy hacia abajo.
        actual = grande[100 - dy:260 - dy, 100 - dx:228 - dx]
        dx_medido, dy_medido, _ = correlacion_de_fase(anterior, actual)
        assert (dx_medido, dy_medido) == (dx, dy)


def test_correlacion_de_fase_coincide_con_opencv():
    grande = textura(300, 300)
    anterior = grande[100:260, 100:228]
    actual = grande[97:257, 95:223]            # movido 5 a la derecha y 3 hacia abajo
    dx, dy, _ = correlacion_de_fase(anterior, actual)
    ventana = cv2.createHanningWindow((128, 160), cv2.CV_64F)
    (dx_cv, dy_cv), _ = cv2.phaseCorrelate(anterior.astype(np.float64), actual.astype(np.float64), ventana)
    # OpenCV entrega decimales y la versión propia, pixeles enteros.
    assert abs(dx - dx_cv) < 0.5
    assert abs(dy - dy_cv) < 0.5


def test_correlacion_de_fase_da_pico_bajo_si_las_imagenes_no_se_parecen():
    _, _, pico_igual = correlacion_de_fase(textura(64, 64, 1), textura(64, 64, 1))
    _, _, pico_distinto = correlacion_de_fase(textura(64, 64, 1), textura(64, 64, 2))
    assert pico_igual > 0.9
    assert pico_distinto < 0.2


def test_recortar_y_escalar_coincide_con_warpaffine():
    img = textura(360, 640)
    for caja in [(200.0, 100.0, 96.0, 120.0), (210.3, 95.7, 150.0, 190.0)]:
        x0, y0, ancho, alto = caja
        ex, ey = ancho / 128, alto / 160
        matriz = np.array([[ex, 0, x0 + 0.5 * ex - 0.5], [0, ey, y0 + 0.5 * ey - 0.5]])
        referencia = cv2.warpAffine(img, matriz, (128, 160),
                                    flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                    borderMode=cv2.BORDER_REPLICATE)
        assert np.abs(recortar_y_escalar(img, caja, 128, 160) - referencia).max() < 0.01


def test_recortar_sin_cambiar_de_tamano_entrega_el_mismo_trozo():
    img = textura(360, 640)
    salida = normalizar_rostro(img, (50, 40, 128, 160))
    assert np.abs(salida - img[40:200, 50:178]).max() == 0


def test_una_caja_que_se_sale_de_la_imagen_no_falla():
    img = textura(100, 100)
    assert recortar_y_escalar(img, (-20, -20, 80, 100), 128, 160).shape == (160, 128)


def test_recortes_de_ojos_miden_64_de_ancho():
    izquierdo, derecho = recortes_de_ojos(textura(160, 128))
    assert izquierdo.shape == derecho.shape
    assert izquierdo.shape[1] == 64
