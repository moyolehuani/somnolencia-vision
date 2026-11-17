# `percepcion/`

De un cuadro de video a tres mediciones: apertura de ojos, apertura de boca y frontalidad de la cabeza. Aquí viven todos los algoritmos de visión computacional del proyecto, escritos a mano con NumPy.

## Estado

| Archivo | Frente | Qué hace | Estado |
|---|---|---|---|
| `preproceso.py` | 2 | Grises, filtros, histograma | Verificado contra OpenCV |
| `gradiente.py` | 2 | Gradientes de Sobel y razón de bordes | Verificado contra OpenCV |
| `ojos.py` | 2 | Apertura de ojos | Probado con Kaggle (F1 de 0.84 a 0.86 sin calibración). Falta probarlo con calibración y video |
| `piramide.py` | 1 | Pirámide gaussiana y banda laplaciana | Verificado contra OpenCV |
| `correlacion.py` | 1 y 3 | Correlación normalizada y de fase | Verificado contra OpenCV |
| `geometria.py` | 1 | Mapeo inverso y recortes de ojos | Verificado contra OpenCV. Las filas de los recortes son provisionales |
| `rostro.py` | 1 | Seguimiento del rostro | Probado con la escena dibujada. Sin probar con personas |
| `captura.py` | 1 | Lectura de cámara, video o escena | Probado con escena y archivo. Sin probar con cámara |
| `cabeza.py` | 3 | Frontalidad | Probado con la escena dibujada |
| `boca.py` | 3 | Apertura de boca | Probado con la escena dibujada. Sin validar con bocas reales (D31) |

Qué significa cada nivel:

- **Verificado contra OpenCV.** El algoritmo propio da lo mismo que la función de biblioteca. Se comprueba con `python -m verificacion.verificar` y con `pytest`.
- **Probado con Kaggle.** La medida distingue ojos abiertos de cerrados en fotos reales.
- **Probado con la escena dibujada.** Funciona con la cara de dibujo de `escena_sintetica.py`. Comprueba que las piezas están conectadas. No comprueba que funcione con una persona.

La calibración no está en esta carpeta. Vive en `somnolencia/sistema.py`.

## Convenciones

- Las imágenes son arreglos de NumPy en grises, `float32`, con valores de 0 a 255 y forma `(alto, ancho)`.
- Las cajas son `(x, y, ancho, alto)` en pixeles.
- Los parámetros salen de `config.py`.
- No se usan las funciones de OpenCV equivalentes a estos algoritmos. Una prueba lo vigila.

## Cómo se conectan los archivos

```
captura.py ──> gris 640x360
                 │
piramide.py ──> 3 niveles ──> rostro.py (usa correlacion.py) ──> caja, puntaje
                                                                   │
                              geometria.py ──> rostro 128x160 <────┘
                                 │                    │
                     recortes de ojos            preproceso.py (histograma)
                                 │                    │
                 ojos.py (usa gradiente.py)        boca.py
                                 │                    │
                             Medicion              Medicion        cabeza.py ──> Medicion
```

`preproceso.filtrar_1d` es la base de todos los filtros: la usan el suavizado, los gradientes y la pirámide.

---

## `preproceso.py`

Filtros espaciales (práctica 5) y especificación de histograma (práctica 4).

| Función | Recibe | Entrega |
|---|---|---|
| `a_grises(cuadro)` | Cuadro BGR de OpenCV | Imagen en grises `float32` |
| `filtrar_1d(img, nucleo, eje)` | Imagen, núcleo de una dimensión, `eje` 0 (vertical) o 1 (horizontal) | Imagen filtrada, del mismo tamaño |
| `suavizar_binomial(img)` | Imagen | Imagen suavizada con el núcleo (1, 4, 6, 4, 1)/16 en las dos direcciones |
| `histograma_acumulado(img)` | Imagen | Arreglo de 256 valores entre 0 y 1 |
| `tabla_de_especificacion(img, acumulado_ref)` | Imagen y acumulado de referencia | Tabla de 256 entradas: a qué nivel va cada nivel de gris |
| `aplicar_tabla(img, tabla)` | Imagen y tabla | Imagen con los niveles reemplazados |
| `especificar_histograma(img, acumulado_ref)` | Imagen y acumulado de referencia | Lo mismo que armar la tabla con la imagen y aplicársela |

### Cómo funciona `filtrar_1d`

En vez de recorrer la imagen pixel por pixel, suma copias desplazadas de la imagen, cada una multiplicada por un peso del núcleo. Con un núcleo de 5 elementos son 5 sumas de arreglos completos.

En las orillas la imagen se extiende reflejándola (`np.pad` con modo `reflect`). Es el mismo tratamiento que usa OpenCV por omisión, y por eso los resultados coinciden hasta el redondeo.

Un filtro de dos dimensiones separable se obtiene llamándola dos veces, una por eje. El binomial de 5×5 cuesta así 10 sumas en vez de 25.

### Cómo funciona la especificación de histograma

Para cada nivel de gris `g` de la imagen se busca el nivel `r` cuyo acumulado de referencia es el más cercano al acumulado de `g` en la imagen.

Ejemplo. Si el 30% de los pixeles de la imagen tiene nivel 80 o menos, y en la referencia el 30% tiene nivel 120 o menos, la tabla manda el nivel 80 al 120.

Cuidado: supone que la imagen y la referencia muestran lo mismo y que solo cambió la luz. Si cambia el contenido, la especificación lo "corrige" como si fuera luz. Por eso el sistema arma la tabla con la parte de arriba del rostro y la aplica al rostro completo (decisión D33).

**Verificación.** `suavizar_binomial` contra `cv2.GaussianBlur` (diferencia de 0.00005). `especificar_histograma` con referencia uniforme contra `cv2.equalizeHist` (diferencia de 1 nivel, por redondeo). Al corregir una imagen oscurecida, la diferencia entre acumulados baja de 0.609 a 0.014.

---

## `gradiente.py`

Gradientes de Sobel (práctica 5) y la medida de bordes de los ojos.

| Función | Recibe | Entrega |
|---|---|---|
| `gradiente_vertical(img)` | Imagen | Derivada vertical. Responde a bordes horizontales |
| `gradiente_horizontal(img)` | Imagen | Derivada horizontal. Responde a bordes verticales |
| `banda_mas_oscura(img, columnas, alto_de_banda)` | Imagen, `(c0, c1)`, número de renglones | Primer renglón del grupo de renglones seguidos más oscuro |
| `razon_de_bordes(ojo)` | Recorte de un ojo ya suavizado | Suma de bordes verticales entre suma de bordes horizontales |

Los gradientes se aplican de forma separable: suavizado `(1, 2, 1)` en una dirección y diferencia `(-1, 0, 1)` en la otra.

### La idea de `razon_de_bordes`

Un ojo abierto muestra el iris, que es un disco oscuro. Sus lados son bordes verticales y aparecen en el gradiente horizontal. Un ojo cerrado solo tiene la línea de las pestañas, que es un borde horizontal y aparece en el gradiente vertical.

Pasos:

1. Se toman las columnas centrales del recorte (`OJOS_COLUMNA_INICIAL` a `OJOS_COLUMNA_FINAL`).
2. Se busca la banda de `OJOS_ALTO_DE_BANDA` renglones más oscura. Ahí está el iris o la línea de pestañas.
3. Se toma esa banda con `OJOS_MARGEN_DE_BANDA` renglones extra arriba y abajo.
4. Dentro de esa zona se suman los valores absolutos del gradiente horizontal y del vertical, y se dividen.

Resultado medido en el dataset de Kaggle: mediana de 0.72 en ojos abiertos y de 0.41 en ojos cerrados.

**Lo que se descartó.** El primer diseño medía la separación entre los picos del perfil del gradiente vertical (los bordes de los párpados). Con imágenes reales no distinguió abierto de cerrado mejor que el azar, porque la ceja, las pestañas y los pliegues del párpado producen picos propios. Decisión D28.

**Verificación.** Contra `cv2.Sobel`, diferencia de 0.0001.

---

## `ojos.py`

Convierte los recortes de los ojos en una `Medicion`.

| Función | Recibe | Entrega |
|---|---|---|
| `razon_de_un_ojo(ojo_gris)` | Recorte de un ojo, de 64 px de ancho | Razón de bordes |
| `apertura_desde_razon(razon, razon_abierto, razon_cerrado)` | La razón y sus dos referencias | Apertura entre 0 y 1 |
| `medir_ojos(ojo_izquierdo, ojo_derecho, t, razon_abierto, razon_cerrado)` | Los dos recortes, el tiempo y las referencias | `Medicion` con el promedio de las dos aperturas |

`razon_de_un_ojo` descarta el 30% superior del recorte (la ceja), suaviza y llama a `razon_de_bordes`.

`apertura_desde_razon` calcula `(razon − cerrado) / (abierto − cerrado)` y recorta el resultado entre 0 y 1. Con referencias 0.74 y 0.39, una razón de 0.60 da 0.60.

Las referencias vienen de la calibración de la persona. Si no hay, `medir_ojos` usa las de `config.py`.

**Evidencia.** `python -m evaluacion.por_cuadro <carpeta>` sobre los 1452 recortes de Kaggle da F1 de 0.86 y 0.84, sin calibración y con un solo umbral.

**Falta.** Probarlo en video con calibración. Ajustar dónde se recortan los ojos (`OJOS_FILA_INICIAL` y `OJOS_FILA_FINAL`). Tareas T02 y T11 de `docs/tareas_pendientes.md`.

---

## `piramide.py`

Pirámide gaussiana y banda laplaciana (práctica 6).

| Función | Recibe | Entrega |
|---|---|---|
| `reducir(img)` | Imagen | Imagen de la mitad de ancho y alto |
| `piramide_gaussiana(img, niveles)` | Imagen y número de niveles | Lista de imágenes, de la más grande a la más pequeña |
| `banda_laplaciana(img)` | Imagen | La imagen menos su versión suavizada |

`reducir` suaviza con el binomial y conserva un pixel de cada dos. Con 3 niveles y un cuadro de 640×360 salen 640×360, 320×180 y 160×90.

La banda laplaciana conserva bordes y detalles y descarta los cambios lentos de brillo. El rostro se busca sobre ella para depender poco de la iluminación.

**Verificación.** `reducir` contra `cv2.pyrDown`, diferencia de 0.00003.

---

## `correlacion.py`

Dos formas de comparar imágenes.

| Función | Recibe | Entrega |
|---|---|---|
| `correlacion_normalizada(imagen, plantilla)` | Imagen y plantilla más pequeña | Mapa con un valor entre -1 y 1 por posición |
| `posicion_del_maximo(mapa)` | Un mapa | `(y, x, valor)` del punto más alto |
| `correlacion_de_fase(anterior, actual)` | Dos imágenes del mismo tamaño | `(dx, dy, pico)` |

### Correlación normalizada

En cada posición se recorta el trozo de imagen que queda bajo la plantilla, se resta la media al trozo y a la plantilla, se multiplican pixel a pixel, se suma y se divide entre el producto de sus normas.

Restar las medias quita el efecto del brillo. Dividir entre las normas quita el del contraste. El valor 1 significa que el trozo es idéntico a la plantilla salvo por brillo y contraste.

El mapa mide `(alto de imagen − alto de plantilla + 1)` por `(ancho de imagen − ancho de plantilla + 1)`. La posición `(y, x)` corresponde a poner la esquina superior izquierda de la plantilla en ese pixel.

Hay un ciclo por posición, así que conviene pasarle solo la zona donde puede estar la plantilla. Buscar en 17×17 posiciones tarda unos 3 a 5 ms. Buscar en toda la imagen de 160×90 tarda cerca de 80 ms.

### Correlación de fase

Mide cuánto se desplazó el contenido de `actual` respecto a `anterior`. `dx` positivo es hacia la derecha y `dy` positivo es hacia abajo. `pico` va de 0 a 1 y dice qué tan nítido fue el resultado.

Pasos: multiplicar las dos imágenes por una ventana de Hanning, calcular sus transformadas de Fourier, multiplicar el conjugado de una por la otra, dividir entre la magnitud para quedarse con la fase, regresar con la transformada inversa y buscar el máximo. Un máximo en la segunda mitad del arreglo es un desplazamiento negativo.

Funciona porque desplazar una imagen no cambia la magnitud de su transformada, solo su fase, y la cambia en proporción al desplazamiento.

En el sistema se usa para predecir hacia dónde se movió el rostro antes de buscarlo (ver `rostro.py`).

**Verificación.** La normalizada contra `cv2.matchTemplate` (diferencia de 0.00002 y mismo máximo). La de fase recupera cinco desplazamientos conocidos con error 0 y difiere 0.33 px de `cv2.phaseCorrelate`, que entrega decimales.

---

## `geometria.py`

Recorte y cambio de tamaño con mapeo inverso (práctica 3).

| Función | Recibe | Entrega |
|---|---|---|
| `recortar_y_escalar(img, caja, ancho_salida, alto_salida)` | Imagen, caja y tamaño deseado | La región de la caja con ese tamaño |
| `normalizar_rostro(img, caja)` | Imagen y caja del rostro | Rostro de 128×160 |
| `recortes_de_ojos(rostro)` | Rostro normalizado | Dos recortes de 64 px de ancho, uno por mitad |

Mapeo inverso quiere decir que se recorre la imagen de salida y, para cada pixel, se calcula de qué punto de la original viene. Recorrer la original dejaría huecos. Como el punto de origen casi nunca cae sobre un pixel exacto, su valor se interpola entre los cuatro vecinos (interpolación bilineal).

La transformación solo escala y traslada. Por eso la coordenada x de origen depende solo de la columna y la coordenada y solo del renglón, y se calculan una vez por columna y por renglón, sin ciclos.

`recortes_de_ojos` toma las filas entre `OJOS_FILA_INICIAL` y `OJOS_FILA_FINAL` del rostro y las parte en dos mitades. Esas filas son provisionales.

**Verificación.** Contra `cv2.warpAffine`, diferencia de 0.0006.

**Falta.** Ajustar las filas de los ojos con caras reales (tarea T02).

---

## `rostro.py`

Seguimiento del rostro. El rostro no se detecta: se sigue a partir de una plantilla tomada en la calibración.

| Elemento | Recibe | Entrega |
|---|---|---|
| `recortar(img, x, y, ancho, alto)` | Imagen y región | Recorte sin cambiar de tamaño |
| `buscar_cerca(banda, plantilla, centro_x, centro_y, ventana)` | Banda laplaciana, plantilla, centro y radio de búsqueda | `(x, y, puntaje)` del mejor lugar |
| `SeguidorDeRostro(piramide, caja)` | Pirámide del cuadro de calibración y caja del rostro | Objeto que guarda las plantillas |
| `SeguidorDeRostro.seguir(piramide)` | Pirámide de un cuadro nuevo | `(caja, puntaje, movimiento)` |

### Qué guarda el seguidor

Dos plantillas, recortadas de la banda laplaciana: una del nivel intermedio (320×180) y otra del nivel más pequeño (160×90). Usan solo el 65% superior de la caja del rostro (`PLANTILLA_FRACCION_ALTO`): frente, ojos y nariz. La boca queda fuera para que un bostezo no baje el parecido.

### Qué hace `seguir` en cada cuadro

1. **Predicción.** Correlación de fase entre la zona del rostro en el cuadro anterior y en el actual, en el nivel más pequeño. Si el pico es de al menos `FASE_PICO_MINIMO`, el centro de búsqueda se mueve esa cantidad.
2. **Búsqueda gruesa.** Correlación normalizada en el nivel más pequeño, en una ventana de `BUSQUEDA_VENTANA_PX` alrededor de la predicción. De aquí sale el puntaje.
3. **Búsqueda completa, si hace falta.** Si el puntaje quedó debajo de `CABEZA_UMBRAL_DISTRAIDO`, cada `REBUSCAR_CADA_CUADROS` cuadros se busca en toda la imagen pequeña.
4. **Afinado.** Si se encontró, se afina la posición en el nivel intermedio con una ventana de `AFINADO_VENTANA_PX` y se actualiza la caja. Si no, la caja se queda donde estaba, para reencontrar el rostro ahí cuando la persona regrese.

El puntaje es la señal de distracción: cuando la persona voltea, lo que se ve deja de parecerse a la plantilla de frente.

### Limitaciones

- La plantilla no cambia de tamaño. La persona debe quedarse más o menos a la misma distancia.
- La plantilla no se actualiza durante la sesión. Si se actualizara, dejaría poco a poco de ser un rostro de frente.
- Los ojos están dentro de la plantilla, así que cerrarlos baja el puntaje. Con la cara dibujada baja de 0.91 a 0.70. Si con una persona bajara de 0.50, un cierre de ojos se tomaría por distracción. Es el riesgo de la decisión D32 y lo primero que hay que medir con un video real (tarea T03).

**Pruebas.** `pruebas/test_sistema.py`: encuentra una cara movida 12 px, alcanza una movida 48 px gracias a la predicción, y deja la caja quieta si la cara desaparece.

---

## `captura.py`

Lee cuadros de una cámara, de un archivo o de la escena dibujada, y los entrega en grises y en el tamaño de trabajo.

| Elemento | Recibe | Entrega |
|---|---|---|
| `a_tamano_de_trabajo(gris)` | Imagen en grises de cualquier tamaño | Imagen de 640 px de ancho, a lo más 360 de alto |
| `Captura(fuente)` | `"0"`, `"1"`, `"escena"` o una ruta | Objeto de captura |
| `Captura.leer()` | Nada | `(gris, t)` o `None` cuando se acaban los cuadros |
| `Captura.cerrar()` | Nada | Libera la cámara o el archivo |

Cómo se lleva al tamaño de trabajo:

| Ancho de entrada | Método |
|---|---|
| 640 | Se deja igual |
| 1280 | `reducir` de la pirámide |
| Otro | `recortar_y_escalar` conservando la proporción |

Si después de eso la imagen es más alta que 360 (cámaras 4:3), se conserva la franja central.

La marca de tiempo depende de la fuente. Con cámara es el reloj de la computadora. Con un archivo es el número de cuadro entre los cuadros por segundo del video, para que el resultado sea el mismo sin importar la velocidad de proceso. Por eso los videos deben tener cuadros por segundo constantes (`datos/README.md`).

**Falta.** Probar con cámara.

---

## `cabeza.py`

| Función | Recibe | Entrega |
|---|---|---|
| `medir_cabeza(puntaje, t)` | Puntaje del seguimiento (entre -1 y 1) y tiempo | `Medicion` con el puntaje recortado entre 0 y 1 |

Esta medición siempre es válida. Si el rostro no aparece, el valor es bajo y eso cuenta como distracción (decisión D14).

**Falta.** Ajustar `CABEZA_UMBRAL_DISTRAIDO` y `CABEZA_UMBRAL_ATENTO` con los videos del guion G4. Distinguir un giro de una falla por luz usando el movimiento que entrega el seguidor (opcional).

---

## `boca.py`

Apertura de la boca. **La medida no está validada con bocas reales** (decisión D31).

| Función | Recibe | Entrega |
|---|---|---|
| `franja_de_boca(rostro)` | Rostro normalizado | Recorte de la zona de la boca |
| `umbral_oscuro_en_reposo(rostro)` | Rostro con la boca cerrada | Nivel de gris que separa "oscuro" de "piel" |
| `medida_de_boca(rostro, umbral_oscuro)` | Rostro y umbral | Alto de la zona oscura entre el alto del rostro |
| `medir_boca(rostro, t, umbral_oscuro, medida_en_reposo)` | Rostro, tiempo, umbral y valor en reposo | `Medicion` |

Idea: al abrir la boca aparece una zona oscura cuyo alto crece con la apertura.

- El umbral es el punto medio entre lo más oscuro de la franja en reposo (percentil 2, la línea de los labios) y su nivel típico (la mediana, la piel).
- En cada columna de la franja se cuentan los pixeles más oscuros que el umbral. Se ordenan las columnas y se toma la mediana de la cuarta parte más alta.
- Ese alto se divide entre el alto del rostro y se le resta el valor en reposo.

El rostro que recibe debe tener ya la iluminación corregida, porque el umbral es un nivel de gris fijo.

**Falta.** Validarla con los videos del guion G3: qué valores da al hablar, al sonreír y al bostezar (tarea T07). Si no separa, hay que cambiar de medida, como pasó con los ojos.
