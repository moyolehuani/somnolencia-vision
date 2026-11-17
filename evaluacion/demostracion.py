"""
Demostración de la evaluación completa, con la escena sintética.

Uso, desde la raíz del repositorio:

    python -m evaluacion.demostracion

Hace con la cara dibujada lo mismo que se hará con cada video real:

  1. Corre el sistema sobre el video y guarda la bitácora de eventos y
     las mediciones cuadro por cuadro.
  2. Toma las anotaciones del video. Aquí salen del guion de la escena.
     Con un video real las escribe una persona.
  3. Compara la bitácora contra las anotaciones e imprime las métricas.

Los archivos quedan en salidas/demostracion/, para verlos como ejemplo
del formato. Con la escena todo debe salir perfecto. Eso comprueba que la
evaluación está bien armada, no que el sistema funcione con personas.
"""

import csv
import os

from somnolencia import escena_sintetica as escena
from somnolencia.sistema import Sistema
from somnolencia.interfaz.bitacora import Bitacora, BitacoraDeMediciones
from evaluacion.por_evento import leer_eventos, imprimir_reporte

CARPETA = os.path.join("salidas", "demostracion")


def principal():
    os.makedirs(CARPETA, exist_ok=True)

    # 1. Correr el sistema y guardar sus salidas.
    bitacora = Bitacora(CARPETA, "escena")
    mediciones = BitacoraDeMediciones(CARPETA, bitacora.marca)
    sistema = Sistema()
    for t, gris in escena.generar():
        if sistema.seguidor is None:
            sistema.iniciar(gris, escena.caja_inicial(), t)
        resumen = sistema.procesar(gris, t)
        bitacora.guardar(resumen.get("eventos_nuevos", []))
        mediciones.guardar(resumen)
    bitacora.guardar(sistema.terminar(t))
    bitacora.cerrar()
    mediciones.cerrar()

    # 2. Escribir las anotaciones, con el formato de datos/README.md.
    ruta_de_anotaciones = os.path.join(CARPETA, "anotaciones_escena.csv")
    with open(ruta_de_anotaciones, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["tipo", "inicio_s", "fin_s", "notas"])
        for tipo, inicio, fin in escena.anotaciones():
            escritor.writerow([tipo, "%.2f" % inicio, "%.2f" % fin, "guion de la escena"])

    # 3. Comparar e imprimir.
    imprimir_reporte(leer_eventos(ruta_de_anotaciones), leer_eventos(bitacora.ruta), mediciones.ruta)
    print()
    print("Archivos de ejemplo en", CARPETA)


if __name__ == "__main__":
    principal()
