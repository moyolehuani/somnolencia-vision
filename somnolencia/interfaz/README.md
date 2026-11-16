# `interfaz/`

Lo que se ve en pantalla y lo que se guarda. La interfaz vale 15% de la calificación junto con la integración, y el video demostrativo debe mostrar la modificación interactiva de parámetros.

Responsable: frente 4, con ayuda de quien termine antes su módulo.

Se usa OpenCV para ventanas, dibujo y deslizadores (decisión D08). El enunciado lo permite para visualización e interfaces. Aquí sí se puede usar `cv2.resize` para acomodar las vistas, porque es presentación y no parte de un algoritmo.

---

## `overlay.py`

**Aquí debe ir el código que** dibuja la información sobre el cuadro de video.

- `dibujar(cuadro, datos)`: entrega el cuadro anotado.

Qué debe verse en la vista principal:

- La caja del rostro, con color según el estado de la cabeza.
- Las franjas de ojos y boca dentro de la caja.
- Tres barras con las mediciones actuales (ojos, boca, cabeza) y la marca de sus umbrales.
- El estado de cada señal en texto.
- PERCLOS con su nivel, o "calentando".
- Los contadores: parpadeos normales, lentos y microsueños, bostezos, y distracciones por banda.
- Si hay un evento en curso, su cronómetro.
- La alerta vigente, bien visible, con su motivo.
- Los cuadros por segundo.

Sugerencia de colores para la alerta: sin color cuando no hay, amarillo para aviso, naranja para alerta, rojo para crítica. Además del color, el texto dice el nivel, para que se entienda en una proyección con mal contraste.

---

## Vista de depuración

**Aquí debe ir también el código que** muestra las imágenes intermedias en una segunda ventana. Se activa con la tecla `d`.

- Los niveles de la pirámide.
- La banda laplaciana donde se busca la plantilla, con la ventana de búsqueda marcada.
- El rostro normalizado, antes y después de especificar el histograma.
- La franja de ojos con su perfil de gradiente dibujado al lado, y los dos picos marcados.
- Lo mismo para la boca.
- La gráfica de las tres mediciones en los últimos 10 segundos, con sus umbrales.

Esta vista es la herramienta principal de la defensa. Con ella, cualquier resultado del sistema se puede explicar señalando la imagen que lo produjo.

---

## `controles.py`

**Aquí debe ir el código que** permite cambiar parámetros mientras el sistema corre y atiende el teclado.

Deslizadores:

| Deslizador | Parámetro |
|---|---|
| Umbral de cierre de ojos | `OJOS_UMBRAL_CIERRE` |
| Umbral de reapertura de ojos | `OJOS_UMBRAL_REAPERTURA` |
| Umbral de apertura de boca | `BOCA_UMBRAL_APERTURA` |
| Umbral de distracción | `CABEZA_UMBRAL_DISTRAIDO` |
| Ventana de búsqueda del rostro | `BUSQUEDA_VENTANA_PX` |
| Antirrebote | `ANTIRREBOTE_CUADROS` |

Los umbrales de duración del enunciado (0.5 s, 7 s, PERCLOS) no llevan deslizador. Son parte de la especificación y no se ajustan.

Teclas:

| Tecla | Acción |
|---|---|
| `c` | Recalibrar |
| `d` | Mostrar u ocultar la vista de depuración |
| `r` | Reiniciar contadores y PERCLOS |
| `q` | Salir |

Los deslizadores cambian los valores solo durante la sesión. No reescriben `config.py`.

---

## `bitacora.py`

**Aquí debe ir el código que** guarda cada evento cerrado en un archivo CSV dentro de `salidas/`.

Columnas: `tipo`, `inicio_s`, `fin_s`, `duracion_s`, `categoria`.

Además, al iniciar escribe un archivo junto a la bitácora con los parámetros vigentes y la fuente usada. La evaluación lee estos archivos, así que el formato es el mismo de las anotaciones (ver `datos/README.md`).

La bitácora no guarda imágenes ni video.

---

## Hecho cuando

- La vista principal se entiende sin explicación por alguien que no conoce el proyecto.
- Mover un deslizador cambia el comportamiento de inmediato y se ve en pantalla.
- La vista de depuración muestra al menos la pirámide, el rostro normalizado y los perfiles de gradiente.
- Al cerrar el programa queda una bitácora que `evaluacion/por_evento.py` puede leer.
- Dibujar todo tarda menos de 8 ms por cuadro con la vista de depuración apagada.
