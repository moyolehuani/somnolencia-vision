"""
Bitácora: guarda en un archivo CSV cada evento que termina.

Columnas: tipo, inicio_s, fin_s, duracion_s, categoria. Son las mismas de
los archivos de anotaciones, para poder comparar unos con otros.

Junto a la bitácora se guarda un archivo de texto con los parámetros de
config.py que estaban vigentes y la fuente usada. Así se sabe con qué
valores se obtuvo cada resultado.

La bitácora no guarda imágenes ni video.

BitacoraDeMediciones guarda, además, una fila por cuadro con las tres
mediciones, los estados, PERCLOS y la alerta. Sirve para ajustar umbrales
y para las gráficas del reporte. Se activa con la opción --mediciones.
"""

import csv
import os
import time

from somnolencia import config


class Bitacora:

    def __init__(self, carpeta="salidas", fuente=""):
        os.makedirs(carpeta, exist_ok=True)
        marca = time.strftime("%Y%m%d_%H%M%S")
        self.marca = marca      # la usa la bitácora de mediciones para llevar el mismo nombre
        self.ruta = os.path.join(carpeta, "bitacora_%s.csv" % marca)
        self._archivo = open(self.ruta, "w", newline="", encoding="utf-8")
        self._escritor = csv.writer(self._archivo)
        self._escritor.writerow(["tipo", "inicio_s", "fin_s", "duracion_s", "categoria"])

        # Copia de los parámetros vigentes.
        with open(os.path.join(carpeta, "parametros_%s.txt" % marca), "w", encoding="utf-8") as f:
            f.write("fuente = %s\n" % fuente)
            for nombre in sorted(dir(config)):
                if nombre.isupper():
                    f.write("%s = %r\n" % (nombre, getattr(config, nombre)))

    def guardar(self, eventos):
        """Escribe una lista de eventos (puede estar vacía)."""
        for evento in eventos:
            self._escritor.writerow([evento.tipo, "%.3f" % evento.inicio, "%.3f" % evento.fin,
                                     "%.3f" % evento.duracion, evento.categoria])
        self._archivo.flush()

    def cerrar(self):
        self._archivo.close()


# Columnas del archivo de mediciones, en orden. Todas salen del diccionario
# "resumen" que entrega Sistema.procesar.
COLUMNAS_DE_MEDICIONES = [
    "t", "fase", "valor_ojos", "valor_boca", "valor_cabeza", "razon_ojos", "puntaje",
    "estado_ojos", "estado_boca", "estado_cabeza", "perclos", "nivel_perclos", "alerta",
]


class BitacoraDeMediciones:
    """Guarda una fila por cuadro con las mediciones y los estados."""

    def __init__(self, carpeta="salidas", marca=None):
        os.makedirs(carpeta, exist_ok=True)
        marca = marca or time.strftime("%Y%m%d_%H%M%S")
        self.ruta = os.path.join(carpeta, "mediciones_%s.csv" % marca)
        self._archivo = open(self.ruta, "w", newline="", encoding="utf-8")
        self._escritor = csv.writer(self._archivo)
        self._escritor.writerow(COLUMNAS_DE_MEDICIONES)

    def guardar(self, resumen):
        """Escribe la fila de un cuadro. Lo que no hay en ese cuadro queda vacío."""
        fila = []
        for columna in COLUMNAS_DE_MEDICIONES:
            valor = resumen.get(columna)
            if valor is None:
                fila.append("")
            elif isinstance(valor, float):
                fila.append("%.4f" % valor)
            else:
                fila.append(str(valor))
        self._escritor.writerow(fila)

    def cerrar(self):
        self._archivo.close()
