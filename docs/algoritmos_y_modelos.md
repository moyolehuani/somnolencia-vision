# Algoritmos y modelos

## Qué cuenta como "modelo" en este proyecto

No hay red neuronal dentro del sistema y no hace falta. El enunciado pide al menos cuatro algoritmos de visión computacional vistos en clase e implementados por el equipo, y califica con 5 un sistema que sea solo una red.

Lo que en otros sistemas hace una red, aquí lo hace una cadena de algoritmos clásicos cuyos pasos se pueden mostrar uno por uno. Esa es también la ventaja para la defensa: ante cualquier resultado se puede enseñar la imagen intermedia que lo produjo.

## Algoritmos propios

Estos son los que se presentan como "implementados por el equipo". Todos vienen de las prácticas del curso.

| # | Técnica | Práctica | Archivo | Para qué se usa | Se verifica contra |
|---|---|---|---|---|---|
| 1 | Especificación de histograma | P4 | `preproceso.py` | Igualar la iluminación de cada cuadro a la del cuadro de calibración | Comparación de histogramas acumulados |
| 2 | Filtros espaciales: binomial y gradiente | P5 | `preproceso.py`, `gradiente.py` | Quitar ruido y medir la separación de párpados y labios | `cv2.GaussianBlur`, `cv2.Sobel` |
| 3 | Pirámide gaussiana y banda laplaciana | P6 | `piramide.py` | Buscar el rostro de grueso a fino y comparar en una banda poco sensible a la luz | `cv2.pyrDown` |
| 4 | Correlación de fase (Fourier) | P6 | `correlacion.py` | Medir cuánto se desplazó la cabeza entre dos cuadros | `cv2.phaseCorrelate` |
| 5 | Transformación geométrica con mapeo inverso | P3 | `geometria.py` | Llevar el rostro a un tamaño fijo | `cv2.warpAffine` |
| 6 | Correlación normalizada (plantilla) | Convolución, P5 | `correlacion.py` | Seguir el rostro y medir qué tan de frente está | `cv2.matchTemplate` |

Opcional, solo si sobra tiempo: SIFT con RANSAC y homografía (P7) para confirmar el giro de la cabeza cada cierto número de cuadros.

### Cómo mide la apertura el algoritmo 2

Este es el punto central del sistema, así que va con un ejemplo.

Se toma la franja del rostro normalizado donde caen los ojos, por ejemplo de 128 px de ancho por 35 de alto. Se suaviza con el filtro binomial y se calcula el gradiente vertical, que responde donde la intensidad cambia de un renglón al siguiente. Después se suma el valor absoluto del gradiente a lo largo de cada renglón. El resultado es un perfil con un número por renglón.

- Con el ojo abierto hay dos renglones donde el perfil es alto: el borde del párpado superior y el borde inferior del ojo. Supongamos que quedan en los renglones 12 y 23. La separación es 11 px.
- Con el ojo cerrado los dos bordes se juntan en la línea de las pestañas. Queda un solo pico, o dos a 1 o 2 px. La separación es casi 0.

La apertura compara la separación actual con las dos que se midieron en la calibración, una con los ojos abiertos y otra con los ojos cerrados:

```
apertura = (separación actual − separación cerrada) / (separación abierta − separación cerrada)
```

Si en la calibración fueron 11 px con los ojos abiertos y 1 px con los ojos cerrados, y ahora son 9, la apertura es (9 − 1) / (11 − 1) = 0.80. Si ahora son 2, la apertura es 0.10 y el ojo se declara cerrado porque quedó debajo de 0.20.

Las cejas también son bordes horizontales y pueden confundir la medida. Por eso la franja de los ojos no se fija a mano: se toma de la calibración, como las filas donde el perfil más cambia entre ojos abiertos y ojos cerrados.

La boca se mide igual, en su propia franja y contra su separación en reposo.

### Cómo se mantiene barato el algoritmo 6

Buscar la plantilla en toda la imagen sería lento. Se hace en el nivel más pequeño de la pirámide (160×90), con una plantilla de unos 30×38 px, y solo en una ventana de 8 px alrededor de la posición anterior. Son 17×17 = 289 posiciones de unos 1100 px cada una, cerca de 330 mil multiplicaciones por cuadro, que NumPy resuelve sin problema. Después se afina en el nivel siguiente con una ventana de 2 px.

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
