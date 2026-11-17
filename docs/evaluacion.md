# Evaluación

La evaluación responde cuatro preguntas distintas. Cada una tiene su propio método, y juntas cubren lo que pide la rúbrica.

| Pregunta | Nivel | Con qué datos | Código |
|---|---|---|---|
| ¿Cada algoritmo propio hace lo que debe? | Por algoritmo | Imágenes de prueba | `verificacion/` |
| ¿Cada medición distingue bien en una imagen? | Por cuadro | Datasets de Kaggle | `evaluacion/por_cuadro.py` |
| ¿El sistema detecta y clasifica bien los eventos? | Por evento | Videos anotados | `evaluacion/por_evento.py` |
| ¿Corre en tiempo real? | Desempeño | Cámara en el equipo de la demo | `evaluacion/desempeno.py` |

Las metas que aparecen abajo son propuestas iniciales. Se revisan cuando haya una primera corrida.

## Nivel 1. Por algoritmo

Para cada algoritmo propio se corre la misma entrada por la implementación del equipo y por la función equivalente de OpenCV, y se reporta la diferencia.

| Algoritmo | Referencia | Medida | Meta | Resultado | Tiempo propio | Tiempo OpenCV |
|---|---|---|---|---|---|---|
| Suavizado binomial | `cv2.GaussianBlur` con el mismo núcleo | Diferencia máxima por pixel | 1 nivel de gris o menos | 0.00005 | 1.6 ms | 0.1 ms |
| Gradiente vertical | `cv2.Sobel` | Diferencia máxima por pixel | 1 nivel de gris o menos | 0.0001 | 1.3 ms | 0.2 ms |
| Gradiente horizontal | `cv2.Sobel` | Diferencia máxima por pixel | 1 nivel de gris o menos | 0.0001 | 1.2 ms | 0.1 ms |
| Pirámide gaussiana (3 niveles) | `cv2.pyrDown` | Diferencia máxima por pixel | 2 niveles de gris o menos | 0.00003 | 2.1 ms | 0.1 ms |
| Especificación de histograma | `cv2.equalizeHist`, con referencia uniforme | Diferencia máxima por pixel | 1 nivel de gris o menos | 1 | 0.3 ms | 0.02 ms |
| Especificación de histograma | Histograma acumulado objetivo | Diferencia máxima entre acumulados | 0.02 o menos | 0.014 (antes de corregir: 0.609) | | |
| Correlación normalizada | `cv2.matchTemplate` | Diferencia máxima del mapa y posición del máximo | Misma posición | 0.00002, misma posición | 2.7 ms | 0.06 ms |
| Correlación de fase | Desplazamiento conocido | Error en pixeles | 1 px o menos | 0 en cinco desplazamientos | 1.2 ms | 0.4 ms |
| Correlación de fase | `cv2.phaseCorrelate` | Diferencia en pixeles | 0.5 px o menos | 0.33 | | |
| Mapeo inverso | `cv2.warpAffine` | Diferencia máxima por pixel | 2 niveles de gris o menos | 0.0006 | 0.3 ms | 0.03 ms |

Corrida del 16 de noviembre con `python -m verificacion.verificar`, sobre texturas sintéticas con los tamaños que usa el sistema (640×360 para el cuadro, 128×160 para el rostro, 17×17 posiciones para la búsqueda de la plantilla). Los tiempos son del entorno donde se desarrolló y hay que repetirlos en el equipo de la demo.

Cómo leer la tabla:

- Los filtros, la pirámide y el mapeo inverso coinciden con OpenCV hasta el redondeo de la aritmética. No hay diferencia en las orillas porque la imagen se extiende reflejándola, igual que hace OpenCV por omisión.
- La especificación de histograma difiere en un nivel de gris de `equalizeHist` porque las dos redondean distinto.
- La correlación de fase propia entrega pixeles enteros y la de OpenCV entrega decimales. De ahí la diferencia de 0.33.
- Las versiones propias son entre 3 y 45 veces más lentas que OpenCV, que está escrito en C++ y optimizado. Aun así, todas juntas suman unos 10 ms por cuadro, dentro de los 66 ms disponibles a 15 cuadros por segundo. Es el compromiso entre entender cada paso y la velocidad que pide discutir el enunciado.


## Nivel 2. Por cuadro

Se corre la medición sobre imágenes sueltas con etiqueta conocida y se cuenta cuántas clasifica bien.

Para una clase (por ejemplo "ojo cerrado"):

- **Precisión.** De las imágenes que el sistema llamó cerradas, qué fracción lo estaba.
- **Recall.** De las imágenes realmente cerradas, qué fracción encontró el sistema.
- **F1.** Media armónica de las dos anteriores.

| Medición | Dataset | Imágenes | Precisión | Recall | F1 | Meta de F1 |
|---|---|---|---|---|---|---|
| Ojo abierto o cerrado, umbral con mitad A y reporte en B | Muestra de Kaggle | 22 abiertos, 20 cerrados | 0.83 | 0.95 | 0.88 | 0.90 |
| Ojo abierto o cerrado, umbral con mitad B y reporte en A | Muestra de Kaggle | 22 abiertos, 20 cerrados | 0.94 | 0.85 | 0.89 | 0.90 |
| Dataset completo, umbral con mitad A y reporte en B | Kaggle somnolencia | 363 abiertos, 363 cerrados | 0.84 | 0.88 | 0.86 | 0.90 |
| Dataset completo, umbral con mitad B y reporte en A | Kaggle somnolencia | 363 abiertos, 363 cerrados | 0.82 | 0.87 | 0.84 | 0.90 |
| Bostezo o no | No evaluable por cuadro (ver abajo) | | | | | |

Cada fila va acompañada de su matriz de confusión.

**Primer resultado (16 de noviembre).** Se probó con una muestra de 84 recortes de ojos (44 abiertos y 40 cerrados), sin calibración y con un umbral fijo. La medida de razón de bordes quedó en F1 de 0.88 y 0.89, un poco debajo de la meta. La mediana de la razón fue 0.74 en abiertos y 0.39 en cerrados. La muestra es pequeña.

**Resultado con el dataset completo (16 de noviembre).** Con los 1452 recortes (726 abiertos y 726 cerrados) el F1 fue de 0.86 y 0.84, y la medida clasifica bien alrededor del 85% de las imágenes. Las medianas de la razón fueron 0.72 en abiertos y 0.41 en cerrados, y el umbral elegido fue el mismo con las dos mitades, 0.563. La medida es estable, pero queda debajo de la meta de 0.90.

Tres cosas para leer bien este número:

- Es sin calibración y con un solo umbral para todas las personas. En el sistema cada persona se calibra, y además el umbral doble y el antirrebote absorben errores de cuadros sueltos. Cuánto mejora con eso solo se sabe con video.
- Las dos mitades se forman alternando imágenes por nombre. Si el dataset trae fotos seguidas de la misma persona, esa persona queda en las dos mitades. El número dice qué tan bien separa un umbral este dataset, no qué tan bien funcionaría con personas nuevas.
- Los recortes de Kaggle son ojos muy cercanos y de fuentes variadas. Los del sistema saldrán de una webcam a 60 cm. No conviene afinar la medida contra Kaggle más allá de este punto.

Se reproduce con `python -m evaluacion.por_cuadro <carpeta que contiene Open y Closed>`.

La primera medida que se diseñó (separación de picos del gradiente vertical) se probó con las mismas imágenes y no separó las clases mejor que el azar. Por eso se cambió.

**Bostezos.** Las carpetas `yawn` y `no_yawn` del dataset no son recortes de boca. Son escenas completas de 640×480 de personas manejando, con el rostro pequeño y visto desde varios ángulos. Para medir la boca ahí primero habría que encontrar el rostro, y el sistema lo encuentra con la plantilla de la persona calibrada. El bostezo se evalúa entonces por evento, con los videos del guion G3.

La distracción no aparece en esta tabla. La medición de cabeza compara cada cuadro contra la plantilla de la persona calibrada, así que no puede aplicarse a imágenes sueltas de otras personas. Se evalúa en el nivel 3 con los videos del guion G4. Qué uso se le da al dataset de distracción de Kaggle queda por decidir después de inventariarlo (decisión D26).

Dos cuidados:

- Las imágenes de Kaggle no pasan por calibración, así que aquí se evalúa la medición con un umbral fijo. El número sirve para saber si la idea funciona, y puede ser peor que el desempeño en video con calibración.
- Una parte de las imágenes se usa para elegir el umbral y otra distinta para reportar. La división se fija una vez y se guarda.

Qué tanto se puede hacer aquí depende del inventario de los datasets (paso 0.7). Si las imágenes de ojos no son recortes del ojo sino caras completas, primero hay que recortar la franja a mano o con proporciones fijas, y se dice en el reporte.

## Nivel 3. Por evento

Es el nivel que más importa, porque el enunciado define todo en términos de duraciones.

### Videos con guion

Cada persona graba los guiones G1 a G5. El guion ya es casi la anotación, porque dice qué pasa y cuándo. Se graba con un cronómetro visible fuera de cuadro o con alguien dando las indicaciones.

| Guion | Contenido | Para qué sirve |
|---|---|---|
| G1 | 60 s mirando al frente con parpadeo natural | Parpadeos normales, PERCLOS de base, falsas alarmas |
| G2 | Cierres de 1 s, 3 s y 8 s, con 5 s de ojos abiertos entre cada uno, dos veces | Las tres categorías de la Tabla 1 del enunciado |
| G3 | Tres bostezos, 10 s hablando, una sonrisa amplia | Bostezos y sus confusiones |
| G4 | Giros a izquierda y derecha de 0.5, 1, 1.5, 2 y 3 s; mirar hacia abajo 3 s | Bandas de distracción |
| G5 | Dos minutos con todo mezclado | Prueba de conjunto y PERCLOS |
| G6 | G2 repetido con lentes, con luz baja y a contraluz | Robustez. Se reporta aparte |

Todos los guiones empiezan con la calibración: 3 s mirando al frente con los ojos abiertos y 2 s con los ojos cerrados. Esos 5 s no se anotan ni cuentan como evento.

El formato, la resolución, el encuadre y la duración de cada guion están en `datos/README.md`.

Con cuatro personas son 20 videos cortos más los de G6. Dos personas van al grupo de ajuste y dos al de evaluación (regla 6 de `datos_y_gobernanza.md`).

### Anotación

Alguien revisa cada video cuadro por cuadro y anota el inicio y el fin real de cada evento. El formato está en `datos/README.md`. En dos o tres videos conviene que anoten dos personas por separado y comparar, para saber cuánto varía la anotación misma.

### Cómo se compara

Un evento detectado **coincide** con uno anotado si son del mismo tipo y sus intervalos se traslapan. Cada evento anotado coincide con uno detectado a lo más: el que más se traslape.

- **Verdadero positivo.** Evento detectado que coincide con uno anotado.
- **Falso positivo.** Evento detectado que no coincide con ninguno.
- **Falso negativo.** Evento anotado que nadie detectó.

Ejemplo. El video `P03_G2_01` tiene anotado un cierre de 10.00 a 13.00 s. El sistema reporta un parpadeo de 10.07 a 13.13 s. Se traslapan, así que coincide. La duración anotada es 3.00 s y la detectada 3.06 s: error de 0.06 s, que a 15 cuadros por segundo es un cuadro. Las dos duraciones caen en la categoría "lento", así que la categoría también coincide.

El programa que hace esta comparación es `evaluacion/por_evento.py`. Su uso está en `evaluacion/README.md`, y `python -m evaluacion.demostracion` lo muestra completo con la escena dibujada.

### Tablas a llenar

| Tipo de evento | Anotados | Detectados | Precisión | Recall | Error medio de duración |
|---|---|---|---|---|---|
| Parpadeo | | | | | |
| Bostezo | | | | | |
| Distracción | | | | | |

Confusión entre categorías de parpadeo, solo sobre los que coincidieron:

| Anotado \ Detectado | Normal | Lento | Microsueño |
|---|---|---|---|
| Normal | | | |
| Lento | | | |
| Microsueño | | | |

PERCLOS. Se calcula a partir de las anotaciones con la misma definición que usa el sistema, se compara segundo a segundo y se reporta:

| Video | Error medio absoluto (puntos porcentuales) | Segundos en que coincide el nivel de alerta |
|---|---|---|
| | | |

Metas propuestas: recall de 0.90 o más en parpadeos lentos y microsueños, error de duración de 2 cuadros o menos, error de PERCLOS de 3 puntos porcentuales o menos.

## Nivel 4. Desempeño

Se mide en el equipo que se usará en la demo, con cámara.

| Etapa | Tiempo medio por cuadro (ms) | Tiempo máximo (ms) |
|---|---|---|
| Captura y grises | | |
| Pirámide | | |
| Seguimiento del rostro | | |
| Normalización e histograma | | |
| Ojos y boca | | |
| Cabeza | | |
| Capa temporal | | |
| Interfaz | | |
| **Total** | | |

Meta: 15 cuadros por segundo o más. El enunciado supone entre 10 y 25.

El enunciado pide además identificar los compromisos entre complejidad, calidad y velocidad. Para eso se repite la medición cambiando una cosa a la vez:

| Variante | Cuadros por segundo | Recall de parpadeos lentos |
|---|---|---|
| Resolución de trabajo 640×360 (base) | | |
| Resolución de trabajo 320×180 | | |
| Sin especificación de histograma | | |
| Ventana de búsqueda del rostro de 16 px en vez de 8 | | |

## Orden de la evaluación

1. Nivel 1 se va llenando conforme cada algoritmo se termina.
2. Nivel 2 se corre al terminar `ojos.py`, `boca.py` y `cabeza.py`.
3. Los umbrales se ajustan con los videos de ajuste.
4. Se congelan los umbrales y se guarda una copia de `config.py`.
5. Nivel 3 se corre una sola vez sobre los videos de evaluación.
6. Nivel 4 se corre en el equipo de la demo.

Si después del paso 5 se cambia un umbral, hay que decirlo en el reporte, porque los videos de evaluación ya dejaron de ser nuevos para el sistema.
