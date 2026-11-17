"""
Parámetros del sistema.

Todos los umbrales y tamaños viven en este archivo. Ningún otro módulo debe
llevar números escritos a mano. Cada valor dice de dónde sale.

La primera parte son valores que fija el enunciado del proyecto y no se
ajustan. La segunda parte son valores que eligió el equipo. Los que dicen
"por ajustar" se afinan con los videos de ajuste, nunca con los de evaluación.
"""

# ---------------------------------------------------------------------------
# Valores que fija el enunciado
# ---------------------------------------------------------------------------

# Tabla 1 del enunciado. Un cierre de ojos es:
#   parpadeo normal  si  t <= 0.5 s
#   parpadeo lento   si  0.5 s < t <= 7 s
#   microsueño       si  t > 7 s
PARPADEO_NORMAL_MAX_S = 0.5
PARPADEO_LENTO_MAX_S = 7.0      # criterio de la referencia [3] del enunciado

# Bandas de duración de los episodios de distracción (enunciado).
# Interpretación del equipo (decisión D10): cada número es el inicio de una
# banda, y un episodio menor a la primera no se cuenta.
BANDAS_DISTRACCION_S = (0.5, 1.0, 1.5, 2.0)

# PERCLOS: ventana deslizante y umbrales de alerta, fatiga y somnolencia.
PERCLOS_VENTANA_S = 30.0
PERCLOS_ALERTA = 0.08
PERCLOS_FATIGA = 0.15
PERCLOS_SOMNOLENCIA = 0.30

# Tiempo de cierre en curso a partir del cual se avisa al conductor.
# Es el umbral de alerta de la referencia [1] del enunciado.
AVISO_CIERRE_EN_CURSO_S = 1.5

# ---------------------------------------------------------------------------
# Valores que fija el equipo
# ---------------------------------------------------------------------------

# Decisión D09 (pendiente de confirmar con los profesores).
# False: PERCLOS solo cuenta los cierres que duran más de 0.5 s.
# True:  PERCLOS cuenta todo cierre, incluidos los parpadeos normales.
PERCLOS_CUENTA_PARPADEOS_NORMALES = False

# Antes de reunir este tiempo de datos válidos, PERCLOS no se reporta.
# Con dos segundos de datos, un solo cierre daría 50%.
PERCLOS_TIEMPO_MINIMO_S = 10.0

# Decisión D11 (provisional, falta una fuente).
# La boca debe estar abierta al menos este tiempo para contar un bostezo.
BOSTEZO_MIN_S = 1.5

# Decisión D15. Umbral doble para los ojos, sobre la apertura (0 a 1).
# Se declara cerrado al bajar de 0.20, es decir 80% cerrado respecto a la
# calibración. Se declara abierto de nuevo al subir de 0.35.
OJOS_UMBRAL_CIERRE = 0.20
OJOS_UMBRAL_REAPERTURA = 0.35

# Medida de los ojos (somnolencia/percepcion/gradiente.py).
# Se validó con recortes de un ojo de 64 pixeles de ancho, sin la ceja.
OJOS_ANCHO_DE_RECORTE = 64      # ancho al que se lleva cada ojo antes de medir
OJOS_FRACCION_SIN_CEJA = 0.30   # parte superior del recorte que se descarta
OJOS_COLUMNA_INICIAL = 0.20     # columnas centrales que se usan, como fracción
OJOS_COLUMNA_FINAL = 0.80       # del ancho del recorte
OJOS_ALTO_DE_BANDA = 5          # renglones de la banda más oscura
OJOS_MARGEN_DE_BANDA = 4        # renglones extra arriba y abajo de la banda

# Valores de la razón de bordes cuando no hay calibración de la persona.
# Son las medianas medidas en los 1452 recortes de ojos del dataset de Kaggle
# (726 abiertos y 726 cerrados).
# Con calibración se usan en su lugar los valores de la propia persona.
OJOS_RAZON_ABIERTO = 0.72
OJOS_RAZON_CERRADO = 0.41

# Umbral doble para la boca, sobre su apertura (0 a 1). Por ajustar.
BOCA_UMBRAL_APERTURA = 0.20
BOCA_UMBRAL_CIERRE = 0.14

# Umbral doble para la cabeza, sobre la frontalidad (0 a 1). Por ajustar.
# Se declara distraído al bajar de 0.50 y atento de nuevo al subir de 0.60.
CABEZA_UMBRAL_DISTRAIDO = 0.50
CABEZA_UMBRAL_ATENTO = 0.60

# Decisión D16. Si en medio de un evento aparecen hasta este número de
# cuadros seguidos en el estado contrario, se toman como ruido y el evento
# continúa.
ANTIRREBOTE_CUADROS = 2

# Si durante un evento se pierde el dato más de este tiempo, el evento se
# cierra como indeterminado y no entra a ningún contador.
SIN_DATO_TOLERANCIA_S = 0.3

# Duración de una distracción en curso para dar aviso y para dar alerta.
ALERTA_DISTRACCION_AVISO_S = 1.0
ALERTA_DISTRACCION_ALERTA_S = 2.0

# Decisión D18. Tamaños de imagen.
GRABACION_ANCHO, GRABACION_ALTO = 1280, 720   # tamaño de los videos
TRABAJO_ANCHO, TRABAJO_ALTO = 640, 360        # tamaño al que procesa el sistema
ROSTRO_ANCHO, ROSTRO_ALTO = 128, 160          # rostro normalizado
PIRAMIDE_NIVELES = 3
BUSQUEDA_VENTANA_PX = 8                       # en el nivel más pequeño de la pirámide

# Dónde se recortan los ojos dentro del rostro normalizado, como fracción de
# su alto. Provisional: se ajusta con los videos de ajuste.
OJOS_FILA_INICIAL = 0.22
OJOS_FILA_FINAL = 0.52

# Seguimiento del rostro (somnolencia/percepcion/rostro.py).
# La plantilla usa solo la parte de arriba de la caja del rostro (frente,
# ojos y nariz). Se deja fuera la boca para que un bostezo no haga que el
# rostro deje de parecerse a su plantilla. Provisional (decisión D32).
PLANTILLA_FRACCION_ALTO = 0.65
AFINADO_VENTANA_PX = 2          # ventana de búsqueda al afinar en el nivel intermedio
REBUSCAR_CADA_CUADROS = 5       # con el rostro perdido, cada cuántos cuadros se busca en toda la imagen
FASE_PICO_MINIMO = 0.15         # pico mínimo de la correlación de fase para creerle al movimiento

# Recuadro donde la persona coloca la cara al calibrar con cámara, en
# pixeles del tamaño de trabajo. Queda centrado. Provisional.
RECUADRO_ANCHO, RECUADRO_ALTO = 110, 138

# Medida de la boca (somnolencia/percepcion/boca.py). SIN VALIDAR (decisión D31).
BOCA_FILA_INICIAL = 0.68        # franja de la boca dentro del rostro normalizado,
BOCA_FILA_FINAL = 0.98          # como fracción de su alto
BOCA_COLUMNA_INICIAL = 0.25     # columnas centrales, como fracción del ancho
BOCA_COLUMNA_FINAL = 0.75

# Decisión D25. Calibración en dos pasos.
CALIBRACION_ABIERTOS_S = 3.0
CALIBRACION_CERRADOS_S = 2.0
# Al inicio de cada paso se descarta este tiempo, mientras la persona reacciona.
CALIBRACION_MARGEN_S = 0.5
# Si la razón de ojos abiertos y la de ojos cerrados quedan más cerca que
# esto, la calibración de ojos no sirve y se usan las referencias generales.
CALIBRACION_DIFERENCIA_MINIMA = 0.10

# Núcleo del filtro binomial de la práctica 5 (se divide entre su suma, 16).
NUCLEO_BINOMIAL = (1, 4, 6, 4, 1)
