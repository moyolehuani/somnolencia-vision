# `evaluacion/`

Aquí va el código que calcula las métricas del reporte. El método completo está en `docs/evaluacion.md`. Este README dice qué archivo hace qué.

Nada de esta carpeta se ejecuta durante la demo.

```
evaluacion/
├── por_cuadro.py       métricas sobre imágenes sueltas de Kaggle
├── por_evento.py       métricas sobre videos anotados
├── desempeno.py        tiempos por etapa y cuadros por segundo
└── resultados/         tablas y gráficas que salen de las corridas
```

---

## `por_cuadro.py` (frentes 2 y 3)

**Aquí debe ir el código que** recorre una carpeta de imágenes con etiqueta conocida, aplica la medición correspondiente y cuenta aciertos y errores.

- Recibe la carpeta del dataset y qué medición probar (ojos o boca). La de cabeza no se evalúa aquí porque depende de la plantilla de la persona calibrada.
- Entrega la matriz de confusión, precisión, recall y F1.
- Guarda la lista de imágenes mal clasificadas, para revisarlas.

Dos cosas que cuidar:

- La división entre imágenes para elegir umbral e imágenes para reportar se hace una vez, con una semilla fija, y se guarda en un archivo. No se vuelve a sortear.
- Estas imágenes no pasan por la calibración. Se usa un umbral fijo sobre la separación de picos dividida entre el alto de la imagen.

---

## `por_evento.py` (frente 4)

**Aquí debe ir el código que** compara la bitácora del sistema contra las anotaciones de un video.

- Recibe el archivo de anotaciones y la bitácora del mismo video.
- Empareja eventos del mismo tipo que se traslapan en el tiempo. Cada evento anotado se empareja con uno detectado a lo más.
- Entrega, por tipo de evento: anotados, detectados, precisión, recall y error medio de duración.
- Entrega la matriz de confusión entre categorías de parpadeo.
- Calcula PERCLOS a partir de las anotaciones con el mismo código de `temporal/perclos.py`, lo compara segundo a segundo contra el del sistema y entrega el error medio y la coincidencia de nivel.

Para correr sobre muchos videos, `principal.py` debe poder ejecutarse sin ventana (por ejemplo con una opción `--sin-ventana`) y a toda velocidad. Como con archivos el tiempo sale del número de cuadro, el resultado no depende de la velocidad.

La calibración con videos: los primeros segundos de cada video de guion son la calibración (ojos abiertos 3 s y ojos cerrados 2 s). Los guiones lo incluyen al inicio.

---

## `desempeno.py` (frente 1)

**Aquí debe ir el código que** lee los tiempos que `principal.py` registra por etapa y produce la tabla de tiempo medio, tiempo máximo y cuadros por segundo.

También corre las variantes de la tabla de compromisos de `docs/evaluacion.md` (otra resolución, sin especificación de histograma, otra ventana de búsqueda).

Se ejecuta en el equipo de la demo.

---

## `resultados/`

**Aquí deben ir** las tablas (CSV) y gráficas que producen los tres programas.

Cada corrida se guarda en su propia subcarpeta con fecha, y dentro lleva tres archivos que la hacen reproducible:

- `version.txt`: etiqueta o commit del código.
- `parametros.txt`: copia de los valores de `config.py`.
- `videos.txt`: lista de videos o imágenes que se usaron.

Aquí no se guardan imágenes de rostros. Las gráficas son de números: matrices de confusión, barras, curvas.

---

## Hecho cuando

- Las tablas de los niveles 2, 3 y 4 de `docs/evaluacion.md` están llenas con resultados de la versión `v0.9`.
- Cualquier integrante puede repetir una corrida y obtener los mismos números.
