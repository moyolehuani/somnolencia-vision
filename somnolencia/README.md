# Paquete `somnolencia`

Este es el sistema. Es lo único que se ejecuta en la demo.

```
somnolencia/
├── config.py       umbrales y parámetros
├── tipos.py        estructuras compartidas
├── simulador.py    mediciones inventadas, para probar sin cámara
├── principal.py    ciclo principal
├── percepcion/     de un cuadro a tres mediciones
├── temporal/       de mediciones a eventos, PERCLOS y alertas
└── interfaz/       overlay, controles y bitácora
```

## Reglas de este paquete

- No se importa ninguna red ni modelo preentrenado.
- En `percepcion/` no se usan las funciones de OpenCV equivalentes a los algoritmos propios (`cv2.GaussianBlur`, `cv2.Sobel`, `cv2.equalizeHist`, `cv2.pyrDown`, `cv2.matchTemplate`, `cv2.phaseCorrelate`, `cv2.warpAffine`, `cv2.resize`). Esas van solo en `verificacion/`.
- `temporal/` no importa `cv2` ni recibe imágenes. Solo números y tiempos.
- Ningún archivo lleva umbrales escritos a mano. Todos se leen de `config.py`.
- Cada función tiene un comentario inicial que dice qué recibe, qué entrega y qué algoritmo implementa.

Las dos primeras reglas se comprueban con una prueba automática (ver `pruebas/README.md`).

## `config.py`

**Aquí debe ir** la lista de todos los parámetros del sistema. Cada uno con un comentario que diga de dónde sale el valor. Responsable: frente 4. Los demás frentes proponen sus parámetros.

### Valores que fija el enunciado

| Nombre | Valor | Fuente |
|---|---|---|
| `PARPADEO_NORMAL_MAX_S` | 0.5 | Tabla 1 del enunciado |
| `PARPADEO_LENTO_MAX_S` | 7.0 | Tabla 1 del enunciado, criterio de la referencia [3] |
| `BANDAS_DISTRACCION_S` | (0.5, 1.0, 1.5, 2.0) | Enunciado. Interpretación en D10 |
| `PERCLOS_VENTANA_S` | 30.0 | Enunciado |
| `PERCLOS_ALERTA` | 0.08 | Enunciado |
| `PERCLOS_FATIGA` | 0.15 | Enunciado |
| `PERCLOS_SOMNOLENCIA` | 0.30 | Enunciado |
| `AVISO_CIERRE_EN_CURSO_S` | 1.5 | Umbral de alerta de la referencia [1] del enunciado |

### Valores que fija el equipo

Todos son provisionales hasta ajustarlos con los videos de ajuste.

| Nombre | Valor inicial | Decisión |
|---|---|---|
| `PERCLOS_CUENTA_PARPADEOS_NORMALES` | `False` | D09 |
| `PERCLOS_TIEMPO_MINIMO_S` | 10.0 | Antes de ese tiempo PERCLOS se muestra como "calentando" |
| `BOSTEZO_MIN_S` | 1.5 | D11 |
| `OJOS_UMBRAL_CIERRE` | 0.20 | D15 |
| `OJOS_UMBRAL_REAPERTURA` | 0.35 | D15 |
| `BOCA_UMBRAL_APERTURA` | 0.20 | Por ajustar |
| `BOCA_UMBRAL_CIERRE` | 0.14 | Por ajustar |
| `CABEZA_UMBRAL_DISTRAIDO` | 0.50 | Por ajustar |
| `CABEZA_UMBRAL_ATENTO` | 0.60 | Por ajustar |
| `ANTIRREBOTE_CUADROS` | 2 | D16 |
| `SIN_DATO_TOLERANCIA_S` | 0.3 | Si un evento abierto pasa más de este tiempo sin dato, se cierra como indeterminado |
| `GRABACION_ANCHO`, `GRABACION_ALTO` | 1280, 720 | D18. Tamaño de los videos |
| `TRABAJO_ANCHO`, `TRABAJO_ALTO` | 640, 360 | D18. Tamaño al que procesa el sistema |
| `ROSTRO_ANCHO`, `ROSTRO_ALTO` | 128, 160 | D18 |
| `PIRAMIDE_NIVELES` | 3 | D18 |
| `BUSQUEDA_VENTANA_PX` | 8 | En el nivel más pequeño de la pirámide |
| `CALIBRACION_ABIERTOS_S` | 3.0 | D25 |
| `CALIBRACION_CERRADOS_S` | 2.0 | D25 |
| `NUCLEO_BINOMIAL` | (1, 4, 6, 4, 1) | Práctica 5 |

## `tipos.py`

**Aquí debe ir** la definición de las estructuras que comparten los módulos: `Medicion`, `Evento`, `Calibracion` y los nombres de los estados. Están descritas en `docs/arquitectura.md`. Responsable: frente 4.

Estados:

| Señal | Estados |
|---|---|
| Ojos | `ABIERTO`, `CERRADO`, `SIN_DATO` |
| Boca | `CERRADA`, `ABIERTA`, `SIN_DATO` |
| Cabeza | `ATENTO`, `DISTRAIDO` |

## `simulador.py`

**Aquí debe ir** el código que genera mediciones inventadas con la misma forma que las reales, a partir de un guion escrito en el propio archivo. Por ejemplo: ojos abiertos de 0 a 10 s, cerrados de 10 a 13 s, abiertos de 13 a 20 s, cabeza distraída de 15 a 17 s.

Sirve para que la capa temporal y la interfaz se desarrollen y se prueben sin esperar a la percepción. Responsable: frente 4.

**Hecho cuando:** `python -m somnolencia.principal --fuente simulador` muestra la interfaz reaccionando al guion.

## `principal.py`

**Aquí debe ir** el ciclo que une todo. No contiene algoritmos, solo llama a los módulos en orden. Responsable: frente 4.

En palabras:

```
leer argumentos (--fuente)
abrir la fuente
calibrar (paso 1 y paso 2)
repetir hasta que se pulse "q" o se acabe el video:
    leer cuadro y tiempo
    pasar a grises y construir pirámide
    seguir el rostro  ->  caja, puntaje
    si el puntaje es suficiente:
        normalizar el rostro y especificar su histograma
        medir ojos y boca
    si no:
        ojos y boca quedan sin dato
    medir cabeza
    actualizar estados, eventos, PERCLOS y alertas
    dibujar overlay y mostrar
    guardar en bitácora los eventos que se cerraron
    atender teclas y deslizadores
cerrar la fuente y la bitácora
```

Además mide cuánto tarda cada etapa, para `evaluacion/desempeno.py`.

**Hecho cuando:** corre con cámara, con un archivo de video y con el simulador, usando el mismo código.
