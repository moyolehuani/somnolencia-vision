# Paquete `somnolencia`

Este paquete es el sistema. Es lo único que se ejecuta en la demo.

```
somnolencia/
├── config.py             todos los parámetros, cada uno con su fuente
├── tipos.py              Medicion, Evento y nombres de estados
├── sistema.py            clase Sistema: procesa un cuadro de principio a fin
├── principal.py          programa principal: captura, ventanas, teclas, bitácora
├── simulador.py          mediciones inventadas, para probar la capa temporal
├── escena_sintetica.py   video dibujado, para probar todo sin cámara
├── percepcion/           algoritmos de visión: de un cuadro a tres mediciones
├── temporal/             reglas de tiempo: de mediciones a eventos y alertas
└── interfaz/             dibujo en pantalla, deslizadores y bitácora
```

Cada subcarpeta tiene su propio README con el detalle de sus archivos.

## Reglas de este paquete

- No se importa ninguna red ni modelo entrenado.
- En `percepcion/` no se usan las funciones de OpenCV equivalentes a los algoritmos propios: `cv2.GaussianBlur`, `cv2.Sobel`, `cv2.equalizeHist`, `cv2.pyrDown`, `cv2.matchTemplate`, `cv2.phaseCorrelate`, `cv2.warpAffine`, `cv2.resize`.
- `temporal/` no importa `cv2` ni recibe imágenes.
- Ningún archivo lleva umbrales escritos a mano. Todos se leen de `config.py`.

Las tres primeras se comprueban con `pruebas/test_reglas.py`.

## Las dos capas

La **percepción** recibe un cuadro y entrega tres mediciones entre 0 y 1: apertura de ojos, apertura de boca y frontalidad de la cabeza.

La **capa temporal** recibe esas mediciones con su marca de tiempo y decide qué eventos hay, cuánto vale PERCLOS y qué alerta toca.

`sistema.py` une las dos. `principal.py` le pasa cuadros y muestra el resultado.

---

## `tipos.py`

Estructuras que comparten todos los módulos.

```python
@dataclass
class Medicion:
    t: float        # marca de tiempo en segundos
    valor: float    # entre 0 y 1
    valido: bool    # False si no se pudo medir en este cuadro

@dataclass
class Evento:
    tipo: str         # "parpadeo", "bostezo" o "distraccion"
    inicio: float     # segundos
    fin: float        # segundos
    duracion: float   # fin - inicio, redondeada a milésimas
    categoria: str    # ver tabla
```

| Tipo de evento | Categorías posibles |
|---|---|
| `parpadeo` | `normal`, `lento`, `microsueno` |
| `bostezo` | `bostezo` |
| `distraccion` | `0.5`, `1.0`, `1.5`, `2.0` (la banda) |

| Señal | Estados | Significado de `valor` |
|---|---|---|
| Ojos | `ABIERTO`, `CERRADO`, `SIN_DATO` | 1 es tan abierto como en la calibración, 0 es tan cerrado como en la calibración |
| Boca | `CERRADA`, `ABIERTA`, `SIN_DATO` | Alto de la zona oscura de la boca entre el alto del rostro, menos su valor en reposo |
| Cabeza | `ATENTO`, `DISTRAIDO` | Parecido con la plantilla de frente. 1 es idéntica |

---

## `config.py`

Todos los parámetros. Cada uno lleva un comentario con su origen. Está dividido en dos partes.

### Valores que fija el enunciado (no se ajustan)

| Nombre | Valor | Qué es |
|---|---|---|
| `PARPADEO_NORMAL_MAX_S` | 0.5 | Hasta aquí un cierre es parpadeo normal |
| `PARPADEO_LENTO_MAX_S` | 7.0 | Hasta aquí es parpadeo lento. Más es microsueño |
| `BANDAS_DISTRACCION_S` | (0.5, 1.0, 1.5, 2.0) | Inicio de cada banda de distracción |
| `PERCLOS_VENTANA_S` | 30.0 | Ventana de PERCLOS |
| `PERCLOS_ALERTA`, `PERCLOS_FATIGA`, `PERCLOS_SOMNOLENCIA` | 0.08, 0.15, 0.30 | Niveles de PERCLOS |
| `AVISO_CIERRE_EN_CURSO_S` | 1.5 | Cierre en curso que dispara la alerta (referencia [1] del enunciado) |

### Valores que fija el equipo

| Grupo | Nombres | Estado |
|---|---|---|
| Reglas de tiempo | `PERCLOS_CUENTA_PARPADEOS_NORMALES`, `PERCLOS_TIEMPO_MINIMO_S`, `BOSTEZO_MIN_S`, `ANTIRREBOTE_CUADROS`, `SIN_DATO_TOLERANCIA_S`, `ALERTA_DISTRACCION_AVISO_S`, `ALERTA_DISTRACCION_ALERTA_S` | Provisionales. Ver D09, D11, D16, D30 |
| Umbrales de estado | `OJOS_UMBRAL_CIERRE`, `OJOS_UMBRAL_REAPERTURA`, `BOCA_UMBRAL_APERTURA`, `BOCA_UMBRAL_CIERRE`, `CABEZA_UMBRAL_DISTRAIDO`, `CABEZA_UMBRAL_ATENTO` | Por ajustar con los videos de ajuste |
| Medida de ojos | `OJOS_ANCHO_DE_RECORTE`, `OJOS_FRACCION_SIN_CEJA`, `OJOS_COLUMNA_INICIAL`, `OJOS_COLUMNA_FINAL`, `OJOS_ALTO_DE_BANDA`, `OJOS_MARGEN_DE_BANDA` | Validados con Kaggle (D28) |
| Referencias de ojos sin calibración | `OJOS_RAZON_ABIERTO`, `OJOS_RAZON_CERRADO` | Medianas del dataset de Kaggle: 0.72 y 0.41 |
| Recortes en el rostro | `OJOS_FILA_INICIAL`, `OJOS_FILA_FINAL`, `BOCA_FILA_INICIAL`, `BOCA_FILA_FINAL`, `BOCA_COLUMNA_INICIAL`, `BOCA_COLUMNA_FINAL` | Provisionales. Puestos sin ver una cara real |
| Tamaños | `GRABACION_ANCHO/ALTO`, `TRABAJO_ANCHO/ALTO`, `ROSTRO_ANCHO/ALTO`, `PIRAMIDE_NIVELES`, `RECUADRO_ANCHO/ALTO` | D18 |
| Seguimiento | `BUSQUEDA_VENTANA_PX`, `AFINADO_VENTANA_PX`, `REBUSCAR_CADA_CUADROS`, `FASE_PICO_MINIMO`, `PLANTILLA_FRACCION_ALTO` | Provisionales. Ver D32 |
| Calibración | `CALIBRACION_ABIERTOS_S`, `CALIBRACION_CERRADOS_S`, `CALIBRACION_MARGEN_S`, `CALIBRACION_DIFERENCIA_MINIMA` | D25 |
| Filtro | `NUCLEO_BINOMIAL` | Práctica 5 |

Para agregar un parámetro: se escribe en `config.py` con un comentario que diga qué es y de dónde sale el valor, y se anota en esta tabla.

---

## `sistema.py`

Contiene la clase `Sistema`, que procesa un cuadro de principio a fin. No sabe nada de cámaras, archivos ni ventanas. Por eso el mismo código sirve para la cámara, para un video, para la evaluación y para las pruebas.

### Uso

```python
from somnolencia.sistema import Sistema

sistema = Sistema()
sistema.iniciar(gris, caja, t)            # una vez, con la caja del rostro
resumen = sistema.procesar(gris, t)       # en cada cuadro
eventos_finales = sistema.terminar(t)     # al acabar
```

| Método | Recibe | Hace |
|---|---|---|
| `iniciar(gris, caja, t, con_calibracion=True)` | Cuadro en grises de 640×360, caja `(x, y, ancho, alto)` del rostro, marca de tiempo | Guarda la plantilla del rostro, el histograma de referencia y el umbral de la boca. Empieza la calibración, o la vigilancia si `con_calibracion` es `False` |
| `procesar(gris, t)` | Un cuadro y su tiempo | Sigue el rostro, mide, actualiza la capa temporal. Entrega `resumen` |
| `terminar(t)` | El último tiempo | Cierra los eventos que quedaron abiertos y los entrega |

### Las dos fases

1. **Calibrando.** Dura 5 s desde `iniciar`. Los primeros 3 s la persona mira al frente con los ojos abiertos. Los 2 s siguientes cierra los ojos. Se descarta el primer medio segundo de cada paso. Al terminar se fijan la razón de ojos abiertos, la de ojos cerrados y la medida de la boca en reposo, usando la mediana de los cuadros de cada paso. Durante esta fase no se cuentan eventos.
2. **Vigilando.** Lo normal: estados, eventos, PERCLOS y alertas.

Si en la calibración hubo menos de 3 cuadros útiles por paso, o la razón de ojos abiertos y la de cerrados quedaron a menos de `CALIBRACION_DIFERENCIA_MINIMA`, se conservan las referencias generales de `config.py` y `resumen["aviso"]` lleva un mensaje.

### La clase `Calibracion`

| Campo | Qué guarda |
|---|---|
| `acumulado_ref` | Histograma acumulado de la parte de arriba del rostro de referencia |
| `razon_abierto`, `razon_cerrado` | Medida de ojos con los ojos abiertos y cerrados |
| `boca_umbral_oscuro` | Nivel de gris que cuenta como "oscuro" en la franja de la boca |
| `boca_en_reposo` | Medida de la boca cerrada |
| `aviso` | Mensaje si la calibración de ojos no fue confiable |

### El diccionario `resumen`

Es lo que entrega `procesar` y lo único que necesita la interfaz.

Claves que siempre están:

| Clave | Tipo | Contenido |
|---|---|---|
| `t` | float | Marca de tiempo del cuadro |
| `fase` | str | `"calibrando"` o `"vigilando"` |
| `caja` | tupla | `(x, y, ancho, alto)` del rostro. Si no se encontró, la última caja buena |
| `puntaje` | float | Parecido con la plantilla, entre -1 y 1 |
| `movimiento` | tupla | `(dx, dy)` estimado de la cabeza respecto al cuadro anterior, en pixeles |
| `valor_ojos` | float o None | Apertura de ojos. `None` si el rostro no estaba de frente |
| `valor_boca` | float o None | Apertura de boca. `None` si el rostro no estaba de frente |
| `valor_cabeza` | float | Frontalidad, entre 0 y 1 |
| `razon_ojos` | float o None | Razón de bordes antes de convertirla en apertura |
| `rostro` | arreglo o None | Rostro normalizado de 128×160, para la vista de depuración |
| `aviso` | str | Mensaje de la calibración, o cadena vacía |

Solo durante la calibración:

| Clave | Contenido |
|---|---|
| `instruccion` | Texto que se le muestra a la persona |

Solo durante la vigilancia:

| Clave | Tipo | Contenido |
|---|---|---|
| `estado_ojos`, `estado_boca`, `estado_cabeza` | str | Estado de cada señal |
| `eventos_nuevos` | lista de `Evento` | Eventos que se cerraron en este cuadro |
| `contadores` | dict | Cuántos eventos van, con claves como `"parpadeo:lento"` o `"distraccion:2.0"` |
| `cierre_en_curso_s` | float | Segundos que lleva el cierre de ojos abierto, o 0 |
| `bostezo_en_curso_s` | float | Lo mismo para la boca abierta |
| `distraccion_en_curso_s` | float | Lo mismo para la distracción |
| `perclos` | float o None | Fracción entre 0 y 1. `None` si todavía no se puede calcular |
| `nivel_perclos` | str | `normal`, `alerta`, `fatiga`, `somnolencia`, `calentando` o `sin dato` |
| `alerta` | str | `ninguna`, `aviso`, `alerta` o `critica` |
| `motivo_alerta` | str | Texto corto para la pantalla |

Si la interfaz necesita un dato nuevo, se agrega una clave a `resumen` en `Sistema.procesar` y se documenta aquí.

### Por qué los ojos y la boca usan imágenes distintas

Los ojos se miden sobre el rostro normalizado tal cual. Su medida es un cociente y no depende del brillo ni del contraste.

La boca usa un umbral de gris fijo, así que primero se corrige la iluminación con especificación de histograma. La tabla de corrección se arma con la parte de arriba del rostro (`zona_estable`) y se aplica al rostro completo. Si se armara con el rostro completo, una boca abierta se "corregiría" como si fuera un cambio de luz (decisión D33).

---

## `principal.py`

Programa principal. No contiene algoritmos: conecta la captura, el sistema, la interfaz y la bitácora.

```bash
python -m somnolencia.principal --fuente escena
python -m somnolencia.principal --fuente 0
python -m somnolencia.principal --fuente datos/videos/P01_G2_01.mp4
python -m somnolencia.principal --fuente video.mp4 --sin-ventana --caja 265,111,110,138
```

| Opción | Efecto |
|---|---|
| `--fuente` | `escena`, un número de cámara o la ruta de un video. Por omisión, `0` |
| `--caja x,y,ancho,alto` | Caja del rostro en el primer cuadro, en pixeles de la imagen de 640×360 |
| `--sin-calibracion` | Empieza a vigilar de inmediato, con las referencias generales de ojos |
| `--sin-ventana` | No abre ventanas. Para evaluar videos |
| `--mediciones` | Guarda además un CSV con una fila por cuadro: mediciones, estados, PERCLOS y alerta |
| `--salida carpeta` | Dónde se guarda la bitácora. Por omisión, `salidas` |

Cómo se decide la caja del rostro en el primer cuadro (función `elegir_caja`):

| Situación | Caja |
|---|---|
| Se dio `--caja` | Esa |
| Fuente `escena` | La de la cara dibujada |
| Archivo de video, con ventana | Se marca con el ratón y se pulsa ENTER |
| Cámara, con ventana | Se muestra un recuadro central y se espera la barra espaciadora |
| Sin ventana y sin `--caja` | El recuadro central |

Teclas: `q` salir, `r` reiniciar contadores y PERCLOS, `d` vista de depuración, `c` recalibrar (solo con cámara).

Al terminar imprime cuántos cuadros procesó, el tiempo de proceso por cuadro y los eventos contados.

**Estado.** Probado sin ventana con la escena y con un archivo de video. Probado con ventana, deslizadores y teclas con la escena en Windows. Sin probar: la cámara (`--fuente 0`), la tecla `c` y marcar la caja con el ratón.

---

## `escena_sintetica.py`

Un video dibujado: una cara muy simple (rectángulo con cejas, ojos, nariz y boca) que se mece sobre un fondo y sigue un guion de 45 s.

| Tramo | Qué pasa | Qué debe reportar el sistema |
|---|---|---|
| 0 a 5 s | Calibración: ojos abiertos 3 s y cerrados 2 s | Nada |
| 8.0 a 8.3 s | Ojos cerrados | Parpadeo normal |
| 11 a 14 s | Ojos cerrados | Parpadeo lento |
| 18 a 20.5 s | La cara se sustituye por una textura | Distracción en la banda 2.0 |
| 24 a 27 s | Boca abierta | Bostezo |
| 31 a 39.5 s | Ojos cerrados | Microsueño |

Funciones: `generar(fps, duracion)` entrega `(t, cuadro)` cuadro por cuadro, `cuadro(t, numero)` dibuja un cuadro, `caja_inicial()` da la caja de la cara en el primer cuadro. `EVENTOS_ESPERADOS` es el diccionario de contadores que debe salir.

Sirve para comprobar que las piezas están conectadas y para ver la interfaz sin cámara. No sirve para saber qué tan bien funciona el sistema con una persona.

## `simulador.py`

Genera mediciones inventadas (no imágenes) a partir de un guion, con la misma forma que las que entrega la percepción. Lo usa `pruebas/test_capa_temporal.py` para probar la capa temporal sola.
