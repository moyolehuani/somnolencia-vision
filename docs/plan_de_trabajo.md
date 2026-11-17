# Plan de trabajo

Hoy es lunes 16 de noviembre de 2026. Todavía no hay fecha oficial de entrega. La meta interna es tener todo funcionando el miércoles 2 de diciembre para poder entregar entre el 4 y el 10 con margen.

Este documento tiene el calendario y los hitos. El detalle de cada tarea que falta, con pasos y criterio de terminado, está en [tareas_pendientes.md](tareas_pendientes.md).

## Los cuatro frentes

Cada integrante es responsable de un frente. Responsable significa que esa persona se asegura de que esté hecho y lo defiende en la presentación, aunque reciba ayuda.

| Frente | Qué incluye | Archivos |
|---|---|---|
| **1. Rostro** | Captura, pirámide, correlación normalizada, seguimiento del rostro, normalización geométrica, calibración | `percepcion/captura.py`, `piramide.py`, `correlacion.py` (normalizada), `geometria.py`, `rostro.py`, y la calibración en `sistema.py` |
| **2. Ojos** | Filtros, histograma, gradientes, medición de apertura de ojos | `percepcion/preproceso.py`, `gradiente.py`, `ojos.py`, `evaluacion/por_cuadro.py` |
| **3. Boca y cabeza** | Apertura de boca, correlación de fase, señal de distracción | `percepcion/boca.py`, `cabeza.py`, `correlacion.py` (de fase) |
| **4. Temporal y evaluación** | Estados, eventos, PERCLOS, alertas, interfaz, programa principal, métricas, anotación de videos | `temporal/`, `interfaz/`, `sistema.py`, `principal.py`, `evaluacion/` |

El frente 4 es el punto donde todo se junta, así que conviene que lo lleve quien supervisa. La interfaz puede repartirse con quien termine antes su módulo.

Además del código, cada frente escribe en el reporte la sección de sus algoritmos y su verificación.

## Hitos

| Hito | Fecha | Qué debe existir |
|---|---|---|
| H0 | mié 18 nov | Repositorio creado, todos con el entorno instalado, decisiones pendientes enviadas a los profesores, frentes asignados |
| H1 | dom 22 nov | Capa temporal probada con señales inventadas, calibración y seguimiento del rostro funcionando, videos grabados |
| H2 | dom 29 nov | Sistema completo corriendo de punta a punta con cámara (versión 0.1) |
| H3 | mié 2 dic | Evaluación completa, interfaz final, funciones congeladas (versión 0.9) |
| H4 | dom 6 dic | Reporte, video y ensayo de la demo (versión 1.0) |
| Colchón | 7 al 10 dic | Imprevistos |

## Paso a paso

Las casillas se van marcando en este mismo archivo. Cada paso dice quién lo hace y cuándo se considera terminado.

### Fase 0. Arranque (16 al 18 de noviembre)

- [ ] **0.1 Crear el repositorio privado en GitHub y subir este esqueleto.** Margarita. Instrucciones en `flujo_git.md`. Hecho cuando los cuatro ven el repositorio.
- [ ] **0.2 Invitar a los tres integrantes como colaboradores.** Margarita.
- [ ] **0.3 Instalar el entorno.** Todos. Seguir `despliegue_y_demo.md`. Hecho cuando cada quien abre su cámara con el comando de prueba de ese documento.
- [ ] **0.4 Asignar frentes.** Equipo. Hecho cuando la tabla de equipo del README raíz y la decisión D22 tienen nombres.
- [ ] **0.5 Enviar a los profesores las preguntas D09 y D10.** Margarita. Las preguntas ya están redactadas en `decisiones.md`.
- [ ] **0.6 Crear la carpeta compartida de videos y cerrar D20.** Margarita.
- [ ] **0.7 Descargar los dos datasets de Kaggle e inventariarlos.** Frente 2 y frente 3. Llenar la tabla de `datos_y_gobernanza.md` (clases, número de imágenes, tamaño, licencia). Hecho cuando la tabla no tiene celdas vacías.
- [x] **0.8 Escribir `config.py` y `tipos.py`.** (Escrito el 16 de noviembre. Falta que el equipo lo revise.) Frente 4. Hecho cuando todos los umbrales del enunciado están ahí con su cita y los otros frentes pueden importar `Medicion`.
- [ ] **0.9 Decidir equipo y cámara de la demo (D24).** Equipo.

### Fase 1. Cimientos (16 al 22 de noviembre)

Los cuatro frentes avanzan en paralelo. Nadie depende de otro todavía.

- [x] **1.1 Capa temporal completa con pruebas.** (Escrita el 16 de noviembre, con 57 pruebas. Falta que el equipo la revise.) Frente 4. `estados.py`, `eventos.py`, `perclos.py`, `alertas.py`. Hecho cuando pasan todas las pruebas listadas en `pruebas/README.md`.
- [x] **1.2 Simulador de señales.** (Escrito el 16 de noviembre.) Frente 4. Un generador de mediciones inventadas (por ejemplo, ojos cerrados de 10.0 a 13.0 s) para probar la capa temporal y la interfaz sin cámara.
- [ ] **1.3 Captura y calibración.** Frente 1. Escritas (`captura.py` y la calibración dentro de `sistema.py`) y probadas con la escena dibujada. Hecho cuando se prueban con cámara: el programa muestra el recuadro y la calibración termina sin aviso.
- [x] **1.4 Pirámide y correlación normalizada, verificadas.** Frente 1. (Escritas el 16 de noviembre. Falta que el frente 1 las revise.)
- [ ] **1.5 Seguimiento del rostro.** Frente 1. Escrito (`rostro.py`) y probado con la escena dibujada. Hecho cuando la caja sigue la cara en vivo y el puntaje baja al voltear. Revisar en especial cuánto baja el puntaje al cerrar los ojos (D32).
- [x] **1.6 Especificación de histograma y suavizado, verificados.** Frente 2. (Escritos el 16 de noviembre. Falta que el frente 2 los revise.)
- [x] **1.7 Gradientes y medida de ojos, verificados.** Frente 2. (Escrito el 16 de noviembre y probado con 84 imágenes de Kaggle. La medida original se descartó, ver D28.)
- [x] **1.7b Correr la evaluación de ojos con el dataset completo.** (Corrida el 16 de noviembre: F1 de 0.86 y 0.84.) Frente 2. `python -m evaluacion.por_cuadro datos/kaggle/drowsiness-dataset/train`. Hecho cuando la tabla del nivel 2 de `evaluacion.md` tiene la fila del dataset completo.
- [x] **1.8 Correlación de fase, verificada.** Frente 3. (Escrita el 16 de noviembre. Falta que el frente 3 la revise.)
- [ ] **1.9 Grabar los videos con guion.** Todos. Lista de videos en `evaluacion.md`. Antes de grabar, cada quien firma el consentimiento de `datos_y_gobernanza.md`.
- [ ] **1.10 Anotar los videos.** Frente 4 con ayuda. Formato en `datos/README.md`.

**Revisión de H1 (domingo 22).** Margarita corre las pruebas y el programa de verificación, y confirma que cada frente mostró su avance funcionando.

### Fase 2. Módulos e integración (23 al 29 de noviembre)

- [ ] **2.1 Normalización geométrica del rostro.** Frente 1. La función ya está escrita y verificada (`geometria.py`). Falta conectarla al seguimiento. Hecho cuando el rostro normalizado se ve estable aunque la persona se acerque o se aleje un poco.
- [ ] **2.2 Medición de ojos.** Frente 2. `ojos.py` entrega `Medicion`. Incluye agregar a la calibración, junto con el frente 1, el paso de ojos cerrados y la ubicación de la franja de ojos. Hecho cuando la apertura baja claramente al cerrar los ojos en vivo.
- [ ] **2.3 Medición de boca.** Frente 3. Escrita (`boca.py`) pero sin validar con bocas reales (D31). Hecho cuando distingue bostezar de hablar en los videos del guion G3.
- [ ] **2.4 Medición de cabeza.** Frente 3. Escrita (`cabeza.py`). Hecho cuando los umbrales están ajustados con los videos del guion G4.
- [x] **2.5 Ciclo principal.** Frente 4. (Escrito el 16 de noviembre: `sistema.py` y `principal.py`. Corre con la escena y con un archivo de video. Falta probar la ventana y la cámara.)
- [x] **2.6 Interfaz mínima.** Frente 4. (Escrita el 16 de noviembre: `overlay.py`.)
- [ ] **2.7 Primera integración (jueves 26).** Todos. Se juntan los módulos aunque estén incompletos. El objetivo es descubrir pronto lo que no embona.
- [ ] **2.8 Primeras métricas.** Frente 4. Aunque sean malas. Sirven para saber qué módulo arreglar primero.

**Revisión de H2 (domingo 29).** El sistema corre de punta a punta con cámara. Se crea la etiqueta `v0.1`.

### Fase 3. Evaluación y cierre de funciones (30 de noviembre al 2 de diciembre)

- [ ] **3.1 Ajustar umbrales con los videos de ajuste.** Cada frente los suyos. Nunca con los videos de evaluación (decisión D17).
- [ ] **3.2 Vista de depuración y deslizadores.** Frente 4. Hay una primera versión: rostro normalizado con sus franjas, y cuatro deslizadores sin probar. Falta mostrar la pirámide, la banda laplaciana y la gráfica de las mediciones.
- [x] **3.3 Bitácora de eventos en CSV.** Frente 4. (Escrita el 16 de noviembre: `bitacora.py`.)
- [ ] **3.4 Evaluación por cuadro sobre Kaggle.** Frentes 2 y 3.
- [ ] **3.5 Evaluación por evento sobre los videos de evaluación.** Frente 4.
- [ ] **3.6 Medición de desempeño en el equipo de la demo.** Frente 1.
- [ ] **3.7 Tablas de verificación completas.** Cada frente. La tabla ya tiene los resultados de la primera corrida. Falta repetir los tiempos en el equipo de la demo con `python -m verificacion.verificar`.
- [ ] **3.8 Congelar funciones.** Margarita. A partir de aquí solo se corrigen errores. Se crea la etiqueta `v0.9`.

### Fase 4. Reporte, video y ensayo (3 al 6 de diciembre)

- [ ] **4.1 Reporte.** Cada frente su sección. Estructura en `reporte/README.md`.
- [ ] **4.2 Ficha del sistema y limitaciones.** Margarita. Plantilla en `algoritmos_y_modelos.md`.
- [ ] **4.3 Video demostrativo de 3 a 5 minutos.** Guion en `reporte/README.md`.
- [ ] **4.4 Ensayo de la demo.** Todos, en el equipo real y con luz parecida a la del salón. Lista de verificación en `despliegue_y_demo.md`.
- [ ] **4.5 Instalación desde cero.** Alguien clona el repositorio en una carpeta nueva y sigue el README sin ayuda. Si algo falla, se corrige el README.
- [ ] **4.6 Etiqueta `v1.0` y entrega.** Margarita.
- [ ] **4.7 Preparar la defensa.** Cada integrante explica su módulo a otro y responde por qué eligió cada parámetro.

### Después de la entrega

- [ ] **5.1 Borrar los videos de la carpeta compartida cuando se asiente la calificación** (decisión D21).

## Qué hacer si algo se atrasa

El orden de recorte, de lo primero que se sacrifica a lo último:

1. SIFT con RANSAC (ya es opcional).
2. Vista de depuración elaborada. Basta con mostrar dos o tres imágenes intermedias.
3. Correlación de fase en `cabeza.py`. La distracción puede detectarse solo con la caída del puntaje de correlación. En ese caso Fourier se pierde como algoritmo y quedan cinco, que sigue arriba del mínimo de cuatro.
4. Evaluación con más de una persona.

Lo que no se recorta: la capa temporal con sus pruebas, la verificación contra OpenCV de cada algoritmo, y el ensayo de la demo.
