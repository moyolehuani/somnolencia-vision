"""
El sistema completo, cuadro por cuadro.

La clase Sistema junta la percepción y la capa temporal. No sabe nada de
cámaras, archivos ni ventanas: recibe un cuadro en grises, ya en el tamaño
de trabajo (640x360), con su marca de tiempo, y entrega un diccionario con
todo lo que pasó en ese cuadro. Así el mismo código sirve para la cámara,
para un video, para la evaluación y para las pruebas.

Uso:

    sistema = Sistema()
    sistema.iniciar(gris, caja, t)          # una vez, con la caja del rostro
    resumen = sistema.procesar(gris, t)     # en cada cuadro
    eventos_finales = sistema.terminar(t)   # al acabar

Fases. Después de iniciar viene la calibración: 3 s con los ojos abiertos
y 2 s con los ojos cerrados. Durante esos 5 s no se cuentan eventos.
Después empieza la vigilancia. Si se inicia sin calibración (por ejemplo
con un video que no la trae), la vigilancia empieza de inmediato y los
ojos usan las referencias generales de config.py.
"""

from dataclasses import dataclass

import numpy as np

from somnolencia import config
from somnolencia.tipos import Medicion
from somnolencia.percepcion.piramide import piramide_gaussiana
from somnolencia.percepcion.preproceso import (
    histograma_acumulado, tabla_de_especificacion, aplicar_tabla,
)
from somnolencia.percepcion.geometria import normalizar_rostro, recortes_de_ojos
from somnolencia.percepcion.rostro import SeguidorDeRostro
from somnolencia.percepcion.ojos import razon_de_un_ojo, medir_ojos
from somnolencia.percepcion.boca import umbral_oscuro_en_reposo, medida_de_boca, medir_boca
from somnolencia.percepcion.cabeza import medir_cabeza
from somnolencia.temporal.capa import CapaTemporal

CALIBRANDO = "calibrando"


def zona_estable(rostro):
    """
    Parte de arriba del rostro normalizado (frente, ojos y nariz). Su
    contenido casi no cambia durante la sesión, así que sus cambios de
    brillo se deben a la luz. Con ella se mide la iluminación.
    """
    return rostro[:int(config.PLANTILLA_FRACCION_ALTO * rostro.shape[0]), :]
VIGILANDO = "vigilando"


@dataclass
class Calibracion:
    """Lo que el sistema aprende de la persona al inicio de la sesión."""
    acumulado_ref: np.ndarray       # histograma acumulado de la zona estable del rostro de referencia
    razon_abierto: float            # medida de ojos con los ojos abiertos
    razon_cerrado: float            # medida de ojos con los ojos cerrados
    boca_umbral_oscuro: float       # nivel de gris que cuenta como "oscuro" en la boca
    boca_en_reposo: float           # medida de la boca cerrada
    aviso: str = ""                 # mensaje si algo de la calibración no salió bien


class Sistema:

    def __init__(self):
        self.seguidor = None
        self.calibracion = None
        self.capa = CapaTemporal()
        self.fase = None
        self.t_calibracion = None       # cuándo empezó la calibración
        self._razones_abiertos = []     # medidas reunidas durante la calibración
        self._razones_cerrados = []
        self._bocas_en_reposo = []

    # ----- Inicio ---------------------------------------------------------------

    def iniciar(self, gris, caja, t, con_calibracion=True):
        """
        Fija el rostro de referencia.

        gris              cuadro en grises, en el tamaño de trabajo
        caja              (x, y, ancho, alto) del rostro en ese cuadro
        t                 marca de tiempo del cuadro
        con_calibracion   False para empezar a vigilar de inmediato
        """
        piramide = piramide_gaussiana(gris, config.PIRAMIDE_NIVELES)
        self.seguidor = SeguidorDeRostro(piramide, caja)

        rostro = normalizar_rostro(gris, self.seguidor.caja)
        umbral = umbral_oscuro_en_reposo(rostro)
        self.calibracion = Calibracion(
            acumulado_ref=histograma_acumulado(zona_estable(rostro)),
            razon_abierto=config.OJOS_RAZON_ABIERTO,
            razon_cerrado=config.OJOS_RAZON_CERRADO,
            boca_umbral_oscuro=umbral,
            boca_en_reposo=medida_de_boca(rostro, umbral),
        )
        self.t_calibracion = t
        self.fase = CALIBRANDO if con_calibracion else VIGILANDO

    # ----- Un cuadro --------------------------------------------------------------

    def procesar(self, gris, t):
        """Procesa un cuadro y entrega el resumen de lo que pasó en él."""
        cal = self.calibracion

        # 1. Pirámide y seguimiento del rostro.
        piramide = piramide_gaussiana(gris, config.PIRAMIDE_NIVELES)
        caja, puntaje, movimiento = self.seguidor.seguir(piramide)
        medicion_cabeza = medir_cabeza(puntaje, t)

        # 2. Los ojos y la boca solo se miden si el rostro está de frente.
        #    Si no, quedan sin dato: no se inventa una medición.
        de_frente = medicion_cabeza.valor >= config.CABEZA_UMBRAL_DISTRAIDO
        razon_ojos, boca_bruta, rostro = None, None, None
        medicion_ojos = Medicion(t, 0.0, False)
        medicion_boca = Medicion(t, 0.0, False)
        if de_frente:
            rostro = normalizar_rostro(gris, caja)
            # Ojos: sobre el rostro tal cual. La medida es un cociente y no
            # depende del brillo ni del contraste.
            ojo_izquierdo, ojo_derecho = recortes_de_ojos(rostro)
            razon_ojos = (razon_de_un_ojo(ojo_izquierdo) + razon_de_un_ojo(ojo_derecho)) / 2
            medicion_ojos = medir_ojos(ojo_izquierdo, ojo_derecho, t,
                                       cal.razon_abierto, cal.razon_cerrado)
            # Boca: usa un umbral de gris fijo, así que primero se corrige
            # la iluminación. La tabla de especificación se arma con la zona
            # estable del rostro y se aplica al rostro completo. Si se armara
            # con el rostro completo, una boca abierta (más pixeles oscuros)
            # se "corregiría" como si fuera un cambio de luz.
            tabla = tabla_de_especificacion(zona_estable(rostro), cal.acumulado_ref)
            rostro_especificado = aplicar_tabla(rostro, tabla)
            boca_bruta = medida_de_boca(rostro_especificado, cal.boca_umbral_oscuro)
            medicion_boca = medir_boca(rostro_especificado, t,
                                       cal.boca_umbral_oscuro, cal.boca_en_reposo)

        resumen = {
            "t": t, "fase": self.fase, "caja": caja, "puntaje": puntaje,
            "movimiento": movimiento,
            "valor_ojos": medicion_ojos.valor if medicion_ojos.valido else None,
            "valor_boca": medicion_boca.valor if medicion_boca.valido else None,
            "valor_cabeza": medicion_cabeza.valor,
            "razon_ojos": razon_ojos,
            "rostro": rostro,           # rostro normalizado, para la vista de depuración
            "aviso": cal.aviso,
        }

        # 3. Durante la calibración solo se reúnen medidas.
        if self.fase == CALIBRANDO:
            resumen["instruccion"] = self._calibrar(t, razon_ojos, boca_bruta)
            return resumen

        # 4. Vigilancia: estados, eventos, PERCLOS y alertas.
        resumen.update(self.capa.actualizar(t, medicion_ojos, medicion_boca, medicion_cabeza))
        return resumen

    def terminar(self, t):
        """Al acabar: cierra los eventos que quedaron abiertos y los entrega."""
        return self.capa.terminar(t)

    # ----- Calibración ---------------------------------------------------------------

    def _calibrar(self, t, razon_ojos, boca_bruta):
        """
        Reúne las medidas de los dos pasos de la calibración y, al terminar
        el segundo, fija las referencias. Entrega la instrucción a mostrar.
        """
        transcurrido = t - self.t_calibracion
        fin_abiertos = config.CALIBRACION_ABIERTOS_S
        fin_cerrados = fin_abiertos + config.CALIBRACION_CERRADOS_S
        margen = config.CALIBRACION_MARGEN_S

        if transcurrido < fin_abiertos:
            # Paso 1: ojos abiertos y boca cerrada.
            if razon_ojos is not None and transcurrido >= margen:
                self._razones_abiertos.append(razon_ojos)
                self._bocas_en_reposo.append(boca_bruta)
            return "Mira al frente con los ojos abiertos"

        if transcurrido < fin_cerrados:
            # Paso 2: ojos cerrados.
            if razon_ojos is not None and transcurrido >= fin_abiertos + margen:
                self._razones_cerrados.append(razon_ojos)
            return "Cierra los ojos"

        self._fijar_referencias()
        self.fase = VIGILANDO
        return "Listo"

    def _fijar_referencias(self):
        cal = self.calibracion
        if self._bocas_en_reposo:
            cal.boca_en_reposo = float(np.median(self._bocas_en_reposo))

        # Se usa la mediana: un parpadeo durante el paso de ojos abiertos no
        # arruina la referencia.
        if len(self._razones_abiertos) >= 3 and len(self._razones_cerrados) >= 3:
            abierto = float(np.median(self._razones_abiertos))
            cerrado = float(np.median(self._razones_cerrados))
            if abierto - cerrado >= config.CALIBRACION_DIFERENCIA_MINIMA:
                cal.razon_abierto, cal.razon_cerrado = abierto, cerrado
                return
        # Si no hubo suficientes cuadros, o abiertos y cerrados dieron casi
        # lo mismo, se dejan las referencias generales y se avisa.
        cal.aviso = "Calibracion de ojos no confiable: se usan referencias generales"
