# Tareas pendientes

Lista de lo que falta, tarea por tarea. Cada una dice quién la hace, por qué importa, los pasos y cuándo se considera terminada.

Antes de empezar una tarea conviene leer `docs/estado_actual.md` y el README de la carpeta que se va a tocar. Quien use un asistente de IA debe pedirle que lea primero `AGENTS.md`.

## Frentes

| Frente | Archivos a su cargo |
|---|---|
| 1. Rostro | `percepcion/captura.py`, `piramide.py`, `correlacion.py` (normalizada), `geometria.py`, `rostro.py`, y la calibración en `sistema.py` |
| 2. Ojos | `percepcion/preproceso.py`, `gradiente.py`, `ojos.py`, `evaluacion/por_cuadro.py` |
| 3. Boca y cabeza | `percepcion/boca.py`, `cabeza.py`, `correlacion.py` (de fase) |
| 4. Temporal y evaluación | `temporal/`, `interfaz/`, `sistema.py`, `principal.py`, `evaluacion/por_evento.py`, `evaluacion/desempeno.py` |

## Resumen

| ID | Tarea | Frente | Prioridad | Depende de |
|---|---|---|---|---|
| T01 | Leer y entender el código del propio frente | Todos | 1 | |
| T02 | Primera prueba con cámara y ajuste de recortes | 1 y 2 | 1 | |
| T03 | Medir el riesgo de ojos cerrados contra distracción (D32) | 1 | 1 | T02 |
| T04 | Grabar, registrar y anotar los videos | Todos | 1 | T02 |
| T05 | Enviar las preguntas a los profesores | Margarita | 1 | |
| T06 | Inventario de los datasets de Kaggle | 2 y 3 | 1 | |
| T07 | Validar la medida de la boca | 3 | 2 | T04, T08 |
| T08 | Guardar las mediciones cuadro por cuadro | 4 | Hecha | |
| T09 | Evaluación por evento | 4 | Programa hecho. Falta correrlo con videos | T04 |
| T10 | Tiempos por etapa | 1 | 2 | |
| T11 | Ajustar umbrales y congelarlos | Todos | 2 | T04, T08 |
| T12 | Vista de depuración completa | 4 | 3 | |
| T13 | Arranque con videos sin calibración (D29) | 1 | 2 | T05 |
| T14 | Decidir PERCLOS al inicio (D30) y bostezo mínimo (D11) | 4 | 2 | T05 |
| T15 | Figuras de verificación para el reporte | Todos | 3 | |
| T16 | Reporte, video y ensayo de la demo | Todos | 3 | T09, T11 |
| T17 | Mejoras opcionales | Quien pueda | 4 | |

Prioridad 1 es para esta semana. Las tareas de prioridad 4 solo se hacen si sobra tiempo.

---

## T01. Leer y entender el código del propio frente

**Quién.** Todos.

**Por qué.** El código actual se escribió en un día con ayuda de un asistente de IA. Nadie del equipo lo ha revisado. La defensa vale 20% y pide explicar los algoritmos propios.

**Pasos.**

1. Leer el README de la carpeta del frente.
2. Leer cada archivo del frente de arriba abajo, con sus comentarios.
3. Correr `python revisar.py` y `python -m somnolencia.principal --fuente escena`.
4. Para cada función, poder responder sin ver el código: qué recibe, qué entrega, cómo lo calcula y por qué se eligió así.
5. Anotar lo que no se entienda. Si después de preguntarlo sigue sin entenderse, se reescribe más simple.
6. Explicarle el frente a otro integrante en diez minutos.

**Terminado cuando.** Cada integrante explicó su frente a otro y no quedan dudas anotadas.

---

## T02. Primera prueba con cámara y ajuste de recortes

**Quién.** Frentes 1 y 2, con todos presentes si se puede.

**Por qué.** El sistema solo se ha probado con una cara dibujada. Varios valores de `config.py` se pusieron sin ver una cara real.

**Pasos.**

1. Correr `python -m somnolencia.principal --fuente 0`.
2. Poner la cara dentro del recuadro, de la frente a la barbilla, y pulsar la barra espaciadora.
3. Mirar al frente 3 s y cerrar los ojos 2 s cuando la pantalla lo pida.
4. Abrir la vista de depuración con `d`.
5. Revisar, en este orden:

| Qué mirar | Si falla | Qué ajustar |
|---|---|---|
| La cámara abre | Error al iniciar | Probar `--fuente 1`. Cerrar otros programas que usen la cámara |
| El recuadro tiene el tamaño de la cara | La cara no cabe o sobra mucho | `RECUADRO_ANCHO`, `RECUADRO_ALTO`, o la distancia a la cámara |
| La caja sigue a la cara y se queda verde | Se pone roja sin voltear | Ver T03. Revisar la luz |
| Los ojos caen en los rectángulos verdes, debajo de la línea punteada | Quedan arriba, abajo o cortados | `OJOS_FILA_INICIAL`, `OJOS_FILA_FINAL` |
| La calibración termina sin aviso | Aparece "calibracion de ojos no confiable" | Primero corregir los recortes. Luego repetir |
| La barra de Ojos baja al cerrar y sube al abrir | No se mueve o se mueve al revés | Revisar los recortes. Anotar los valores que toma |
| La boca cae en el rectángulo amarillo | Queda fuera | `BOCA_FILA_INICIAL`, `BOCA_FILA_FINAL` |

6. Anotar en `docs/estado_actual.md` qué funcionó y qué no, con los valores que quedaron.

**Terminado cuando.** Con al menos dos integrantes distintos, la caja sigue la cara, los ojos caen en sus recortes y la barra de Ojos responde al cerrar y abrir.

**Nota.** Si falla la tecla `c` o marcar la caja con el ratón en un video, también se anota. Esas dos partes de `principal.py` no se han probado.

---

## T03. Medir el riesgo de ojos cerrados contra distracción (D32)

**Quién.** Frente 1.

**Por qué.** Los ojos están dentro de la plantilla del rostro. Al cerrarlos, el parecido con la plantilla baja. Si baja del umbral de distracción (0.50), el sistema cree que la persona volteó, deja los ojos sin dato y no detecta el cierre. Con la cara dibujada baja de 0.91 a 0.70.

**Pasos.**

1. Con cámara o con un video del guion G2, mirar la barra de Cabeza durante los cierres de ojos.
2. Anotar su valor con los ojos abiertos y con los ojos cerrados. Se lee de la columna `valor_cabeza` del archivo de mediciones (opción `--mediciones`).
3. Decidir según lo que salga:

| Resultado | Qué hacer |
|---|---|
| Con ojos cerrados se queda arriba de 0.65 | Nada. Anotar el resultado en D32 |
| Baja a entre 0.50 y 0.65 | Bajar `CABEZA_UMBRAL_DISTRAIDO` y `CABEZA_UMBRAL_ATENTO`, y comprobar con el guion G4 que los giros se siguen detectando |
| Baja de 0.50 | Quitar los ojos de la plantilla (ver abajo) |

**Cómo quitar los ojos de la plantilla.** En `correlacion_normalizada` se agrega un parámetro opcional con los renglones a ignorar. Antes de comparar, se quitan esos renglones de la plantilla y de cada trozo con `np.delete(..., axis=0)`. En `rostro.py` se pasan los renglones que corresponden a los ojos (de `OJOS_FILA_INICIAL` a `OJOS_FILA_FINAL` del alto de la caja, llevados a la escala de cada nivel). Hay que agregar una prueba y comprobar que sin ese parámetro la función sigue dando lo mismo que `cv2.matchTemplate`.

**Terminado cuando.** Un cierre de ojos de 8 s frente a la cámara se reporta como microsueño y no como distracción, y D32 tiene anotado el resultado.

---

## T04. Grabar, registrar y anotar los videos

**Quién.** Todos graban. Frente 4 coordina la anotación.

**Por qué.** Sin videos anotados no hay evaluación por evento, que es la que responde a los umbrales del enunciado.

**Pasos.**

1. Cada quien firma el consentimiento de `docs/datos_y_gobernanza.md`.
2. Grabar los guiones G1 a G6 de `docs/evaluacion.md` con las especificaciones de `datos/README.md` (MP4, 1280×720, 30 cuadros por segundo constantes, sin audio).
3. Comprobar cada video con el comando de `datos/README.md`.
4. Subirlos a la carpeta de Google Drive con el nombre `Pnn_Gn_nn.mp4`.
5. Llenar `datos/manifiesto.csv`. Asignar dos personas al grupo de ajuste y dos al de evaluación.
6. Anotar cada video en `datos/anotaciones/` con el formato de `datos/README.md`.

**Terminado cuando.** Hay 20 videos (cuatro personas por cinco guiones) con su fila en el manifiesto y su archivo de anotaciones.

**Nota.** Conviene hacer T02 antes. Si el encuadre o la distancia no sirven para el sistema, es mejor saberlo antes de grabar todo.

---

## T05. Enviar las preguntas a los profesores

**Quién.** Margarita.

**Pasos.** Enviar las preguntas de `docs/guia_de_supervision.md`. Anotar las respuestas en `docs/decisiones.md` y cambiar lo que haga falta en `config.py`.

Las que más afectan al código:

| Pregunta | Parámetro o archivo que cambia |
|---|---|
| ¿PERCLOS cuenta los parpadeos normales? (D09) | `PERCLOS_CUENTA_PARPADEOS_NORMALES` |
| ¿Cómo se leen las bandas de distracción? (D10) | `banda_de_distraccion` en `temporal/eventos.py` |
| ¿Cómo serán los videos de prueba? (D29) | T13 |
| ¿Se acepta calibrar con la persona? | Si no, cambia el diseño del seguimiento |

**Terminado cuando.** Las respuestas están anotadas en `docs/decisiones.md`.

---

## T06. Inventario de los datasets de Kaggle

**Quién.** Frentes 2 y 3.

**Lo que ya se sabe del primero** (`dheerajperumandla/drowsiness-dataset`, carpeta `train`):

| Carpeta | Contenido |
|---|---|
| `Open` | 726 recortes de un ojo abierto |
| `Closed` | 726 recortes de un ojo cerrado |
| `yawn`, `no_yawn` | Escenas completas de 640×480 de personas manejando. No son recortes de boca |

**Pasos.**

1. Anotar la licencia que declara la página de cada dataset.
2. Revisar si hay una carpeta `test` y qué trae.
3. Descargar el segundo dataset desde la liga del PDF del enunciado y describirlo igual.
4. Llenar la tabla de `docs/datos_y_gobernanza.md` y cerrar la decisión D26.

**Terminado cuando.** La tabla de inventario no tiene celdas con "por confirmar".

---

## T07. Validar la medida de la boca

**Quién.** Frente 3.

**Por qué.** La medida de `boca.py` solo se ha probado con una boca dibujada. La medida de ojos original también parecía razonable y no funcionó con imágenes reales.

**Pasos.**

1. Con los videos del guion G3 del grupo de ajuste, correr el sistema con `--mediciones`.
2. Graficar la apertura de boca en el tiempo y marcar los tramos de bostezo, de hablar y de sonreír según las anotaciones.
3. Ver si hay un umbral que separe los bostezos de lo demás.

| Resultado | Qué hacer |
|---|---|
| Los bostezos quedan claramente arriba | Fijar `BOCA_UMBRAL_APERTURA` y `BOCA_UMBRAL_CIERRE`. Anotar en D31 |
| Hablar y bostezar dan valores parecidos pero el bostezo dura más | Apoyarse en `BOSTEZO_MIN_S` |
| La medida no responde a la apertura | Cambiar de medida y repetir |

**Ideas si hay que cambiar de medida**, todas con lo visto en clase: usar el gradiente vertical en la franja de la boca (el labio superior y el inferior se separan), o comparar la franja de la boca con su plantilla en reposo mediante correlación normalizada (al abrirse deja de parecerse).

**Terminado cuando.** En los videos de ajuste del guion G3 se detectan los bostezos y hablar no los dispara, y D31 quedó cerrada con el resultado.

---

## T08. Guardar las mediciones cuadro por cuadro

**Estado.** Hecha el 16 de noviembre.

Con la opción `--mediciones`, `principal.py` guarda `salidas/mediciones_FECHA_HORA.csv` con una fila por cuadro. Las columnas y un ejemplo están en `somnolencia/interfaz/README.md`.

```bash
python -m somnolencia.principal --fuente datos/videos/P01_G2_01.mp4 --mediciones
```

Se usa en T03, T07 y T11 para ver cómo cambian las mediciones en el tiempo.

---

## T09. Evaluación por evento

**Quién.** Frente 4.

**Estado.** El programa `evaluacion/por_evento.py` está escrito y probado con la escena dibujada. Su documentación está en `evaluacion/README.md`. `python -m evaluacion.demostracion` muestra la evaluación completa con archivos de ejemplo.

**Lo que falta.**

1. Agregar la columna `caja` a `datos/manifiesto.csv` y llenarla para cada video (se marca el rostro con el ratón una vez y se anota).
2. Correr cada video del grupo de ajuste sin ventana y compararlo con sus anotaciones, como dice `evaluacion/README.md`.
3. Escribir un programa corto que recorra el manifiesto, corra todos los videos de un grupo y junte los resultados en una tabla.
4. Al final, correr una sola vez los videos del grupo de evaluación y llenar las tablas del nivel 3 de `docs/evaluacion.md`.

**Terminado cuando.** Las tablas del nivel 3 de `docs/evaluacion.md` están llenas con los videos de evaluación.

---

## T10. Tiempos por etapa

**Quién.** Frente 1.

**Por qué.** El criterio de tiempo real vale 10% y el enunciado pide discutir los compromisos entre complejidad, calidad y velocidad. Hoy `principal.py` solo imprime el tiempo total por cuadro.

**Qué hay que hacer.**

1. En `Sistema.procesar`, tomar la hora con `time.perf_counter()` antes y después de cada etapa (pirámide, seguimiento, normalización, ojos, boca, capa temporal) y guardar los tiempos en `resumen["tiempos"]`, un diccionario de etapa a segundos.
2. En `evaluacion/desempeno.py`, correr un video o la escena, juntar los tiempos e imprimir media y máximo por etapa y los cuadros por segundo.
3. Repetir con las variantes de la tabla de `docs/evaluacion.md`: otra resolución de trabajo, otra ventana de búsqueda.
4. Correrlo en la computadora de la demo y llenar las tablas del nivel 4.

**Referencia.** Con la escena, el proceso completo tarda unos 8 ms por cuadro en una computadora y 11 ms en otra. El cuadro más lento es el de búsqueda completa cuando el rostro se pierde, cerca de 100 ms.

**Terminado cuando.** Las tablas del nivel 4 de `docs/evaluacion.md` están llenas con tiempos de la computadora de la demo.

---

## T11. Ajustar umbrales y congelarlos

**Quién.** Cada frente los suyos.

**Regla.** Solo con los videos del grupo de ajuste. Los de evaluación no se miran hasta el final (D17).

| Parámetros | Frente | Con qué guion |
|---|---|---|
| `OJOS_FILA_INICIAL`, `OJOS_FILA_FINAL` | 2 | Cualquiera, con la vista de depuración |
| `OJOS_UMBRAL_CIERRE`, `OJOS_UMBRAL_REAPERTURA` | 2 | G1 y G2 |
| `BOCA_UMBRAL_APERTURA`, `BOCA_UMBRAL_CIERRE`, `BOSTEZO_MIN_S` | 3 | G3 |
| `CABEZA_UMBRAL_DISTRAIDO`, `CABEZA_UMBRAL_ATENTO` | 3 | G4 |
| `PLANTILLA_FRACCION_ALTO`, `BUSQUEDA_VENTANA_PX` | 1 | G4 y G5 |
| `ANTIRREBOTE_CUADROS`, `SIN_DATO_TOLERANCIA_S` | 4 | G5 |

**Pasos.**

1. Correr los videos de ajuste con `--mediciones`.
2. Probar valores con los deslizadores para ver el efecto.
3. Elegir el valor, escribirlo en `config.py` con un comentario que diga cómo se eligió.
4. Correr `python revisar.py`. Si una prueba falla por el cambio, entender por qué antes de tocarla.
5. Cuando todos terminen, guardar una copia de `config.py` y no cambiarlo más.

**Terminado cuando.** Ningún parámetro de `config.py` dice "provisional" o "por ajustar" sin una nota de cómo se fijó.

---

## T12. Vista de depuración completa

**Quién.** Frente 4.

**Por qué.** Es la herramienta de la defensa: con ella cualquier resultado se explica señalando la imagen que lo produjo.

**Qué falta mostrar.**

| Elemento | Qué debe agregar `Sistema.procesar` a `resumen` |
|---|---|
| Niveles de la pirámide | La lista de niveles |
| Banda laplaciana con la ventana de búsqueda | La banda del nivel pequeño y el centro de búsqueda |
| Cada ojo con su banda más oscura | Los dos recortes y el renglón que entrega `banda_mas_oscura` |
| Gráfica de las mediciones de los últimos 10 s | Nada: la interfaz guarda los últimos valores |

Todo se dibuja en `interfaz/overlay.py`, con las funciones de dibujo de OpenCV.

**Terminado cuando.** Con la tecla `d` se ven esos cuatro elementos y `pruebas/test_sistema.py` comprueba que la función dibuja sin fallar.

---

## T13. Arranque con videos sin calibración (D29)

**Quién.** Frente 1.

**Por qué.** Los videos de prueba de los profesores no traerán la secuencia de calibración.

**Lo que ya existe.** `--sin-calibracion` empieza a vigilar desde el primer cuadro con las referencias generales de ojos (0.72 y 0.41). Con ventana, el rostro se marca con el ratón. Sin ventana, se da con `--caja`.

**Pasos.**

1. Probar ese modo con un video propio y comparar los eventos contra los que salen con calibración.
2. Si los ojos fallan sin calibración, probar una calibración automática: tomar como referencia de "abierto" la mediana de la razón de ojos en los primeros segundos del video.
3. Ajustar según lo que respondan los profesores sobre cómo serán los videos de prueba.

**Terminado cuando.** Hay un procedimiento escrito y probado para correr un video que no trae calibración.

---

## T14. Decidir PERCLOS al inicio (D30) y bostezo mínimo (D11)

**Quién.** Frente 4.

- **D30.** En los primeros 30 s PERCLOS se calcula sobre el tiempo transcurrido y es nervioso: a los 11 s de sesión, un cierre de 1 s ya da 9%. La alternativa es no reportarlo hasta tener 30 s, cambiando `PERCLOS_TIEMPO_MINIMO_S` a 30. Hay que verlo en vivo y decidir.
- **D11.** `BOSTEZO_MIN_S` vale 1.5 s sin una fuente. Hay que buscar un artículo que respalde un valor y citarlo en `config.py`.

**Terminado cuando.** Las dos decisiones están cerradas en `docs/decisiones.md`.

---

## T15. Figuras de verificación para el reporte

**Quién.** Cada frente las de sus algoritmos.

Para cada algoritmo propio, una figura con la entrada, el resultado propio, el de OpenCV y la diferencia. Se puede hacer en un cuaderno de Jupyter que llame a las funciones del paquete. Las imágenes de prueba no deben ser rostros. Los cuadernos se suben sin salidas.

Los números ya están en `docs/evaluacion.md`, nivel 1, y se reproducen con `python -m verificacion.verificar`.

**Terminado cuando.** Hay siete figuras en `reporte/figuras/`.

---

## T16. Reporte, video y ensayo de la demo

**Quién.** Todos. La estructura del reporte y el guion del video están en `reporte/README.md`. La lista del ensayo está en `docs/despliegue_y_demo.md`.

Tres cosas que el reporte debe decir de forma explícita:

- Qué funciones de biblioteca se usaron y por qué.
- Que la primera medida de ojos se descartó al probarla, y con qué datos.
- Con cuántas personas y en qué condiciones se probó.

**Terminado cuando.** Se cumplen las casillas de la fase 4 de `docs/plan_de_trabajo.md`.

---

## T17. Mejoras opcionales

Solo si sobra tiempo. Ninguna es necesaria para entregar.

- **Varios tamaños de plantilla.** Buscar el rostro con la plantilla a tres escalas para tolerar que la persona se acerque o se aleje.
- **Reencontrar el rostro más rápido.** La búsqueda completa tarda cerca de 100 ms. Se puede buscar una posición de cada dos.
- **Distinguir un giro de una falla de luz.** Usar el movimiento que entrega el seguidor: en un giro hay movimiento justo antes de que caiga el puntaje.
- **Medir los ojos por separado.** Hoy se promedian.
- **SIFT con RANSAC** para confirmar el giro de la cabeza (práctica 7).
