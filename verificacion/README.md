# `verificacion/`

Aquí se demuestra que cada algoritmo propio hace lo mismo que su equivalente de OpenCV. El enunciado lo permite de forma expresa: las funciones predefinidas pueden usarse como referencia para verificar las implementaciones. Esta carpeta es la evidencia directa del criterio que más pesa en la rúbrica (35%).

Nada de esta carpeta se ejecuta durante la demo.

## Qué debe ir aquí

Un cuaderno de Jupyter por algoritmo. Cada frente hace los suyos.

| Cuaderno | Algoritmo propio | Se compara contra | Frente |
|---|---|---|---|
| `01_suavizado_binomial.ipynb` | `preproceso.suavizar_binomial` | `cv2.GaussianBlur` | 2 |
| `02_especificacion_histograma.ipynb` | `preproceso.especificar_histograma` | Histograma acumulado objetivo | 2 |
| `03_gradiente_vertical.ipynb` | `gradiente.gradiente_vertical` | `cv2.Sobel` | 2 |
| `04_piramide.ipynb` | `piramide.reducir` | `cv2.pyrDown` | 1 |
| `05_correlacion_normalizada.ipynb` | `correlacion.correlacion_normalizada` | `cv2.matchTemplate` | 1 |
| `06_mapeo_inverso.ipynb` | `geometria.normalizar_rostro` | `cv2.warpAffine` | 1 |
| `07_correlacion_de_fase.ipynb` | `correlacion.correlacion_de_fase` | Desplazamiento conocido y `cv2.phaseCorrelate` | 3 |

## Estructura de cada cuaderno

Todos siguen el mismo orden, para que sean fáciles de leer y de pasar al reporte:

1. **Qué se verifica.** Una frase.
2. **Entrada de prueba.** Una imagen que no sea un rostro: un patrón sintético (tablero, rampas, líneas) o una imagen de las prácticas. Así el cuaderno puede subirse sin datos personales.
3. **Resultado propio.** Se llama a la función del paquete `somnolencia`.
4. **Resultado de referencia.** Se llama a la función de OpenCV con parámetros equivalentes, y se anota cuáles son.
5. **Comparación.** Diferencia máxima y diferencia media, más una imagen de la diferencia.
6. **Explicación de las diferencias.** Casi siempre están en los bordes, porque cada implementación los trata distinto. Si la diferencia está solo ahí, se dice y se muestra la comparación sin la orilla.
7. **Tiempo.** Cuánto tarda la versión propia y cuánto la de OpenCV sobre el tamaño de imagen que se usa en el sistema.
8. **Conclusión.** Una línea que va a la tabla de `docs/evaluacion.md`.

El punto 7 alimenta la discusión de compromisos entre complejidad y velocidad que pide el enunciado. Que la versión propia sea más lenta es normal y se reporta sin problema.

## Reglas

- Los cuadernos importan las funciones desde el paquete. No se copia el código al cuaderno, porque entonces se verificaría una copia y no lo que corre en el sistema.
- Se suben sin salidas (Kernel, "Restart & Clear Output"). Las figuras para el reporte se exportan aparte.
- No se usan imágenes de rostros.

## Hecho cuando

Los siete cuadernos corren de principio a fin sin errores y la tabla del nivel 1 en `docs/evaluacion.md` está llena.
