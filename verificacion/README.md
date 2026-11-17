# `verificacion/`

Aquí se demuestra que cada algoritmo propio hace lo mismo que su equivalente de OpenCV. El enunciado lo permite de forma expresa: las funciones predefinidas pueden usarse como referencia para verificar las implementaciones. Esta carpeta es la evidencia directa del criterio que más pesa en la rúbrica (35%).

Nada de esta carpeta se ejecuta durante la demo.

## `verificar.py` (escrito)

Compara todos los algoritmos propios contra OpenCV y mide cuánto tarda cada uno. Se corre desde la raíz del repositorio:

```bash
python -m verificacion.verificar
```

Imprime una tabla con un renglón por comparación:

| Algoritmo propio | Se compara contra |
|---|---|
| `suavizar_binomial` | `cv2.GaussianBlur` |
| `gradiente_vertical`, `gradiente_horizontal` | `cv2.Sobel` |
| `reducir` (pirámide) | `cv2.pyrDown` |
| `especificar_histograma` | `cv2.equalizeHist` y el histograma acumulado objetivo |
| `correlacion_normalizada` | `cv2.matchTemplate` |
| `correlacion_de_fase` | Desplazamientos conocidos y `cv2.phaseCorrelate` |
| `recortar_y_escalar` | `cv2.warpAffine` |

Los resultados de la primera corrida están en `docs/evaluacion.md`, en la tabla del nivel 1.

Las imágenes de prueba son texturas generadas con números al azar y semilla fija. No se usa ninguna imagen de un rostro, así que todo lo de esta carpeta puede subirse.

El programa importa las funciones desde el paquete `somnolencia`. No copia su código. Así se verifica lo mismo que corre en el sistema.

Las mismas comparaciones, en versión corta, están en `pruebas/test_percepcion.py` y se revisan cada vez que se corre `pytest`.

## Qué falta

- [ ] Correr `verificar.py` en el equipo de la demo y actualizar los tiempos de `docs/evaluacion.md`.
- [ ] Figuras para el reporte. Para cada algoritmo conviene una figura con la entrada, el resultado propio, el de OpenCV y la diferencia. Se pueden hacer en un cuaderno de Jupyter que llame a las mismas funciones. Si se usan cuadernos, se suben sin salidas.

## Hecho cuando

La tabla del nivel 1 de `docs/evaluacion.md` tiene los tiempos del equipo de la demo y el reporte tiene una figura por algoritmo.
