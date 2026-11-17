"""
Seguimiento del rostro.

El rostro no se detecta: se sigue. Al calibrar se guarda una plantilla de
la cara de frente, y en cada cuadro se busca dónde quedó esa plantilla,
cerca de donde estaba en el cuadro anterior.

La búsqueda va de grueso a fino sobre la pirámide:

  1. Predicción. La correlación de fase entre el cuadro anterior y el
     actual dice hacia dónde se movió la cabeza. La búsqueda se centra ahí.
  2. Búsqueda gruesa en el nivel más pequeño (160x90), en una ventana de
     unos cuantos pixeles alrededor de la predicción.
  3. Afinado en el nivel intermedio (320x180), en una ventana de 2 pixeles.

La comparación se hace sobre la banda laplaciana, que conserva bordes y
detalles y depende poco de la iluminación.

El puntaje de la búsqueda gruesa (entre -1 y 1) dice cuánto se parece lo
encontrado a la plantilla de frente. Cuando la persona voltea, baja. Ese
mismo número es la señal de distracción.

Limitaciones: la plantilla no cambia de tamaño, así que la persona debe
quedarse más o menos a la misma distancia de la cámara. Y la plantilla no
se actualiza durante la sesión. Si se actualizara, poco a poco dejaría de
ser un rostro de frente y el puntaje ya no significaría "volteó".
"""

from somnolencia import config
from somnolencia.percepcion.piramide import banda_laplaciana
from somnolencia.percepcion.correlacion import (
    correlacion_normalizada, posicion_del_maximo, correlacion_de_fase,
)


def recortar(img, x, y, ancho, alto):
    """Recorte simple, sin cambiar de tamaño."""
    return img[y:y + alto, x:x + ancho]


def buscar_cerca(banda, plantilla, centro_x, centro_y, ventana):
    """
    Busca la plantilla alrededor de (centro_x, centro_y), a lo más "ventana"
    pixeles en cada dirección. Entrega (x, y, puntaje) del mejor lugar.
    """
    alto_p, ancho_p = plantilla.shape
    alto_img, ancho_img = banda.shape
    # Zona de la imagen que cubre todas las posiciones a probar, sin salirse.
    x_ini = max(0, centro_x - ventana)
    y_ini = max(0, centro_y - ventana)
    x_fin = min(ancho_img, centro_x + ventana + ancho_p)
    y_fin = min(alto_img, centro_y + ventana + alto_p)
    if x_fin - x_ini < ancho_p or y_fin - y_ini < alto_p:
        return centro_x, centro_y, 0.0      # la plantilla no cabe ahí
    mapa = correlacion_normalizada(banda[y_ini:y_fin, x_ini:x_fin], plantilla)
    y, x, puntaje = posicion_del_maximo(mapa)
    return x_ini + x, y_ini + y, puntaje


class SeguidorDeRostro:

    def __init__(self, piramide, caja):
        """
        piramide   lista de 3 niveles del cuadro de calibración
        caja       (x, y, ancho, alto) del rostro en el nivel más grande
        """
        x, y, ancho, alto = [int(round(v)) for v in caja]
        self.caja = (x, y, ancho, alto)
        # La plantilla usa solo la parte de arriba del rostro (sin la boca).
        alto_plantilla = int(config.PLANTILLA_FRACCION_ALTO * alto)

        media, chica = piramide[1], piramide[2]
        # En el nivel intermedio todo mide la mitad. En el más pequeño, la cuarta parte.
        self.plantilla_media = recortar(banda_laplaciana(media),
                                        x // 2, y // 2, ancho // 2, alto_plantilla // 2).copy()
        self.plantilla_chica = recortar(banda_laplaciana(chica),
                                        x // 4, y // 4, ancho // 4, alto_plantilla // 4).copy()

        self.chica_anterior = chica     # para medir el movimiento entre cuadros
        self.cuadros_perdido = 0        # cuadros seguidos sin encontrar el rostro

    def seguir(self, piramide):
        """
        Busca el rostro en un cuadro nuevo.

        Entrega (caja, puntaje, movimiento):
            caja        (x, y, ancho, alto) en el nivel más grande. Si el
                        rostro no se encontró, es la última caja buena.
            puntaje     parecido con la plantilla de frente, entre -1 y 1
            movimiento  (dx, dy) estimado de la cabeza, en pixeles del nivel
                        más grande
        """
        media, chica = piramide[1], piramide[2]
        banda_media = banda_laplaciana(media)
        banda_chica = banda_laplaciana(chica)
        x, y, ancho, alto = self.caja
        x_chica, y_chica = x // 4, y // 4

        # 1. Predicción del movimiento con correlación de fase, comparando la
        #    zona del rostro en el cuadro anterior y en el actual.
        dx, dy = 0, 0
        zona_anterior = recortar(self.chica_anterior, x_chica, y_chica, ancho // 4, alto // 4)
        zona_actual = recortar(chica, x_chica, y_chica, ancho // 4, alto // 4)
        if zona_anterior.shape == zona_actual.shape and zona_actual.size > 0:
            dx_fase, dy_fase, pico = correlacion_de_fase(zona_anterior, zona_actual)
            if pico >= config.FASE_PICO_MINIMO:
                dx, dy = dx_fase, dy_fase
        self.chica_anterior = chica

        # 2. Búsqueda gruesa alrededor de la posición predicha.
        x_g, y_g, puntaje = buscar_cerca(banda_chica, self.plantilla_chica,
                                         x_chica + dx, y_chica + dy,
                                         config.BUSQUEDA_VENTANA_PX)

        # 3. Si no apareció cerca, cada cierto número de cuadros se busca en
        #    toda la imagen pequeña. Es lento, y por eso no se hace siempre.
        if puntaje < config.CABEZA_UMBRAL_DISTRAIDO:
            self.cuadros_perdido += 1
            if self.cuadros_perdido % config.REBUSCAR_CADA_CUADROS == 0:
                mapa = correlacion_normalizada(banda_chica, self.plantilla_chica)
                y_g, x_g, puntaje = posicion_del_maximo(mapa)

        # 4. Si se encontró, se afina la posición en el nivel intermedio y se
        #    actualiza la caja. Si no, la caja se queda donde estaba, para
        #    reencontrar el rostro ahí mismo cuando la persona regrese.
        if puntaje >= config.CABEZA_UMBRAL_DISTRAIDO:
            self.cuadros_perdido = 0
            x_m, y_m, _ = buscar_cerca(banda_media, self.plantilla_media,
                                       2 * x_g, 2 * y_g, config.AFINADO_VENTANA_PX)
            self.caja = (2 * x_m, 2 * y_m, ancho, alto)

        return self.caja, puntaje, (4 * dx, 4 * dy)
