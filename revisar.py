"""
Corre todas las comprobaciones del proyecto, una tras otra.

Uso, desde la raíz del repositorio:

    python revisar.py
    python revisar.py datos\\kaggle\\drowsiness_dataset\\train

Hace cuatro cosas:

  1. Pruebas automáticas (pytest).
  2. Verificación de los algoritmos propios contra OpenCV.
  3. Evaluación de la medida de ojos con las imágenes de Kaggle.
  4. Evaluación por evento del sistema completo, con la escena sintética.

Para el paso 3 hace falta la carpeta del dataset que contiene Open y
Closed. Si no se escribe la ruta, se busca sola dentro de datos/kaggle.
Si no aparece, el paso 3 se salta y los demás corren igual.

Nada de esto entrena un modelo. Solo se calculan números y se cuentan
aciertos, así que tarda unos segundos.
"""

import os
import subprocess
import sys


def buscar_dataset(raiz="datos/kaggle"):
    """Busca dentro de datos/kaggle una carpeta que contenga Open y Closed."""
    if not os.path.isdir(raiz):
        return None
    for carpeta, subcarpetas, _ in os.walk(raiz):
        if "Open" in subcarpetas and "Closed" in subcarpetas:
            return carpeta
    return None


def correr(titulo, argumentos):
    """Corre un paso con el mismo Python que corre este archivo. Entrega True si salió bien."""
    print()
    print("=" * 78)
    print(titulo)
    print("=" * 78)
    resultado = subprocess.run([sys.executable] + argumentos)
    return resultado.returncode == 0


def principal():
    resumen = []

    bien = correr("1 de 4. Pruebas automáticas", ["-m", "pytest", "-q", "pruebas"])
    resumen.append(("Pruebas automáticas", "bien" if bien else "FALLÓ"))

    bien = correr("2 de 4. Algoritmos propios contra OpenCV", ["-m", "verificacion.verificar"])
    resumen.append(("Verificación contra OpenCV", "bien" if bien else "FALLÓ"))

    dataset = sys.argv[1] if len(sys.argv) > 1 else buscar_dataset()
    if dataset is None:
        print()
        print("3 de 4. No se encontró el dataset de Kaggle dentro de datos/kaggle.")
        print("        Para incluirlo: python revisar.py <carpeta que contiene Open y Closed>")
        resumen.append(("Medida de ojos con Kaggle", "no se corrió, falta el dataset"))
    else:
        bien = correr("3 de 4. Medida de ojos con Kaggle (%s)" % dataset,
                      ["-m", "evaluacion.por_cuadro", dataset])
        resumen.append(("Medida de ojos con Kaggle", "bien" if bien else "FALLÓ"))

    bien = correr("4 de 4. Evaluación por evento con la escena sintética",
                  ["-m", "evaluacion.demostracion"])
    resumen.append(("Evaluación por evento", "bien" if bien else "FALLÓ"))

    print()
    print("=" * 78)
    print("Resumen")
    print("=" * 78)
    for nombre, estado in resumen:
        print("  %-30s %s" % (nombre, estado))

    if any(estado == "FALLÓ" for _, estado in resumen):
        print()
        print("Si falló el paso 1 con 'No module named pytest', falta instalar:")
        print("    pip install -r requirements-dev.txt")
        sys.exit(1)


if __name__ == "__main__":
    principal()
