# `percepcion/`

De un cuadro de video a tres mediciones. Aquí viven los algoritmos de visión computacional del proyecto.

Cada archivo tiene abajo qué código debe ir, qué recibe, qué entrega, con qué se verifica y cuándo se considera terminado. Los nombres de funciones son una propuesta. Lo que no puede cambiar sin avisar es lo que entregan `ojos.py`, `boca.py` y `cabeza.py`, porque de eso depende la capa temporal.

Orden en que conviene programarlos: `captura`, `preproceso`, `piramide`, `correlacion`, `calibracion`, `rostro`, `geometria`, `gradiente`, `ojos`, `boca`, `cabeza`.

---

## `captura.py` (frente 1)

**Aquí debe ir el código que** abre la cámara o un archivo de video y entrega cuadros con su marca de tiempo.

- `abrir(fuente)`: recibe `"0"` para la cámara o una ruta de video.
- `a_tamano_de_trabajo(cuadro)`: entrega el cuadro en 640×360. Los videos se graban en 1280×720, así que se reducen a la mitad con `piramide.reducir`. En vivo se le pide a la cámara 640×360 directo si lo admite, para ahorrar ese paso.
- `leer(captura)`: entrega `(cuadro, t)` o `None` cuando se acaba el video.

La marca de tiempo se calcula distinto según la fuente:

- Con cámara, `t` es el reloj del sistema al leer el cuadro (`time.monotonic()`), contado desde que arrancó el programa.
- Con archivo, `t` es el número de cuadro dividido entre los cuadros por segundo del video. Así el resultado es el mismo sin importar qué tan rápido procese la computadora, y la evaluación es reproducible.

Usa `cv2.VideoCapture`, permitido por el enunciado para adquirir imágenes.

**Hecho cuando:** imprime resolución y cuadros por segundo reales con cámara y con archivo.

---

## `preproceso.py` (frente 2)

**Aquí debe ir el código que** prepara la imagen: grises, suavizado y especificación de histograma. Se adapta lo hecho en las prácticas 4 y 5.

- `a_grises(cuadro)`: conversión de formato.
- `suavizar_binomial(img)`: filtro pasabajas con el núcleo binomial de `config.py`, aplicado de forma separable (primero por renglones, después por columnas).
- `histograma_acumulado(img)`: entrega el histograma acumulado normalizado.
- `especificar_histograma(img, acumulado_ref)`: transforma los niveles de gris de `img` para que su histograma acumulado se parezca al de referencia. Para cada nivel de entrada se busca el nivel cuyo acumulado de referencia es el más cercano, y con eso se arma una tabla de 256 entradas.

La especificación se aplica al rostro normalizado, que es pequeño, y no al cuadro completo.

Para que sea rápido: el filtro separable con un núcleo de 5 se escribe como la suma de 5 copias desplazadas del arreglo, sin ciclos por pixel.

**Se verifica contra:** `cv2.GaussianBlur` con el mismo núcleo, y la comparación de acumulados antes y después de especificar.

**Hecho cuando:** las dos verificaciones están en `verificacion/` y la función tarda menos de 3 ms sobre un rostro de 128×160.

---

## `piramide.py` (frente 1)

**Aquí debe ir el código que** construye la pirámide gaussiana y la banda laplaciana. Se adapta lo hecho en la práctica 6.

- `reducir(img)`: suaviza con el binomial y se queda con un pixel de cada dos en cada dirección.
- `piramide_gaussiana(img, niveles)`: lista de imágenes, de la más grande a la más pequeña.
- `banda_laplaciana(img)`: la imagen menos su versión suavizada. Conserva bordes y detalles y descarta los cambios lentos de iluminación.

**Se verifica contra:** `cv2.pyrDown`.

**Hecho cuando:** la verificación está en `verificacion/` y construir tres niveles desde 640×360 tarda menos de 5 ms.

---

## `correlacion.py` (frentes 1 y 3)

**Aquí debe ir el código que** compara imágenes de dos maneras.

### Correlación normalizada (frente 1)

- `correlacion_normalizada(ventana, plantilla)`: desliza la plantilla sobre la ventana y entrega un mapa con un valor entre -1 y 1 por posición. En cada posición se resta la media a los dos recortes, se multiplican pixel a pixel, se suma y se divide entre el producto de sus normas.

Restar la media y dividir entre las normas hace que el resultado no cambie si la imagen se aclara o se oscurece de manera uniforme.

**Se verifica contra:** `cv2.matchTemplate` con el método `TM_CCOEFF_NORMED`. El máximo debe caer en la misma posición.

### Correlación de fase (frente 3)

- `correlacion_de_fase(a, b)`: entrega `(dx, dy, pico)`, el desplazamiento entre dos imágenes del mismo tamaño y qué tan nítido fue el resultado.

Pasos: multiplicar ambas imágenes por una ventana que las atenúe hacia los bordes, calcular sus transformadas de Fourier, multiplicar una por el conjugado de la otra, dividir entre la magnitud para quedarse solo con la fase, regresar con la transformada inversa y buscar el máximo. La posición del máximo es el desplazamiento. Los máximos que caen en la segunda mitad del arreglo corresponden a desplazamientos negativos.

**Se verifica contra:** un desplazamiento puesto a mano (por ejemplo, recorrer una imagen 5 px a la derecha y 3 hacia abajo y recuperar esos números) y `cv2.phaseCorrelate`. Cuidado con el signo: hay que comprobar con el desplazamiento conocido cuál imagen se toma como referencia.

**Hecho cuando:** las dos verificaciones están en `verificacion/`.

---

## `calibracion.py` (frente 1, con frente 2 para el paso de ojos)

**Aquí debe ir el código que** aprende las referencias de la persona al inicio de la sesión, en los dos pasos descritos en `docs/arquitectura.md`.

- `calibrar(captura, interfaz)`: entrega un objeto `Calibracion` con:
  - la plantilla frontal del rostro en cada nivel de la pirámide,
  - la caja inicial del rostro,
  - el histograma acumulado de referencia,
  - las filas de la franja de ojos y de la franja de boca,
  - la separación de párpados con ojos abiertos y con ojos cerrados,
  - la separación de labios en reposo.

Detalles:

- La plantilla se toma del recuadro que la interfaz muestra en pantalla.
- Las separaciones de referencia son la **mediana** de los cuadros de cada paso. Con la mediana, un parpadeo durante el paso de ojos abiertos no arruina la referencia.
- La franja de ojos son las filas donde el perfil de gradiente más cambia entre el paso de ojos abiertos y el de ojos cerrados.
- Si la separación abierta y la cerrada salen casi iguales, la calibración falló. Se avisa en pantalla y se repite.

La calibración vive en memoria. Contiene una imagen del rostro, así que no se guarda en el repositorio.

**Hecho cuando:** al terminar la calibración se muestran en pantalla la plantilla, las dos franjas marcadas y las tres separaciones.

---

## `rostro.py` (frente 1)

**Aquí debe ir el código que** encuentra el rostro en cada cuadro a partir de dónde estaba en el anterior.

- `seguir(piramide, calibracion, caja_anterior)`: entrega `(caja, puntaje)`.

Pasos:

1. En el nivel más pequeño de la pirámide, calcular la banda laplaciana y buscar la plantilla con correlación normalizada, solo en una ventana de `BUSQUEDA_VENTANA_PX` alrededor de la posición anterior.
2. Afinar la posición en el nivel siguiente con una ventana de 2 px.
3. Convertir la posición a coordenadas del cuadro completo.
4. Si el puntaje se mantiene bajo varios cuadros seguidos, buscar en toda la imagen del nivel más pequeño para reencontrar el rostro.

La plantilla no se actualiza durante la sesión. Si se actualizara con cada cuadro, poco a poco dejaría de ser un rostro de frente y la caída del puntaje dejaría de significar "volteó".

**Hecho cuando:** en vivo la caja sigue la cara al moverse despacio, el puntaje baja claramente al voltear y el rostro se reencuentra en menos de un segundo al regresar.

---

## `geometria.py` (frente 1)

**Aquí debe ir el código que** recorta el rostro y lo lleva a un tamaño fijo con mapeo inverso. Se adapta lo hecho en la práctica 3.

- `normalizar_rostro(img, caja)`: entrega una imagen de `ROSTRO_ANCHO` × `ROSTRO_ALTO`.

Para cada pixel de la imagen de salida se calcula de qué coordenada de la imagen original viene (escala y traslación) y se interpola entre los cuatro pixeles vecinos. Se recorre la salida y no la entrada para que no queden huecos.

Las coordenadas de todos los pixeles de salida se calculan de una vez con arreglos de NumPy, sin ciclos.

**Se verifica contra:** `cv2.warpAffine` con la misma transformación.

**Hecho cuando:** la verificación está en `verificacion/` y el rostro normalizado se ve estable en vivo.

---

## `gradiente.py` (frente 2)

**Aquí debe ir el código que** mide la separación entre dos bordes horizontales dentro de una franja. Lo usan `ojos.py` y `boca.py`.

- `gradiente_vertical(img)`: derivada en dirección vertical con el núcleo de Sobel, aplicada de forma separable (suavizado `[1, 2, 1]` a lo ancho y diferencia `[-1, 0, 1]` a lo alto).
- `perfil_por_renglon(grad)`: suma del valor absoluto del gradiente a lo largo de cada renglón. Entrega un número por renglón.
- `separacion_de_picos(perfil)`: distancia en pixeles entre los dos picos principales del perfil.

Dificultad conocida: elegir "los dos picos principales" puede ser inestable cuando hay ruido o armazones de lentes. Si pasa, la alternativa es medir qué tan repartido está el perfil (la desviación estándar de las filas, pesada por el perfil) en lugar de buscar picos. Entrega un número con el mismo sentido: grande con el ojo abierto, pequeño con el ojo cerrado.

**Se verifica contra:** `cv2.Sobel` para el gradiente, y una imagen sintética con dos líneas horizontales a distancia conocida para la separación.

**Hecho cuando:** sobre imágenes de ojos abiertos y cerrados de Kaggle, las separaciones de los dos grupos se distinguen a simple vista en un histograma.

---

## `ojos.py` (frente 2)

**Aquí debe ir el código que** entrega la apertura de los ojos como `Medicion`.

- `medir_ojos(rostro_normalizado, calibracion, t)`: entrega `Medicion`.

Pasos:

1. Recortar la franja de ojos guardada en la calibración.
2. Suavizar y calcular la separación con `gradiente.py`.
3. Convertir a apertura: `(separación − cerrada) / (abierta − cerrada)`, recortada entre 0 y 1.
4. Entregar `Medicion(t, apertura, valido=True)`.

Si el rostro no se encontró bien en este cuadro, `principal.py` no llama a esta función y la medición queda como no válida.

Se miden los dos ojos juntos en una sola franja. Medirlos por separado es una mejora posible.

**Hecho cuando:** en vivo la apertura se mantiene arriba de 0.6 con los ojos abiertos y baja de 0.2 al cerrarlos, y el F1 por cuadro está reportado en `evaluacion/`.

---

## `boca.py` (frente 3)

**Aquí debe ir el código que** entrega la apertura de la boca como `Medicion`.

- `medir_boca(rostro_normalizado, calibracion, t)`: entrega `Medicion`.

Igual que los ojos, con la franja de boca. El valor es la separación de labios menos la de reposo, dividida entre el alto del rostro normalizado y recortada entre 0 y 1.

Lo que hay que observar con los videos de guion G3: qué valores da al hablar, al sonreír y al bostezar. El umbral de `config.py` se coloca entre hablar y bostezar. La duración mínima del bostezo (D11) hace el resto.

**Hecho cuando:** en vivo un bostezo supera el umbral durante más de un segundo y hablar no lo hace de forma sostenida.

---

## `cabeza.py` (frente 3)

**Aquí debe ir el código que** dice qué tan de frente está la cabeza y cuánto se movió.

- `medir_cabeza(puntaje, rostro_actual, rostro_anterior, t)`: entrega `Medicion` y el desplazamiento `(dx, dy)`.

El valor de la medición es el puntaje de correlación del seguimiento, llevado al rango de 0 a 1. Cuando la persona voltea, el rostro deja de parecerse a la plantilla frontal y el valor baja.

La correlación de fase entre el rostro actual y el anterior da el desplazamiento de la cabeza. Sirve para dos cosas: mostrar en la interfaz hacia dónde se mueve, y distinguir un giro (hay movimiento justo antes de que caiga el puntaje) de una falla por luz (el puntaje cae sin movimiento).

A diferencia de ojos y boca, esta medición siempre es válida. Si el rostro no aparece, el valor es 0 (decisión D14).

**Hecho cuando:** con los videos de guion G4 el valor baja del umbral durante los giros y se recupera al regresar, y el desplazamiento apunta hacia el lado correcto.
