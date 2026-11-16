# `temporal/`

De mediciones a eventos, PERCLOS y alertas. Esta carpeta no ve imágenes y no importa `cv2`. Recibe números con su marca de tiempo y aplica las reglas del enunciado.

Responsable: frente 4. Es lo primero que se programa, porque no depende de nada más y se prueba con señales inventadas.

Una regla para toda la carpeta: **las duraciones se calculan con marcas de tiempo, nunca contando cuadros**. La cámara no entrega los cuadros a intervalos exactos.

---

## `estados.py`

**Aquí debe ir el código que** convierte cada medición en un estado estable.

- `ActualizadorDeEstado`: un objeto por señal (ojos, boca, cabeza) que recibe una `Medicion` y entrega el estado actual.

Dos mecanismos:

**Umbral doble.** Para pasar a `CERRADO` la apertura debe bajar de `OJOS_UMBRAL_CIERRE` (0.20). Para regresar a `ABIERTO` debe subir de `OJOS_UMBRAL_REAPERTURA` (0.35). Entre los dos valores el estado no cambia. Ejemplo con una apertura que oscila cerca del límite:

| Apertura | 0.80 | 0.22 | 0.18 | 0.27 | 0.23 | 0.28 | 0.40 |
|---|---|---|---|---|---|---|---|
| Con umbral doble | ABIERTO | ABIERTO | CERRADO | CERRADO | CERRADO | CERRADO | ABIERTO |
| Con un solo umbral en 0.25 | ABIERTO | CERRADO | CERRADO | ABIERTO | CERRADO | ABIERTO | ABIERTO |

Con umbral doble sale un solo parpadeo. Con un solo umbral salen dos, y el segundo es falso.

**Antirrebote.** Funciona distinto al entrar y al salir de un cierre:

- Entrar a `CERRADO` se acepta de inmediato. A 15 cuadros por segundo un parpadeo de 0.2 s dura solo 3 cuadros, y si se exigiera esperar se perderían los parpadeos cortos.
- Salir de `CERRADO` solo se acepta si la apertura se sostiene más de `ANTIRREBOTE_CUADROS` cuadros. Si en medio de un cierre aparecen uno o dos cuadros abiertos, se ignoran y el cierre continúa.
- Cuando la salida sí se acepta, el fin del cierre es la marca de tiempo del primer cuadro abierto, no la del cuadro en que se confirmó.

Lo mismo aplica a la boca abierta y a la cabeza distraída.

Si la medición llega con `valido = False`, el estado es `SIN_DATO`.

---

## `eventos.py`

**Aquí debe ir el código que** abre, cierra y clasifica los eventos.

- `RastreadorDeEventos`: recibe los tres estados y el tiempo en cada cuadro. Entrega la lista de eventos que se cerraron en ese cuadro y permite consultar los eventos en curso y cuánto llevan.

### Parpadeos

Un parpadeo empieza en la marca de tiempo del primer cuadro `CERRADO` y termina en la del primer cuadro `ABIERTO` que le sigue. Al cerrarse se clasifica con la Tabla 1 del enunciado:

| Categoría | Duración |
|---|---|
| Normal | t ≤ 0.5 s |
| Lento | 0.5 s < t ≤ 7 s |
| Microsueño | t > 7 s |

Los límites son exactos: 0.5 s es normal y 7.0 s es lento. Antes de clasificar, la duración se redondea a milésimas, para que una resta como 13.5 − 13.0 no dé 0.49999 por la aritmética de punto flotante.

### Bostezos

Un bostezo es la boca en estado `ABIERTA` durante `BOSTEZO_MIN_S` o más. Se cuenta uno al cerrarse la boca. Aperturas más cortas se descartan.

### Distracción

Un episodio de distracción es la cabeza en estado `DISTRAIDO`. Al terminar se asigna a su banda (interpretación de D10):

| Banda | Duración |
|---|---|
| No se cuenta | menos de 0.5 s |
| 0.5 | de 0.5 a menos de 1.0 s |
| 1.0 | de 1.0 a menos de 1.5 s |
| 1.5 | de 1.5 a menos de 2.0 s |
| 2.0 | 2.0 s o más |

### Sin dato

Si llega `SIN_DATO` mientras hay un parpadeo o un bostezo en curso:

- Si dura menos de `SIN_DATO_TOLERANCIA_S`, el evento sigue como si nada.
- Si dura más, el evento se cierra como "indeterminado" y no entra a ningún contador. No se puede saber qué pasó con los ojos mientras no se veían.

### Contadores

El rastreador lleva la cuenta de parpadeos por categoría, bostezos y episodios de distracción por banda. La interfaz los muestra.

---

## `perclos.py`

**Aquí debe ir el código que** calcula el porcentaje de tiempo con los ojos cerrados en los últimos 30 segundos.

- `Perclos`: recibe el estado de los ojos y el tiempo en cada cuadro. Entrega el porcentaje y el nivel.

```
PERCLOS = tiempo cerrado que cuenta, dentro de la ventana
          ------------------------------------------------
          tiempo con dato válido, dentro de la ventana
```

Qué cuenta como tiempo cerrado depende de `PERCLOS_CUENTA_PARPADEOS_NORMALES` (decisión D09). Con el valor `False`, un cierre solo cuenta si dura más de 0.5 s, y entonces cuenta completo desde su inicio.

Ejemplo. La ventana va de 40 a 70 s. En ese tramo hubo:

- Un parpadeo de 45.0 a 45.3 s. Dura 0.3 s, es normal, no cuenta.
- Un cierre de 50.0 a 52.0 s. Cuenta 2.0 s.
- Un cierre de 60.0 a 61.5 s. Cuenta 1.5 s.
- Un tramo sin dato de 65 a 67 s. Se quita del denominador.

Tiempo cerrado: 3.5 s. Tiempo válido: 30 − 2 = 28 s. PERCLOS = 3.5 / 28 = 12.5%.

Niveles:

| Nivel | PERCLOS |
|---|---|
| Normal | menos de 8% |
| Alerta | de 8% a menos de 15% |
| Fatiga | de 15% a menos de 30% |
| Somnolencia | 30% o más |

Con 12.5%, el ejemplo está en nivel de alerta.

Casos que hay que cuidar:

- **Los primeros segundos.** Antes de `PERCLOS_TIEMPO_MINIMO_S` de datos válidos, se entrega "calentando" en lugar de un porcentaje. Con dos segundos de datos, un solo cierre daría 50%.
- **Un cierre que cruza el borde de la ventana.** Solo cuenta la parte que queda dentro.
- **Un cierre en curso.** Cuenta desde que supera 0.5 s, aunque todavía no termine.
- **Ventana casi sin datos válidos.** Si el tiempo válido es menor al mínimo, se entrega "sin dato".

---

## `alertas.py`

**Aquí debe ir el código que** decide qué alerta mostrar en cada cuadro, a partir de los eventos en curso y de PERCLOS.

- `nivel_de_alerta(rastreador, perclos)`: entrega el nivel y el motivo.

Propuesta de reglas. Se aplica la más grave que se cumpla:

| Nivel | Condición |
|---|---|
| Crítica | Cierre en curso de más de 7 s, o PERCLOS en somnolencia |
| Alerta | Cierre en curso de 1.5 s o más, o PERCLOS en fatiga, o distracción en curso de 2.0 s o más |
| Aviso | PERCLOS en alerta, o distracción en curso de 1.0 s o más |
| Ninguna | Nada de lo anterior |

El enunciado indica que la notificación al conductor ocurre en la banda intermedia de cierre, donde están los umbrales de alerta de la literatura. Por eso la alerta se dispara mientras el cierre sigue en curso y no al clasificarlo (decisión D12).

---

## Hecho cuando

- Pasan todas las pruebas de `pruebas/README.md`.
- Con `--fuente simulador` la interfaz muestra los eventos y niveles que el guion del simulador debe producir.
- Cambiar `PERCLOS_CUENTA_PARPADEOS_NORMALES` o las bandas de distracción en `config.py` cambia el comportamiento sin tocar otro archivo.
