# `pruebas/`

Aquí van las pruebas automáticas. Una prueba es un programa pequeño que llama a una función con una entrada cuya salida correcta se conoce, y avisa si la salida es otra. Sirven para saber en segundos si un cambio rompió algo que ya funcionaba.

Se corren todas con:

```bash
pytest
```

Se corren antes de abrir cada pull request.

## Qué debe ir aquí

### `test_eventos.py` (frente 4)

**Aquí deben ir las pruebas que** comprueban la clasificación de eventos con señales inventadas. Cada renglón es una prueba.

Las entradas son listas de pares (tiempo, estado) escritas a mano. "Ojos cerrados de 10.0 a 10.5 s" quiere decir que el primer cuadro cerrado tiene `t = 10.0` y el primer cuadro abierto tiene `t = 10.5`. Así se prueba la regla de clasificación sin que el muestreo de la cámara mueva los límites.

| Entrada | Resultado esperado |
|---|---|
| Ojos cerrados de 10.0 a 10.3 s | Un parpadeo normal |
| Ojos cerrados de 10.0 a 10.5 s | Un parpadeo normal (el límite de 0.5 s es normal) |
| Ojos cerrados de 10.0 a 10.6 s | Un parpadeo lento |
| Ojos cerrados de 10.0 a 17.0 s | Un parpadeo lento (el límite de 7 s es lento) |
| Ojos cerrados de 10.0 a 17.1 s | Un microsueño |
| Cierre de 10.0 a 18.0 s con un solo cuadro abierto a los 14.0 s | Un microsueño, no dos parpadeos lentos |
| Cierre de 10.0 a 12.0 s con sin dato de 10.5 a 10.7 s | Un parpadeo lento de 2.0 s |
| Cierre que empieza en 10.0 s y sin dato de 10.5 a 12.0 s | Ningún parpadeo contado. Un evento indeterminado |
| Boca abierta de 20.0 a 20.8 s | Ningún bostezo |
| Boca abierta de 20.0 a 23.0 s | Un bostezo |
| Cabeza distraída de 30.0 a 30.4 s | Ningún episodio |
| Cabeza distraída de 30.0 a 30.5 s | Un episodio en la banda 0.5 |
| Cabeza distraída de 30.0 a 31.2 s | Un episodio en la banda 1.0 |
| Cabeza distraída de 30.0 a 33.0 s | Un episodio en la banda 2.0 |
| Un cierre de 3 s muestreado a 10 y a 25 cuadros por segundo | Parpadeo lento en los dos casos, con duraciones que difieren en menos de un cuadro |

La última prueba comprueba que el resultado depende del tiempo y no del número de cuadros.

### `test_estados.py` (frente 4)

| Entrada | Resultado esperado |
|---|---|
| Aperturas 0.80, 0.22, 0.18, 0.27, 0.23, 0.28, 0.40 | ABIERTO, ABIERTO, CERRADO, CERRADO, CERRADO, CERRADO, ABIERTO |
| Medición con `valido = False` | `SIN_DATO` |

En esta prueba el antirrebote se pone en cero, para probar solo el umbral doble.

### `test_perclos.py` (frente 4)

| Entrada | Resultado esperado |
|---|---|
| 30 s con ojos abiertos | 0%, nivel normal |
| El ejemplo de `temporal/README.md` (cierres de 2.0 y 1.5 s, 2 s sin dato) | 12.5%, nivel de alerta |
| 30 s con diez parpadeos de 0.3 s, con el interruptor en `False` | 0% |
| Lo mismo con el interruptor en `True` | 10% |
| Cierre de 5 s que empezó 3 s antes del inicio de la ventana | Cuentan solo 2 s |
| Solo 5 s de datos | "calentando" |
| Exactamente 8.0% | Nivel de alerta |

### `test_alertas.py` (frente 4)

| Entrada | Resultado esperado |
|---|---|
| Cierre en curso de 1.4 s | Sin alerta por cierre |
| Cierre en curso de 1.5 s | Alerta |
| Cierre en curso de 7.1 s | Crítica |
| Distracción en curso de 2.0 s | Alerta |

### `test_percepcion.py` (frentes 1, 2 y 3)

**Aquí deben ir las pruebas que** comprueban cada algoritmo con una entrada sintética sencilla. Son una versión corta de los cuadernos de `verificacion/`.

| Función | Entrada | Resultado esperado |
|---|---|---|
| `suavizar_binomial` | Imagen constante | La misma imagen, fuera de la orilla |
| `gradiente_vertical` | Rampa vertical | Valor constante, fuera de la orilla |
| `separacion_de_picos` | Dos líneas horizontales a 10 px | 10 |
| `correlacion_normalizada` | Plantilla recortada de la propia imagen | Máximo de 1.0 en la posición del recorte |
| `correlacion_de_fase` | Imagen desplazada 5 px a la derecha y 3 hacia abajo | (5, 3), con el signo acordado |
| `normalizar_rostro` | Caja del mismo tamaño que la salida | La misma imagen |
| `especificar_histograma` | Imagen contra su propio histograma | La misma imagen |

### `test_reglas.py` (frente 4)

**Aquí deben ir las pruebas que** vigilan las reglas del repositorio leyendo el texto de los archivos de `somnolencia/`.

- Ningún archivo importa `mediapipe`, `dlib`, `torch`, `tensorflow` ni `keras`, ni usa `cv2.dnn` o `cv2.CascadeClassifier`.
- Ningún archivo de `percepcion/` usa las funciones de OpenCV equivalentes a los algoritmos propios (la lista está en `somnolencia/README.md`).
- Ningún archivo de `temporal/` importa `cv2`.

Si alguien pregunta en la defensa cómo se garantiza que el sistema no depende de una red, esta prueba es la respuesta.

## Hecho cuando

`pytest` termina sin fallas en la computadora de cada integrante y en el equipo de la demo.
