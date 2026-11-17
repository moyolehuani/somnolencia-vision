# `evaluacion/`

Código que calcula las métricas del reporte. El método completo está en `docs/evaluacion.md`. Este README dice qué archivo hace qué.

Nada de esta carpeta se ejecuta durante la demo. Aquí sí se pueden usar funciones de OpenCV como `cv2.resize`, porque no es parte del sistema.

## Estado

| Archivo | Nivel de evaluación | Estado |
|---|---|---|
| `por_cuadro.py` | 2. Por cuadro, con imágenes de Kaggle | Escrito y corrido con el dataset completo |
| `por_evento.py` | 3. Por evento, con videos anotados | Escrito y probado con la escena dibujada. Falta correrlo con videos reales |
| `demostracion.py` | Ejemplo de la evaluación completa con la escena | Escrito |
| `desempeno.py` | 4. Tiempos por etapa | Por escribir (tarea T10) |
| `resultados/` | Salidas de las corridas | Se crea al correr |

El nivel 1 (cada algoritmo contra OpenCV) está en `verificacion/`.

---

## `por_cuadro.py`

Mide qué tan bien la razón de bordes separa ojos abiertos de ojos cerrados en imágenes sueltas.

```bash
python -m evaluacion.por_cuadro datos/kaggle/drowsiness_dataset/train
```

El argumento es la carpeta que contiene las subcarpetas `Open` y `Closed`. `python revisar.py` la busca sola dentro de `datos/kaggle`.

| Función | Recibe | Entrega |
|---|---|---|
| `cargar_recorte(ruta)` | Ruta de una imagen de un ojo | Imagen en grises de 64 px de ancho, o `None` si no se pudo leer |
| `medir_carpeta(carpeta)` | Carpeta de imágenes | Lista de `(nombre, razón)` |
| `mejor_umbral(abiertos, cerrados)` | Razones de cada clase | Umbral que da el mejor promedio de aciertos de las dos clases |
| `metricas(abiertos, cerrados, umbral)` | Razones y umbral | Matriz de confusión, precisión, recall y F1 de la clase "cerrado" |
| `principal(raiz, salida)` | Carpeta y archivo de salida | Imprime el resultado y guarda la razón de cada imagen |

### Cómo evita hacer trampa

Las imágenes se dividen en dos mitades fijas, alternando por orden de nombre. El umbral se elige con una mitad y los resultados se reportan con la otra. Después se repite al revés.

Límite de esta división: si el dataset trae fotos seguidas de la misma persona, esa persona queda en las dos mitades. El número dice qué tan bien separa un umbral este dataset, no qué pasaría con personas nuevas.

### Resultado

Con los 1452 recortes del dataset (726 abiertos y 726 cerrados):

| | Umbral | Precisión | Recall | F1 |
|---|---|---|---|---|
| Umbral con mitad A, reporte en B | 0.563 | 0.84 | 0.88 | 0.86 |
| Umbral con mitad B, reporte en A | 0.563 | 0.82 | 0.87 | 0.84 |

Mediana de la razón: 0.716 en abiertos y 0.408 en cerrados.

Es sin calibración y con un solo umbral para todas las personas. En el sistema cada persona se calibra. Cuánto mejora con eso solo se sabe con video.

### Salida

`evaluacion/resultados/por_cuadro_ojos.csv`, con columnas `clase`, `imagen`, `razon`. Sirve para revisar qué imágenes fallan. No contiene imágenes, así que puede subirse al repositorio.

### Lo que no se puede evaluar aquí

- **La boca.** Las carpetas `yawn` y `no_yawn` son escenas completas de personas manejando, no recortes de boca.
- **La cabeza.** Su medición compara contra la plantilla de la persona calibrada y no aplica a fotos sueltas de otras personas.

Las dos se evalúan por evento, con los videos del equipo.

---

## `por_evento.py`

Compara la bitácora del sistema contra las anotaciones del mismo video.

```bash
python -m evaluacion.por_evento anotaciones.csv bitacora.csv
python -m evaluacion.por_evento anotaciones.csv bitacora.csv mediciones.csv
```

| Archivo | Qué es | Quién lo produce |
|---|---|---|
| `anotaciones.csv` | Eventos reales del video | Una persona, con el formato de `datos/README.md` |
| `bitacora.csv` | Eventos que detectó el sistema | `somnolencia.principal` |
| `mediciones.csv` | Mediciones de cada cuadro. Opcional, para comparar PERCLOS | `somnolencia.principal --mediciones` |

| Función | Recibe | Entrega |
|---|---|---|
| `categoria_de(tipo, duracion)` | Tipo y segundos | Categoría con las reglas del sistema, o `None` si no se cuenta |
| `crear_evento(tipo, inicio, fin)` | Tipo y tiempos | Un `Evento`, o `None` si no se cuenta |
| `leer_eventos(ruta)` | Un CSV de anotaciones o una bitácora | Lista de `Evento` |
| `traslape(a, b)` | Dos eventos | Segundos en que coinciden |
| `emparejar(anotados, detectados)` | Dos listas de eventos | `(parejas, sin_detectar, de_mas)` |
| `metricas_por_tipo(parejas, sin_detectar, de_mas)` | El resultado de emparejar | Por tipo: anotados, detectados, aciertos, precisión, recall, error de duración y fracción con la misma categoría |
| `confusion_de_parpadeos(parejas)` | Las parejas | Tabla de categoría anotada contra detectada |
| `comparar_perclos(ruta_de_mediciones, anotados)` | El CSV de mediciones y las anotaciones | Error medio y máximo de PERCLOS y fracción de cuadros con el mismo nivel |
| `imprimir_reporte(anotados, detectados, ruta_de_mediciones=None)` | Las dos listas | Imprime todo |

### Cómo se emparejan los eventos

Un evento detectado corresponde a uno anotado si son del mismo tipo y sus intervalos se traslapan. Se listan todas las parejas posibles, se ordenan de mayor a menor traslape y se aceptan en ese orden, siempre que ninguno de los dos esté ya emparejado. Cada evento queda en una pareja a lo más.

- Un anotado sin pareja es un evento que el sistema no detectó. Baja el recall.
- Un detectado sin pareja es un evento que el sistema inventó. Baja la precisión.

Ejemplo. Se anotó un cierre de 10.0 a 18.0 s (microsueño). El sistema reportó dos: de 10.0 a 13.0 s y de 13.5 a 18.0 s. La pareja se forma con el segundo, que se traslapa más (4.5 s). El primero queda como detectado de más. Y la categoría no coincide: se anotó microsueño y se detectó lento.

### Cuidados

- **La categoría se recalcula.** Las anotaciones no la traen. Se calcula a partir de la duración con `clasificar_parpadeo` y `banda_de_distraccion`, las mismas funciones que usa el sistema.
- **Las distracciones anotadas de menos de 0.5 s se descartan**, porque el enunciado no las cuenta.
- **La calibración no se anota.** Los primeros 5 s de cada video quedan fuera.
- **PERCLOS de referencia.** Se calcula con `calcular_perclos` a partir de las anotaciones. Los parpadeos anotados son los cierres. Las distracciones anotadas se tratan como tramos sin dato, porque mientras la persona no mira al frente no se le ven los ojos. Es la misma regla que aplica el sistema.

### Salida de ejemplo

Con la escena dibujada:

```
Tipo          Anotados  Detectados  Aciertos  Precisión  Recall Error dur. (s)  Misma categoría
parpadeo             3           3         3       1.00    1.00          0.022             1.00
bostezo              1           1         1       1.00    1.00          0.000             1.00
distraccion          1           1         1       1.00    1.00          0.033             1.00

Parpadeos: categoría anotada (renglón) contra detectada (columna)
               normal    lento   microsueno
normal              1        0            0
lento               0        1            0
microsueno          0        0            1

PERCLOS, sobre 450 cuadros:
  error medio:   0.1 puntos porcentuales
  error máximo:  0.4 puntos porcentuales
  mismo nivel:   100% del tiempo
```

Con la escena sale perfecto porque es un dibujo. Eso comprueba que la evaluación está bien armada. Con videos de personas los números serán otros.

### Cómo evaluar un video real

1. Anotar el video en `datos/anotaciones/P03_G2_01.csv`.
2. Correr el sistema sin ventana:

```bash
python -m somnolencia.principal --fuente datos/videos/P03_G2_01.mp4 --sin-ventana --mediciones --caja x,y,ancho,alto
```

3. Comparar, con los nombres de archivo que imprimió el paso anterior:

```bash
python -m evaluacion.por_evento datos/anotaciones/P03_G2_01.csv salidas/bitacora_FECHA.csv salidas/mediciones_FECHA.csv
```

La caja del rostro de cada video se guarda en la columna `caja` de `datos/manifiesto.csv`. Para saber cuál es, se corre el video una vez con ventana, se marca el rostro con el ratón y se anota.

### Falta

- Correrlo con videos reales (tareas T04 y T11).
- Un programa que recorra todos los videos del manifiesto y junte los resultados en una sola tabla. Hoy se corre video por video.

---

## `demostracion.py`

Hace la evaluación completa con la escena dibujada, de principio a fin: corre el sistema, guarda bitácora y mediciones, escribe las anotaciones a partir del guion y compara.

```bash
python -m evaluacion.demostracion
```

Deja los tres archivos en `salidas/demostracion/`. Sirven como ejemplo del formato de cada uno. `python revisar.py` lo corre como su cuarto paso.

---

## `desempeno.py` (por escribir)

Mide el tiempo de cada etapa y los cuadros por segundo. La especificación está en la tarea T10 de `docs/tareas_pendientes.md`.

Hoy `principal.py` imprime al terminar el tiempo total de proceso por cuadro. Con la escena dibujada son unos 8 a 11 ms.

---

## `resultados/`

Aquí van las tablas y gráficas que producen los programas.

Cada corrida que vaya al reporte se guarda en su propia subcarpeta con fecha, junto con tres archivos que la hacen reproducible:

- `version.txt`: etiqueta o commit del código.
- `parametros.txt`: copia de los valores de `config.py`. La bitácora ya genera uno.
- `videos.txt`: lista de videos o imágenes que se usaron.

Aquí no se guardan imágenes de rostros. Las gráficas son de números.
