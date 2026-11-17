"""
Pruebas que vigilan las reglas del repositorio.

Leen el texto de los archivos de somnolencia/ y fallan si alguno rompe una
regla. Son la respuesta a "¿cómo garantizan que el sistema no depende de
una red ni de funciones ya hechas?".
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PAQUETE = RAIZ / "somnolencia"

# Bibliotecas de redes y detectores ya entrenados. No se usan en el proyecto.
REDES_Y_DETECTORES = [
    "mediapipe", "dlib", "torch", "tensorflow", "keras",
    "cv2.dnn", "CascadeClassifier",
]

# Funciones de OpenCV equivalentes a los algoritmos propios. Solo pueden
# aparecer en verificacion/, nunca dentro de percepcion/.
EQUIVALENTES_DE_OPENCV = [
    "cv2.GaussianBlur", "cv2.Sobel", "cv2.equalizeHist", "cv2.pyrDown",
    "cv2.matchTemplate", "cv2.phaseCorrelate", "cv2.warpAffine", "cv2.resize",
]


def archivos_py(carpeta):
    return sorted(carpeta.rglob("*.py"))


def lineas_de_codigo(ruta):
    """Líneas del archivo sin los comentarios, para no fallar por una mención."""
    lineas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        lineas.append(linea.split("#")[0])
    return lineas


def test_el_sistema_no_usa_redes_ni_detectores_entrenados():
    for ruta in archivos_py(PAQUETE):
        for linea in lineas_de_codigo(ruta):
            for prohibido in REDES_Y_DETECTORES:
                assert prohibido not in linea, "%s usa %s" % (ruta.name, prohibido)


def test_percepcion_no_usa_las_funciones_equivalentes_de_opencv():
    for ruta in archivos_py(PAQUETE / "percepcion"):
        for linea in lineas_de_codigo(ruta):
            for prohibido in EQUIVALENTES_DE_OPENCV:
                assert prohibido not in linea, "%s usa %s" % (ruta.name, prohibido)


def test_la_capa_temporal_no_importa_opencv():
    for ruta in archivos_py(PAQUETE / "temporal"):
        for linea in lineas_de_codigo(ruta):
            assert "cv2" not in linea, "%s menciona cv2" % ruta.name
