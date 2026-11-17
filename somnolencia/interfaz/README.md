# `interfaz/`

Lo que se ve en pantalla y lo que se guarda. Responsable: frente 4.

La interfaz vale 15% de la calificación junto con la integración, y el video demostrativo debe mostrar la modificación interactiva de parámetros.

Se usa OpenCV para ventanas, dibujo y deslizadores. El enunciado lo permite para visualización e interfaces. Aquí sí se puede usar `cv2.resize`, porque es presentación y no parte de un algoritmo.

## Estado

| Archivo | Qué hace | Estado |
|---|---|---|
| `overlay.py` | Dibuja el video anotado, el tablero y la vista de depuración | Probado: pruebas automáticas y revisión en pantalla con la escena |
| `controles.py` | Ventana de deslizadores con leyenda | Probado en Windows con la escena |
| `bitacora.py` | Guarda en CSV los eventos y, si se pide, las mediciones de cada cuadro | Probado |

Las ventanas, las teclas y el orden en que se llama a estas funciones están en `somnolencia/principal.py`.

## Ventanas del programa

| Ventana | Contenido | Cuándo aparece |
|---|---|---|
| "Somnolencia y distraccion" | Video con la caja del rostro y la alerta, y el tablero a la derecha | Siempre que no se use `--sin-ventana` |
| "Controles" | Cuatro deslizadores y una leyenda que los explica | Igual |
| "Depuracion" | Rostro normalizado con las franjas de ojos y boca | Al pulsar `d` |

Los nombres de las ventanas y los textos van sin acentos, porque las letras de OpenCV no los tienen.

---

## `overlay.py`

| Función | Recibe | Entrega |
|---|---|---|
| `dibujar(gris, resumen, fps=None)` | Cuadro en grises, el `resumen` del sistema y los cuadros por segundo | Imagen a color de 940×360: video de 640 px y tablero de 300 px |
| `vista_de_depuracion(resumen)` | El `resumen` | Imagen de 256×320, o `None` si el rostro no estaba de frente |

Las claves de `resumen` están documentadas en `somnolencia/README.md`.

### Qué muestra `dibujar`

Sobre el video:

- La caja del rostro, verde si está de frente y roja si no.
- Durante la calibración, una franja gris con la instrucción.
- Durante la vigilancia, si hay alerta, una franja de color con el nivel y el motivo. Amarillo para aviso, naranja para alerta y rojo para crítica.

En el tablero:

- Tres barras (Ojos, Boca, Cabeza) con el valor de 0 a 1, dos marcas amarillas en sus umbrales y el estado en texto.
- PERCLOS con su nivel, o "calentando".
- Contadores de parpadeos por categoría, bostezos y distracciones por banda.
- Lo que está en curso: cuánto llevan los ojos cerrados, la boca abierta o la persona sin mirar al frente.
- El tiempo, los cuadros por segundo y el aviso de calibración, si lo hay.

### Qué muestra `vista_de_depuracion`

El rostro normalizado al doble de tamaño, con:

- Dos rectángulos verdes: los recortes de los ojos.
- Una línea punteada verde: hasta dónde se descarta la parte de la ceja.
- Un rectángulo amarillo: la franja de la boca.
- La razón de bordes de los ojos, en texto.

Sirve para comprobar que los ojos y la boca caen donde el sistema los busca. Es la herramienta principal para ajustar `OJOS_FILA_INICIAL`, `OJOS_FILA_FINAL` y las filas de la boca.

### Qué falta en la vista de depuración (tarea T12)

- Los niveles de la pirámide.
- La banda laplaciana con la ventana de búsqueda marcada.
- Cada recorte de ojo con su banda más oscura marcada.
- La gráfica de las tres mediciones en los últimos 10 segundos, con sus umbrales.

Para agregarlos, `Sistema.procesar` debe poner esos datos en `resumen` y esta función dibujarlos.

---

## `controles.py`

| Función | Recibe | Hace |
|---|---|---|
| `imagen_de_leyenda()` | Nada | Entrega la imagen con la explicación de cada deslizador y de las teclas |
| `crear_deslizadores()` | Nada | Abre la ventana "Controles" con los deslizadores en su valor actual y la leyenda |
| `aplicar_deslizadores(capa)` | La capa temporal del sistema | Lee los deslizadores y pasa sus valores a `config` y a la capa |

Deslizadores:

| Nombre en pantalla | Parámetro | Efecto |
|---|---|---|
| Ojo cierra | `OJOS_UMBRAL_CIERRE` | Los ojos cuentan como cerrados si su barra baja de este valor |
| Ojo abre | `OJOS_UMBRAL_REAPERTURA` | Vuelven a contar como abiertos si su barra sube de este valor |
| Boca abre | `BOCA_UMBRAL_APERTURA` | La boca cuenta como abierta si su barra sube de este valor |
| Cabeza | `CABEZA_UMBRAL_DISTRAIDO` | Cuenta como distraído si la barra de cabeza baja de este valor |

Cada deslizador va de 0 a 100 y equivale a un umbral de 0.00 a 1.00. Los cambios duran lo que dura la sesión y no se escriben en `config.py`.

Los umbrales de duración del enunciado (0.5 s, 7 s, PERCLOS) no tienen deslizador. Son parte de la especificación.

### Detalles que hay que respetar

- **Nombres de 10 letras o menos.** En Windows, OpenCV recorta los nombres más largos y los muestra con puntos suspensivos. La explicación completa va en la leyenda. Una prueba lo revisa.
- **Ventana aparte.** Si los deslizadores se ponen en la ventana del video, lo empujan hacia abajo.
- **Para agregar un deslizador** se agrega una fila a la lista `DESLIZADORES` con: nombre corto, nombre del parámetro en `config`, señal (`ojos`, `boca` o `cabeza`), atributo del actualizador (`umbral_entrada` o `umbral_salida`) y la explicación para la leyenda.

---

## `bitacora.py`

| Elemento | Recibe | Hace |
|---|---|---|
| `Bitacora(carpeta="salidas", fuente="")` | Carpeta de salida y nombre de la fuente | Crea `bitacora_FECHA_HORA.csv` y `parametros_FECHA_HORA.txt` |
| `Bitacora.guardar(eventos)` | Lista de `Evento` | Escribe una fila por evento |
| `Bitacora.cerrar()` | Nada | Cierra el archivo |
| `BitacoraDeMediciones(carpeta="salidas", marca=None)` | Carpeta y la misma marca de fecha de la bitácora | Crea `mediciones_FECHA_HORA.csv` |
| `BitacoraDeMediciones.guardar(resumen)` | El `resumen` de un cuadro | Escribe una fila |
| `BitacoraDeMediciones.cerrar()` | Nada | Cierra el archivo |

Columnas del CSV: `tipo`, `inicio_s`, `fin_s`, `duracion_s`, `categoria`. Son las mismas de los archivos de anotaciones, para poder compararlos.

Ejemplo de una bitácora:

```
tipo,inicio_s,fin_s,duracion_s,categoria
parpadeo,8.000,8.333,0.333,normal
parpadeo,11.000,14.000,3.000,lento
distraccion,18.000,20.533,2.533,2.0
bostezo,24.000,27.000,3.000,bostezo
parpadeo,31.000,39.533,8.533,microsueno
```

El archivo de parámetros guarda la fuente y todos los valores de `config.py` vigentes al empezar. Así se sabe con qué valores se obtuvo cada resultado.

La bitácora no guarda imágenes ni video. La carpeta `salidas/` no se sube al repositorio.

### Mediciones cuadro por cuadro

Con la opción `--mediciones` de `principal.py` se guarda un segundo CSV con una fila por cuadro. Sirve para ajustar umbrales y para las gráficas del reporte.

Columnas: `t`, `fase`, `valor_ojos`, `valor_boca`, `valor_cabeza`, `razon_ojos`, `puntaje`, `estado_ojos`, `estado_boca`, `estado_cabeza`, `perclos`, `nivel_perclos`, `alerta`. Lo que no hay en un cuadro queda vacío: por ejemplo, `valor_ojos` cuando el rostro no está de frente, o los estados durante la calibración.

Dos filas de ejemplo, una normal y otra durante un giro de cabeza:

```
t,fase,valor_ojos,valor_boca,valor_cabeza,razon_ojos,puntaje,estado_ojos,estado_boca,estado_cabeza,perclos,nivel_perclos,alerta
6.5333,vigilando,0.9848,0.0000,0.7443,1.6448,0.7443,ABIERTO,CERRADA,ATENTO,,calentando,ninguna
19.2000,vigilando,,,0.1611,,0.1611,SIN_DATO,SIN_DATO,DISTRAIDO,0.2320,fatiga,alerta
```

Para graficar una medición en el tiempo basta abrir el archivo en una hoja de cálculo o leerlo con `csv`.

**Falta.** Si se mueven los deslizadores durante la sesión, el archivo de parámetros no lo registra.
