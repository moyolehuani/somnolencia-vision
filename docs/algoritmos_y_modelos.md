# Algoritmos y modelos

## Qué cuenta como "modelo" en este proyecto

No hay red neuronal dentro del sistema y no hace falta. El enunciado pide al menos cuatro algoritmos de visión computacional vistos en clase e implementados por el equipo, y califica con 5 un sistema que sea solo una red.

Lo que en otros sistemas hace una red, aquí lo hace una cadena de algoritmos clásicos cuyos pasos se pueden mostrar uno por uno. Esa es también la ventaja para la defensa: ante cualquier resultado se puede enseñar la imagen intermedia que lo produjo.

## Algoritmos propios

Estos son los que se presentan como "implementados por el equipo". Todos vienen de las prácticas del curso.

| # | Técnica | Práctica | Archivo | Para qué se usa | Se verifica contra |
|---|---|---|---|---|---|
| 1 | Especificación de histograma | P4 | `preproceso.py` | Igualar la iluminación de cada cuadro a la del cuadro de calibración | `cv2.equalizeHist` y comparación de histogramas acumulados |
| 2 | Filtros espaciales: binomial y gradiente | P5 | `preproceso.py`, `gradiente.py` | Quitar ruido y medir los bordes del ojo en las dos direcciones | `cv2.GaussianBlur`, `cv2.Sobel` |
| 3 | Pirámide gaussiana y banda laplaciana | P6 | `piramide.py` | Buscar el rostro de grueso a fino y comparar en una banda poco sensible a la luz | `cv2.pyrDown` |
| 4 | Correlación de fase (Fourier) | P6 | `correlacion.py` | Medir cuánto se desplazó la cabeza entre dos cuadros | `cv2.phaseCorrelate` |
| 5 | Transformación geométrica con mapeo inverso | P3 | `geometria.py` | Llevar el rostro a un tamaño fijo | `cv2.warpAffine` |
| 6 | Correlación normalizada (plantilla) | Convolución, P5 | `correlacion.py` | Seguir el rostro y medir qué tan de frente está | `cv2.matchTemplate` |

Opcional, solo si sobra tiempo: SIFT con RANSAC y homografía (P7) para confirmar el giro de la cabeza cada cierto número de cuadros.

### Cómo mide la apertura el algoritmo 2

Este es el punto central del sistema, así que va con detalle.

En un ojo abierto se ve el iris, que es un disco oscuro. Sus lados izquierdo y derecho son bordes verticales, y un borde vertical aparece en el gradiente horizontal. En un ojo cerrado solo queda la línea de las pestañas, que es un borde horizontal y aparece en el gradiente vertical.

La medida es el cociente entre las dos cosas:

```
razón = suma de |gradiente horizontal| / suma de |gradiente vertical|
```

Se calcula así, sobre el recorte de un ojo de 64 px de ancho:

1. Se descarta el 30% superior del recorte, donde suele estar la ceja.
2. Se suaviza con el filtro binomial.
3. Se busca la banda de 5 renglones más oscura. Ahí está el iris o la línea de pestañas.
4. En esa banda, con 4 renglones de margen arriba y abajo y en las columnas centrales, se suman los valores absolutos de los dos gradientes de Sobel y se dividen.

La razón se convierte en apertura con dos referencias, la del ojo abierto y la del ojo cerrado:

```
apertura = (razón − razón cerrado) / (razón abierto − razón cerrado)
```

Con las referencias 0.74 y 0.39, una razón de 0.67 da (0.67 − 0.39) / (0.74 − 0.39) = 0.80. Una razón de 0.45 da 0.17 y el ojo se declara cerrado porque quedó debajo de 0.20.

Las referencias salen de la calibración de la persona. Si no hay calibración, se usan 0.72 y 0.41, que son las medianas medidas en el dataset de Kaggle.

**Evidencia.** Sobre los 1452 recortes de ojos de Kaggle (726 abiertos y 726 cerrados, sin calibración y con un solo umbral), la medida separa las dos clases con F1 de 0.86 y 0.84 en las dos mitades de prueba, cerca de 85% de aciertos. Detalle en `evaluacion.md`.

**La idea que se descartó.** El primer diseño medía la separación entre los bordes de los párpados en el perfil del gradiente vertical. Con las mismas 84 imágenes no distinguió abierto de cerrado mejor que el azar. La ceja, las pestañas y los pliegues del párpado producen picos que se confunden con los párpados. Se conserva aquí porque es un buen ejemplo para el reporte de por qué se prueba antes de construir.

La medida de la boca todavía no está validada (decisión D31).

### Cómo se mantiene barato el algoritmo 6

Buscar la plantilla en toda la imagen sería lento. Se hace en el nivel más pequeño de la pirámide (160×90), con una plantilla de unos 30×38 px, y solo en una ventana de 8 px alrededor de la posición anterior. Son 17×17 = 289 posiciones de unos 1100 px cada una, cerca de 330 mil multiplicaciones por cuadro. Medido, tarda unos 3 ms. Después se afina en el nivel siguiente con una ventana de 2 px.

## Funciones de biblioteca que sí se usan

El enunciado permite bibliotecas para adquirir imágenes, convertir formatos, manejar memoria, visualizar y construir interfaces, y para operaciones matemáticas básicas. Cada uso debe poder justificarse:

| Función | Para qué | Por qué se permite |
|---|---|---|
| `cv2.VideoCapture` | Leer cámara o video | Adquisición de imágenes |
| `cv2.cvtColor` | Pasar a grises | Conversión de formato |
| `cv2.imshow`, `cv2.createTrackbar`, `cv2.putText`, `cv2.rectangle` | Ventanas, deslizadores y dibujo | Visualización e interfaz |
| `numpy` (arreglos, sumas, productos) | Aritmética de arreglos | Operaciones básicas |
| `numpy.fft.fft2` | Transformada de Fourier | Operación matemática básica. Lo propio es la correlación de fase que se construye encima |

Las funciones de OpenCV equivalentes a los algoritmos propios (`cv2.GaussianBlur`, `cv2.matchTemplate` y las demás) solo aparecen en `verificacion/`, nunca en `somnolencia/`.

## Papel de los modelos de IA

Ninguno. Decisión D03: el proyecto no usa redes ni modelos preentrenados, ni dentro del sistema ni para evaluarlo.

- El sistema solo depende de NumPy y OpenCV, y de OpenCV solo se usan la lectura de video, la conversión a grises y las ventanas.
- La referencia para evaluar son las anotaciones hechas a mano sobre los videos del equipo.
- Una prueba automática (`pruebas/test_reglas.py`) revisa que ningún archivo del sistema importe bibliotecas de redes ni detectores ya entrenados.

## Ficha del sistema

Una ficha del sistema es una página que dice para qué sirve, con qué se probó y dónde falla. Se llena al final y va en el reporte. Lo ya escrito sale del diseño; lo que tiene línea se llena con resultados.

**Qué hace.** Detecta parpadeos y los clasifica por duración, cuenta bostezos, mide episodios de distracción y calcula PERCLOS sobre 30 s, a partir del video de una cámara frontal.

**Uso previsto.** Demostración académica de algoritmos de visión computacional.

**Usos no previstos.** No es un dispositivo de seguridad. No debe usarse para conducir ni para tomar decisiones sobre una persona.

**Supuestos.**
- Una sola persona frente a la cámara.
- Cámara fija, de frente, a una distancia parecida a la de la calibración.
- Calibración al inicio de cada sesión.
- Iluminación sin cambios bruscos después de calibrar.

**Limitaciones conocidas por diseño.**
- La etiqueta de microsueño describe ojos cerrados más de 7 s, no un estado de sueño confirmado. El enunciado lo reconoce.
- Mirar hacia abajo puede confundirse con ojos cerrados o con distracción.
- Una mano frente a la boca oculta el bostezo.
- Lentes oscuros o con reflejos impiden medir los ojos.
- La duración de cada evento tiene un error de un cuadro de más o de menos.
- Sirve para la persona con la que se calibró.

**Con qué se probó.** ______ (tabla de cobertura de `datos_y_gobernanza.md`)

**Resultados.** ______ (tablas de `evaluacion.md`)

**Dónde falla.** ______ (casos observados durante la evaluación)

**Versión evaluada.** Etiqueta ______ del repositorio.
