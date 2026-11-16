# `datos/`

Carpeta de datos en la computadora de cada integrante. Casi nada de lo que hay aquí se sube al repositorio. Las reglas completas están en `docs/datos_y_gobernanza.md`.

```
datos/
├── README.md         se sube
├── manifiesto.csv    se sube
├── anotaciones/      se sube
├── kaggle/           NO se sube. Cada quien descarga los datasets
└── videos/           NO se sube. Copia local de la carpeta compartida
```

El archivo `.gitignore` de la raíz ya está configurado así. Aun con eso, antes de cada commit se revisa `git status`.

## `kaggle/`

**Aquí deben ir** los dos datasets del enunciado, descargados por cada integrante con su cuenta de Kaggle, cada uno en su subcarpeta. Las ligas están en el PDF del enunciado.

## `videos/`

**Aquí deben ir** las copias locales de los videos de la carpeta de Google Drive.

Nombre de cada archivo: código de participante, guion y número de toma.

```
P02_G3_01.mp4     participante 02, guion G3, toma 1
```

### Especificaciones de grabación

Todos los videos se graban igual, para que las diferencias en los resultados vengan del sistema y no de la cámara.

| Aspecto | Valor | Por qué |
|---|---|---|
| Archivo | MP4 con video H.264 | OpenCV lo abre sin problemas en cualquier sistema |
| Resolución | 1280×720, horizontal | Es la que entrega casi cualquier webcam. El sistema la reduce a la mitad |
| Cuadros por segundo | 30, constantes | Con archivos, el tiempo se calcula como número de cuadro entre cuadros por segundo |
| Audio | Sin audio | No se usa, y es un dato personal menos |
| Cámara | La webcam de una laptop, de preferencia la de la demo | Los videos deben parecerse a lo que el sistema verá el día de la demo |
| Efectos | Ninguno: sin filtros, sin fondo desenfocado, sin HDR, sin modo espejo | Cambian la imagen de maneras que no ocurren en vivo |
| Una toma por archivo | Si sale mal, se repite y sube el número de toma | Facilita anotar |

### Encuadre

- Cámara fija, a la altura de los ojos, a una distancia de 50 a 70 cm.
- Rostro centrado. De la barbilla a la frente debe ocupar más o menos un tercio del alto de la imagen.
- Luz de frente o de lado. Nunca una ventana o lámpara detrás de la persona.
- Fondo sin otras personas ni caras (fotos, pantallas, carteles).
- La laptop no se mueve durante la toma.
- Cabello recogido si tapa los ojos. Lentes solo en el guion G6.

### Duración de cada guion

Cada video empieza con 5 s de calibración (3 s con ojos abiertos y 2 s con ojos cerrados) y termina con 3 s de margen mirando al frente. Los guiones están en `docs/evaluacion.md`.

| Guion | Duración aproximada |
|---|---|
| G1. Parpadeo natural | 70 s |
| G2. Cierres de 1, 3 y 8 s, dos veces | 70 s |
| G3. Bostezos, hablar, sonreír | 60 s |
| G4. Giros y mirada hacia abajo | 75 s |
| G5. Todo mezclado | 125 s |
| G6. G2 con lentes, con luz baja y a contraluz | 70 s cada condición |

De G1 a G5 son unos 400 s por persona, menos de 7 minutos. Entre los cuatro son alrededor de 27 minutos de video más las tomas de G6, que en este formato ocupan del orden de 1 a 2 GB.

Para llevar el tiempo durante la toma, otra persona da las indicaciones con un cronómetro. Quien se graba no mira el cronómetro, porque mirar a un lado cuenta como distracción.

### Comprobar cada video

Después de grabar, este comando imprime resolución, cuadros por segundo, número de cuadros y duración:

```bash
python -c "import cv2,sys; c=cv2.VideoCapture(sys.argv[1]); n=c.get(cv2.CAP_PROP_FRAME_COUNT); f=c.get(cv2.CAP_PROP_FPS); print(int(c.get(cv2.CAP_PROP_FRAME_WIDTH)), 'x', int(c.get(cv2.CAP_PROP_FRAME_HEIGHT)), '|', f, 'fps |', int(n), 'cuadros |', round(n/f, 2), 's')" datos/videos/P01_G1_01.mp4
```

Debe decir 1280 x 720 y 30 fps, y la duración debe coincidir con la que muestra el reproductor. Si difieren en más de medio segundo, la cámara grabó con cuadros por segundo variables. Pasa con poca luz y con casi todos los celulares. En ese caso las duraciones que mida el sistema saldrían mal, así que el video se vuelve a grabar con más luz o se normaliza.

### Si hay que normalizar un video

Para dejar un video en 1280×720, 30 cuadros por segundo constantes y sin audio se usa ffmpeg, un programa gratuito de conversión de video. Solo prepara datos. No forma parte del sistema ni del entregable.

```bash
ffmpeg -i original.mp4 -vf "scale=1280:720,fps=30" -c:v libx264 -crf 18 -an P01_G1_01.mp4
```

Esto supone que el original es horizontal y de proporción 16:9. Si no lo es, se graba de nuevo.

### Si no queda más que usar celular

- Horizontal y sobre un soporte fijo.
- 720p a 30 cuadros por segundo.
- En los ajustes de la cámara, elegir el formato "más compatible" (H.264). El formato de alta eficiencia (HEVC) puede no abrir en OpenCV.
- Pasarlo siempre por el comando de normalización.

## `manifiesto.csv`

**Aquí debe ir** una fila por video, con lo necesario para saber qué es cada uno sin abrirlo.

| Columna | Ejemplo | Significado |
|---|---|---|
| `video` | `P02_G3_01.mp4` | Nombre del archivo |
| `participante` | `P02` | Código, nunca el nombre |
| `guion` | `G3` | Guion grabado |
| `grupo` | `ajuste` | `ajuste` o `evaluacion`. Se fija una vez y no cambia |
| `fps` | `30` | Cuadros por segundo del archivo |
| `resolucion` | `1280x720` | |
| `duracion_s` | `62.4` | |
| `condiciones` | `luz de salón, sin lentes` | |
| `fecha` | `2026-11-20` | Fecha de grabación |
| `anotado_por` | `P01` | Código de quien anotó |

## `anotaciones/`

**Aquí debe ir** un archivo CSV por video, con el mismo nombre y extensión `.csv`, y una fila por evento real.

| Columna | Ejemplo | Significado |
|---|---|---|
| `tipo` | `parpadeo` | `parpadeo`, `bostezo` o `distraccion` |
| `inicio_s` | `10.00` | Primer cuadro en que los ojos están cerrados, la boca abierta o la cabeza girada |
| `fin_s` | `13.00` | Primer cuadro en que eso deja de pasar |
| `notas` | `cierre de 3 s del guion` | Opcional |

Las columnas coinciden con las de la bitácora del sistema, para que `evaluacion/por_evento.py` lea las dos igual.

### Cómo anotar

1. Abrir el video en un reproductor que avance cuadro por cuadro y muestre el tiempo.
2. Anotar los eventos después de la calibración. Los 5 s iniciales no se anotan.
3. Para cada evento, buscar el primer cuadro donde empieza y el primer cuadro donde ya terminó.
4. El criterio para "ojos cerrados" es que no se vea el iris. Para "distraído", que la cara no apunte a la cámara. Se anota lo que se ve, no lo que decía el guion.
5. También se anotan los parpadeos naturales, no solo los del guion.

En dos o tres videos anotan dos personas por separado. La diferencia entre ambas dice cuánta incertidumbre tiene la anotación, y se menciona en el reporte.
