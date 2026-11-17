# Estado actual

Fecha: 16 de noviembre de 2026. Pruebas automáticas: 115.

Este documento dice qué está escrito, cómo se probó cada cosa y qué falta. Es el primero que hay que leer antes de tocar el código, porque varios README de carpeta se escribieron antes que el código, como plan.

## En una frase

Todo el sistema está escrito y corre de punta a punta sobre una cara dibujada. Todavía no se ha probado con una cámara ni con el video de una persona, y es ahí donde se sabrá qué tan bien funciona.

## Qué significa cada nivel de prueba

| Nivel | Qué comprueba | Qué no comprueba |
|---|---|---|
| Verificado contra OpenCV | El algoritmo propio da lo mismo que la función de biblioteca | Que el algoritmo sirva para el problema |
| Probado con Kaggle | La medida distingue ojos abiertos de cerrados en fotos reales | Que funcione con calibración y en video |
| Probado con señales inventadas | Las reglas de tiempo del enunciado están bien programadas | Nada sobre imágenes |
| Probado con la escena dibujada | Las piezas están bien conectadas, del cuadro a la bitácora | Que funcione con una persona |
| Sin probar | El código está escrito con cuidado, pero nadie lo ha visto correr | Todo |

## Archivo por archivo

| Archivo | Qué hace | Nivel de prueba |
|---|---|---|
| `config.py`, `tipos.py` | Parámetros y estructuras | Usados por todas las pruebas |
| `temporal/` (5 archivos) | Estados, eventos, PERCLOS, alertas | Señales inventadas, 57 pruebas |
| `percepcion/preproceso.py` | Suavizado, histograma | Verificado contra OpenCV |
| `percepcion/gradiente.py` | Gradientes, razón de bordes | Verificado contra OpenCV |
| `percepcion/piramide.py` | Pirámide, banda laplaciana | Verificado contra OpenCV |
| `percepcion/correlacion.py` | Correlación normalizada y de fase | Verificado contra OpenCV |
| `percepcion/geometria.py` | Mapeo inverso, recortes de ojos | Verificado contra OpenCV. Las filas de los recortes son provisionales |
| `percepcion/ojos.py` | Apertura de ojos | Kaggle: F1 de 0.84 a 0.86 sin calibración |
| `percepcion/rostro.py` | Seguimiento del rostro | Escena dibujada |
| `percepcion/cabeza.py` | Frontalidad | Escena dibujada |
| `percepcion/boca.py` | Apertura de boca | Escena dibujada. Sin validar con bocas reales |
| `percepcion/captura.py` | Lectura de cámara, video o escena | Escena y archivo de video. Sin probar con cámara |
| `sistema.py` | Une todo, incluida la calibración | Escena dibujada |
| `interfaz/overlay.py` | Dibujo del video y el tablero | Se revisaron imágenes generadas |
| `interfaz/bitacora.py` | Eventos a CSV y mediciones por cuadro | Escena dibujada |
| `interfaz/controles.py` | Deslizadores en su propia ventana, con leyenda | Probado en Windows con la escena |
| `principal.py` | Programa principal | Probado sin ventana, y con ventana y teclas `d`, `r`, `q` usando la escena. Sin probar: la cámara, la tecla `c` y marcar la caja con el ratón |
| `evaluacion/por_cuadro.py` | Evaluación de ojos con Kaggle | Corrido con el dataset completo |
| `evaluacion/por_evento.py` | Bitácora contra anotaciones | Escena dibujada. Sin correr con videos reales |
| `evaluacion/demostracion.py` | Ejemplo de la evaluación completa | Corrido |
| `verificacion/verificar.py` | Comparación contra OpenCV | Corrido en dos computadoras |

## Qué falta

La lista completa, tarea por tarea, con pasos y criterio de terminado, está en [tareas_pendientes.md](tareas_pendientes.md). Lo que todavía no existe como código:

- `evaluacion/desempeno.py`: tiempos por etapa. Por ahora `principal.py` solo imprime el tiempo total por cuadro.
- Vista de depuración completa: pirámide, banda laplaciana y gráfica de las mediciones en el tiempo.
- Un programa que evalúe todos los videos del manifiesto de una vez.

## Cambios respecto al plan original

Los README de carpeta ya describen el código como está. Para quien leyó el plan anterior, esto es lo que cambió:

- No hay `percepcion/calibracion.py`. La calibración está en `sistema.py`.
- La medida de ojos es la razón de bordes y no la separación de picos (decisión D28).
- Los recortes de ojos salen de posiciones fijas en el rostro normalizado. La calibración no los busca.
- La correlación de fase se usa para predecir hacia dónde se movió el rostro antes de buscarlo.
- El histograma se corrige con una tabla armada en la parte de arriba del rostro (decisión D33).
- `principal.py` acepta `--fuente escena` y no `--fuente simulador`.
- Los deslizadores están en una ventana aparte, "Controles".

## Primera prueba con una persona

Es el siguiente paso y el más importante. Con un video del guion G2 (calibración, cierres de 1, 3 y 8 s):

```bash
python -m somnolencia.principal --fuente datos/videos/P01_G2_01.mp4
```

Se marca el rostro con el ratón, de la frente a la barbilla, y se pulsa ENTER. Con la tecla `d` se abre la vista de depuración.

Qué mirar, en este orden:

1. **La caja.** ¿Sigue a la cara? ¿Se queda verde mientras la persona mira al frente?
2. **Los recortes de ojos.** En la vista de depuración, ¿los dos ojos caen dentro de los rectángulos verdes y debajo de la línea punteada? Si no, se ajustan `OJOS_FILA_INICIAL` y `OJOS_FILA_FINAL`.
3. **La calibración.** ¿Termina sin el aviso de "calibración no confiable"?
4. **El puntaje de la cabeza al cerrar los ojos.** ¿La barra de Cabeza se mantiene arriba de su umbral durante los cierres? Es el riesgo de la decisión D32.
5. **La barra de Ojos.** ¿Baja con claridad al cerrar y sube al abrir?
6. **Los eventos.** ¿La bitácora trae los seis cierres del guion con sus categorías?

Lo más probable es que la primera vez algo de esto falle. Es normal: los valores provisionales se pusieron sin ver una cara real. La lista dice en qué orden buscar la causa.

## Riesgos abiertos

| Riesgo | Decisión |
|---|---|
| Cerrar los ojos baja el parecido con la plantilla y puede tomarse por distracción | D32 |
| La medida de boca no está validada | D31 |
| Los videos de prueba de los profesores no traen calibración | D29 |
| PERCLOS es nervioso en los primeros 30 s | D30 |
| La medida de ojos queda en 85% sin calibración. Falta saber cuánto mejora con ella | D28 |
| La plantilla no cambia de tamaño: la persona debe quedarse a la misma distancia | D07 |
| Todo el código lo escribió un asistente en un día. Nadie del equipo lo ha revisado todavía | |

El último punto importa para la defensa. Cada integrante debe leer los archivos de su frente y poder explicarlos sin leer el código. Están comentados paso por paso para eso. Si algo no se entiende, conviene reescribirlo más simple antes que defender algo que no se domina.
