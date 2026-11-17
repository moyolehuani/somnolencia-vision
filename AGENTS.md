# Guía para asistentes de IA y para quien llega al proyecto

Este archivo resume lo que hay que saber antes de cambiar algo en el repositorio. Está pensado para que lo lea un asistente de IA al inicio de una sesión, y sirve igual para una persona.

Si usas un asistente, pídele que lea este archivo completo antes de proponer cambios.

## 1. Qué es este proyecto

Proyecto final de Visión Computacional (PCIC-UNAM, semestre 2027-1). Es un sistema que analiza el video de una persona frente a una cámara y reporta parpadeos (normal, lento, microsueño), bostezos, episodios de distracción y la métrica PERCLOS, con alertas en pantalla.

Lo construye un equipo de cuatro estudiantes. Se califica sobre todo por la implementación propia de algoritmos clásicos vistos en clase y por la capacidad de cada integrante de explicarlos en una defensa oral.

## 2. Reglas que no se rompen

Las reglas 1 a 4 las vigila una prueba automática (`pruebas/test_reglas.py`). Si un cambio las rompe, `pytest` falla.

1. **Sin redes neuronales ni modelos entrenados.** Nada de `mediapipe`, `dlib`, `torch`, `tensorflow`, `keras`, `cv2.dnn` ni `cv2.CascadeClassifier`, en ninguna parte del paquete `somnolencia/`. El enunciado califica con 5 un sistema basado en una red.
2. **Los algoritmos de visión se escriben a mano con NumPy.** Dentro de `somnolencia/percepcion/` no se usan `cv2.GaussianBlur`, `cv2.Sobel`, `cv2.equalizeHist`, `cv2.pyrDown`, `cv2.matchTemplate`, `cv2.phaseCorrelate`, `cv2.warpAffine` ni `cv2.resize`. Esas funciones solo aparecen en `verificacion/` y en `pruebas/`, como referencia para comprobar la versión propia.
3. **La capa temporal no ve imágenes.** Ningún archivo de `somnolencia/temporal/` importa `cv2`.
4. **OpenCV se usa solo para lo que el enunciado permite:** leer cámara o video (`cv2.VideoCapture`), pasar a grises (`cv2.cvtColor`), ventanas, dibujo y deslizadores. `numpy.fft` se usa como operación matemática básica.
5. **Ningún número suelto en el código.** Todo umbral, tamaño o proporción vive en `somnolencia/config.py` con un comentario que dice de dónde sale.
6. **Los umbrales del enunciado no se tocan:** 0.5 s y 7 s para parpadeos, bandas de distracción 0.5, 1.0, 1.5 y 2.0 s, ventana de PERCLOS de 30 s y sus niveles 8%, 15% y 30%.
7. **Nada con rostros entra al repositorio:** ni videos, ni fotos, ni cuadernos de Jupyter con imágenes en sus salidas. Los videos viven en una carpeta privada de Google Drive.
8. **Los umbrales se ajustan con los videos de ajuste y nunca con los de evaluación.** La división está en `datos/manifiesto.csv`.
9. **Solo dos dependencias para el sistema:** `numpy` y `opencv-python`. No se agregan bibliotecas sin acordarlo con el equipo.
10. **Todo en español:** nombres de archivos, funciones, variables, comentarios y documentos.

## 3. Criterio del equipo sobre el código

- Se prefiere una solución sencilla y hecha a mano, aunque sea más lenta o más larga, a una avanzada que nadie del equipo pueda explicar. Si una técnica no se vio en las prácticas del curso, hay que decirlo antes de usarla.
- Cada integrante debe poder explicar cada línea de los archivos de su frente sin leer el código. Si algo no se entiende, se simplifica.
- No se reescribe lo que ya funciona. Los cambios son pequeños y con una prueba que los respalde.
- Los comentarios explican el porqué de cada paso, en frases completas.

Las técnicas vistas en las prácticas del curso son: transformación geométrica con mapeo inverso y homografía (P3), especificación de histograma (P4), filtros espaciales, binomial y gradientes (P5), pirámides y Fourier (P6), SIFT con RANSAC (P7).

## 4. Cómo correr las cosas

Desde la raíz del repositorio:

```bash
pip install -r requirements.txt        # lo que necesita el sistema
pip install -r requirements-dev.txt    # pruebas y gráficas

python revisar.py                                    # las cuatro comprobaciones de abajo, una tras otra
python -m pytest                                     # solo las pruebas (115, unos 12 segundos)
python -m verificacion.verificar                     # solo la comparación contra OpenCV
python -m evaluacion.por_cuadro <carpeta con Open y Closed>   # solo la medida de ojos con Kaggle
python -m evaluacion.demostracion                    # evaluación por evento con la escena dibujada
python -m evaluacion.por_evento anotaciones.csv bitacora.csv [mediciones.csv]

python -m somnolencia.principal --fuente escena      # cara dibujada con guion, sin cámara
python -m somnolencia.principal --fuente 0           # cámara
python -m somnolencia.principal --fuente video.mp4   # archivo de video
python -m somnolencia.principal --fuente video.mp4 --sin-ventana --mediciones --caja 265,111,110,138
```

Antes de dar por terminado un cambio se corre `python revisar.py` y debe terminar con los cuatro pasos en "bien" (el de Kaggle se salta si no está el dataset).

## 5. Mapa del repositorio

| Ruta | Qué hay |
|---|---|
| `somnolencia/config.py` | Todos los parámetros |
| `somnolencia/tipos.py` | `Medicion`, `Evento` y los nombres de los estados |
| `somnolencia/sistema.py` | Clase `Sistema`: procesa un cuadro de principio a fin. Incluye la calibración |
| `somnolencia/principal.py` | Programa principal: argumentos, captura, ventanas, teclas, bitácora |
| `somnolencia/percepcion/` | Algoritmos de visión: de un cuadro a tres mediciones |
| `somnolencia/temporal/` | Reglas de tiempo: de mediciones a estados, eventos, PERCLOS y alertas |
| `somnolencia/interfaz/` | Dibujo en pantalla, deslizadores y bitácora |
| `somnolencia/simulador.py` | Mediciones inventadas, para probar la capa temporal |
| `somnolencia/escena_sintetica.py` | Video dibujado, para probar todo sin cámara |
| `verificacion/verificar.py` | Cada algoritmo propio contra OpenCV |
| `evaluacion/por_cuadro.py` | Medida de ojos con las imágenes de Kaggle |
| `evaluacion/por_evento.py` | Bitácora del sistema contra anotaciones de un video |
| `evaluacion/demostracion.py` | Ejemplo de la evaluación completa con la escena dibujada |
| `pruebas/` | Pruebas automáticas |
| `revisar.py` | Corre todas las comprobaciones |
| `docs/` | Documentación general |
| `datos/` | Datos locales. Casi nada se sube |

Cada carpeta tiene su `README.md` con el detalle de sus archivos.

## 6. Cómo fluye un cuadro

```
principal.py
  Captura.leer()                      -> (gris 640x360, t)
  Sistema.procesar(gris, t)
      piramide_gaussiana              -> 3 niveles
      SeguidorDeRostro.seguir         -> caja, puntaje, movimiento
      medir_cabeza(puntaje)           -> Medicion
      si el rostro está de frente:
          normalizar_rostro           -> rostro 128x160
          recortes_de_ojos, medir_ojos   -> Medicion
          tabla_de_especificacion, aplicar_tabla, medir_boca -> Medicion
      si no:
          ojos y boca quedan con valido = False
      CapaTemporal.actualizar         -> estados, eventos, PERCLOS, alerta
  overlay.dibujar(gris, resumen)      -> imagen para la ventana
  Bitacora.guardar(eventos nuevos)
```

`Sistema.procesar` entrega un diccionario llamado `resumen`. Sus claves están documentadas en `somnolencia/README.md`. Es el único canal entre el sistema y la interfaz.

## 7. Convenciones

- **Imágenes.** Arreglos de NumPy en grises, `float32`, valores de 0 a 255, forma `(alto, ancho)`.
- **Cajas.** Tuplas `(x, y, ancho, alto)` en pixeles. `x` crece a la derecha y `y` hacia abajo.
- **Tiempo.** Segundos, como `float`. Las duraciones se calculan con marcas de tiempo, nunca contando cuadros.
- **Mediciones.** `Medicion(t, valor, valido)`, con `valor` entre 0 y 1. Ojos: 1 es abierto. Boca: 0 es cerrada. Cabeza: 1 es de frente.
- **Eficiencia.** Se opera con arreglos completos. Los filtros se escriben como sumas de copias desplazadas de la imagen (`filtrar_1d`). El único ciclo por posición está en `correlacion_normalizada`, y por eso se le pasan zonas pequeñas.
- **Textos en pantalla.** Sin acentos, porque las letras de OpenCV no los tienen.
- **Nombres de deslizadores.** A lo más 10 letras, porque Windows recorta los más largos.
- **Documentos.** Frases directas y cortas. No se usan rayas largas. Los ejemplos van con números concretos.

## 8. Qué hacer al cambiar algo

1. Leer el README de la carpeta y el archivo que se va a tocar.
2. Hacer el cambio más pequeño que resuelva el problema.
3. Si el cambio agrega un parámetro, ponerlo en `config.py` con su explicación.
4. Agregar o ajustar una prueba en `pruebas/`.
5. Correr `python revisar.py`.
6. Actualizar el README de la carpeta y `docs/estado_actual.md`.
7. Si se tomó una decisión de diseño, anotarla en `docs/decisiones.md` con su razón.
8. Subirlo en una rama y pedir revisión (`docs/flujo_git.md`).

## 9. Estado y pendientes

- `docs/estado_actual.md` dice qué está escrito y cómo se probó cada archivo.
- `docs/tareas_pendientes.md` lista lo que falta, tarea por tarea, con pasos y criterio de terminado.
- `docs/decisiones.md` explica por qué cada cosa es como es y qué decisiones siguen abiertas.

Lo más importante que hay que saber hoy: el sistema completo corre sobre una cara dibujada, pero todavía no se ha probado con una persona. Varios parámetros de `config.py` son provisionales y se pusieron sin ver una cara real.

## 10. Errores comunes que hay que evitar

- Proponer un detector de rostros o de puntos faciales ya entrenado. Rompe la regla 1.
- "Mejorar" un filtro llamando a la función de OpenCV. Rompe la regla 2.
- Medir duraciones contando cuadros.
- Reportar ojos cerrados cuando el rostro no se ve. En ese caso la medición lleva `valido = False`.
- Aplicar la especificación de histograma al rostro completo. Al abrir la boca cambia el contenido y la corrección la borra. Ver la decisión D33.
- Ajustar un umbral para que pase una prueba. Primero hay que entender por qué falla.
- Dar por bueno algo porque funciona con la escena dibujada. La escena solo comprueba que las piezas están conectadas.
