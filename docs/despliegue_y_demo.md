# Despliegue y demo

## Qué significa desplegar en este proyecto

Desplegar es llevar el sistema de "funciona en mi computadora" a "funciona donde se va a usar". Aquí ese lugar es una computadora con cámara frente a los profesores, el día de la demostración. No hay servidores ni usuarios externos, pero el problema es el mismo de cualquier despliegue: que lo que se probó sea exactamente lo que se presenta, y que haya un plan si algo falla.

Eso se logra con cuatro cosas:

1. **Entorno reproducible.** Cualquiera instala lo mismo siguiendo las mismas instrucciones.
2. **Versiones con etiqueta.** Se sabe exactamente qué código se evaluó y qué código se presentó.
3. **Ensayo en condiciones reales.** Mismo equipo, misma cámara, luz parecida.
4. **Plan B.** Qué hacer si la cámara o la luz fallan.

## Entorno

### Requisitos

- Python 3.10 o más reciente. Los cuatro integrantes usan la misma versión. Se comprueba con `python --version`.
- Una cámara web.
- Git.

### Instalación paso a paso

```bash
# 1. Descargar el repositorio
git clone <URL del repositorio>
cd somnolencia-vision

# 2. Crear un entorno aislado para el proyecto
python -m venv .venv

# 3. Activarlo (hay que hacerlo cada vez que se abre una terminal nueva)
source .venv/bin/activate          # Linux y macOS
.venv\Scripts\activate             # Windows

# 4. Instalar las bibliotecas
pip install -r requirements.txt
```

El entorno virtual (`.venv`) es una carpeta con una copia de Python y las bibliotecas solo para este proyecto. Evita que las versiones de otro proyecto interfieran.

### Comprobar que la cámara abre

```bash
python -c "import cv2; c = cv2.VideoCapture(0); print('camara:', c.isOpened()); c.release()"
```

Debe imprimir `camara: True`. Si imprime `False`, probar con `1` en lugar de `0`, cerrar otros programas que usen la cámara y revisar los permisos del sistema operativo.

### Archivos de bibliotecas

Aquí deben ir dos archivos en la raíz del repositorio. Los crea el frente 4 en el paso 0.8.

| Archivo | Contenido | Quién lo instala |
|---|---|---|
| `requirements.txt` | `numpy`, `opencv-python` | Todos. Es lo único que necesita la demo |
| `requirements-dev.txt` | `pytest`, `matplotlib`, `jupyter` | Todos, para pruebas, gráficas y cuadernos de verificación |

Cuando el sistema funcione por primera vez en una computadora, se anotan las versiones exactas en esos archivos (por ejemplo `numpy==X.Y.Z`). Las versiones instaladas se ven con `pip freeze`. Así todos instalan lo mismo.

Mantener `requirements.txt` con solo dos bibliotecas es deliberado. Demuestra que el sistema no depende de ningún modelo preentrenado.

## Ejecución

```bash
python -m somnolencia.principal --fuente 0                  # cámara
python -m somnolencia.principal --fuente datos/videos/P01_G2_01.mp4   # video
python -m somnolencia.principal --fuente simulador          # señales inventadas, sin cámara
```

Teclas dentro de la ventana (las implementa `interfaz/controles.py`):

| Tecla | Acción |
|---|---|
| `c` | Recalibrar |
| `d` | Mostrar u ocultar la vista de depuración |
| `r` | Reiniciar contadores |
| `q` | Salir |

## Versiones

Una etiqueta de Git es un nombre fijo para un punto exacto del código. Se crean tres:

| Etiqueta | Cuándo | Qué significa |
|---|---|---|
| `v0.1` | 29 de noviembre | Primera versión que corre de punta a punta |
| `v0.9` | 2 de diciembre | Funciones congeladas. Es la versión que se evalúa |
| `v1.0` | 6 de diciembre | La que se entrega y se presenta |

```bash
git switch main
git pull
git tag -a v1.0 -m "Entrega del proyecto final"
git push origin v1.0
```

Entre `v0.9` y `v1.0` solo entran correcciones de errores y documentación. Si se cambia algo que afecte las métricas, se vuelve a correr la evaluación.

## Entrega del software

El enunciado pide código fuente completo, organizado y documentado, con instrucciones de instalación y ejecución. Falta preguntar a los profesores cómo lo quieren recibir. Las dos formas habituales:

- Un archivo zip descargado desde la etiqueta `v1.0` en GitHub (botón "Code", opción "Download ZIP" con la etiqueta seleccionada).
- Acceso de lectura al repositorio privado.

En cualquiera de los dos casos el paquete no lleva videos ni datasets.

## Ensayo de la demo

La demostración presencial vale 20% y es obligatoria. Se ensaya completa al menos una vez, en el equipo real.

### Una semana antes

- [ ] Decidido en qué computadora y con qué cámara se presenta (D24).
- [ ] El sistema instalado desde cero en esa computadora, siguiendo este documento.
- [ ] Medido el desempeño en esa computadora.

### Un día antes

- [ ] Instalación limpia desde la etiqueta `v1.0` en una carpeta nueva.
- [ ] Ensayo completo con cronómetro: calibración, parpadeo normal, cierre largo, bostezo, giro de cabeza, cambio de un parámetro con el deslizador, vista de depuración.
- [ ] Cada integrante explica su módulo en dos minutos frente a los demás.
- [ ] Video de respaldo copiado en la computadora (un video propio de guion G5).
- [ ] Computadora con batería cargada y cargador en la mochila.
- [ ] Actualizaciones automáticas del sistema operativo pospuestas.

### En el salón, antes de empezar

- [ ] Cerrar todo programa que use la cámara.
- [ ] Revisar la luz. Evitar una ventana detrás de la persona. Si la luz del salón es muy distinta a la del ensayo, recalibrar con calma antes de que empiece la evaluación.
- [ ] Fondo sin otras caras a la vista.
- [ ] Abrir el sistema y dejarlo calibrado.

### Durante la demo

Orden sugerido, que coincide con el del video demostrativo:

1. Calibración y explicación de qué se guarda.
2. Vista de depuración: pirámide, rostro normalizado, perfiles de gradiente.
3. Parpadeo normal, cierre de 2 s con aviso, cierre largo con alerta.
4. Bostezo, y mostrar que hablar no lo dispara.
5. Giro de cabeza y bandas de distracción.
6. PERCLOS subiendo tras varios cierres.
7. Cambio de un umbral con el deslizador y su efecto.

### Plan B

| Si pasa esto | Se hace esto |
|---|---|
| La cámara no abre | Probar el otro índice de cámara. Si no, correr con el video de respaldo y decir por qué |
| La luz impide el seguimiento | Recalibrar. Mover a la persona. Si no mejora, video de respaldo |
| El sistema va muy lento | Bajar la resolución con la opción prevista en `config.py` |
| La computadora falla | Segunda computadora con el sistema instalado y probado |
| Un profesor quiere probarlo | Se recalibra con su rostro. El sistema no guarda video (regla 5 de `datos_y_gobernanza.md`) |

Conviene llevar el sistema instalado en dos computadoras del equipo.
