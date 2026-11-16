# Datos y gobernanza

Gobernanza de datos quiere decir tener por escrito qué datos se usan, de dónde salieron, quién puede verlos, para qué se permite usarlos y cuándo se borran. En este proyecto importa por dos razones. Los videos muestran rostros de personas identificables, que son datos personales. Y las métricas del reporte solo son creíbles si se puede rastrear con qué datos se calcularon.

Este documento no es asesoría legal. Es el criterio práctico del equipo: tratar toda imagen de un rostro como dato personal sensible.

## Inventario de datos

Esta tabla se llena en el paso 0.7 del plan de trabajo. No se evalúa nada con un dataset cuya fila esté incompleta.

| Fuente | Contenido | Personas identificables | Licencia | Dónde vive | Para qué se usa |
|---|---|---|---|---|---|
| Kaggle `dheerajperumandla/drowsiness-dataset` | Por confirmar. Se espera imágenes de ojos abiertos y cerrados, y de bostezo y no bostezo | Por confirmar | Por confirmar en la página de Kaggle | `datos/kaggle/` en cada computadora | Evaluación por cuadro de ojos y boca |
| Kaggle de distracción (liga en el enunciado) | Por confirmar | Por confirmar | Por confirmar | `datos/kaggle/` en cada computadora | Por decidir tras el inventario (D26) |
| Videos de prueba de los profesores | Por recibir | Sí | Uso dentro del curso | Carpeta compartida | Evaluación por evento |
| Videos grabados por el equipo | Guiones G1 a G6 de `evaluacion.md` | Sí, los integrantes | Consentimiento de cada quien | Carpeta compartida | Ajuste y evaluación por evento |
| Anotaciones | Inicio y fin de cada evento en cada video | No | Del equipo | `datos/anotaciones/` en el repositorio | Referencia para las métricas |
| Bitácoras del sistema | Eventos detectados, sin imágenes | No | Del equipo | `salidas/` en cada computadora | Evaluación |

Al inventariar cada dataset de Kaggle se anota: clases, número de imágenes por clase, tamaño de las imágenes, si son recortes de ojo o caras completas, si hay personas repetidas entre entrenamiento y prueba, y qué licencia declara su página.

## Reglas

### 1. Nada con rostros entra al repositorio

- Los videos viven en la carpeta compartida y en `datos/videos/` de cada computadora. El archivo `.gitignore` ya impide subirlos.
- Los datasets de Kaggle no se redistribuyen. Cada quien los descarga con su cuenta desde la liga del enunciado.
- Los cuadernos de Jupyter se suben **sin salidas**. Un cuaderno con una imagen de rostro en una celda ejecutada lleva esa imagen dentro del archivo. Antes de cada commit: menú Kernel, opción "Restart & Clear Output", y guardar.
- Las figuras del reporte que muestren un rostro usan solo a integrantes que dieron consentimiento para eso, y se guardan en Overleaf, no en el repositorio.
- Si por error se sube un archivo con rostros, borrarlo en un commit nuevo no lo quita del historial. Se avisa a Margarita de inmediato para limpiarlo.

### 2. Consentimiento antes de grabar

Cada persona que aparezca en un video llena y firma el texto de abajo antes de grabar. Los consentimientos firmados se guardan en la carpeta compartida.

> **Consentimiento para grabación.** Yo, ______, acepto que se me grabe en video para el proyecto final de Visión Computacional (PCIC-UNAM, semestre 2027-1). Entiendo que:
> - Los videos se usan solo para desarrollar y evaluar el sistema del equipo.
> - Solo los integrantes del equipo y los profesores del curso tienen acceso.
> - Los videos no se publican ni se suben a repositorios.
> - Marco lo que autorizo además: [ ] aparecer en figuras del reporte, [ ] aparecer en el video demostrativo.
> - Los videos se borran cuando se asiente la calificación final del curso.
> - Puedo pedir que se borre un video mío en cualquier momento.
>
> Fecha y firma: ______

### 3. Archivos sin nombres de personas

Los videos se nombran con un código de participante, el guion y un número: `P02_G3_01.mp4`. La correspondencia entre código y persona está solo en la carpeta compartida.

### 4. Acceso mínimo

La carpeta compartida está en Google Drive y la administra Margarita (decisión D20). Los cuatro integrantes tienen permiso de edición y nadie más tiene acceso.

```
Proyecto somnolencia (Google Drive)
├── videos/              los videos, con los nombres de `datos/README.md`
├── consentimientos/     un consentimiento firmado por persona
└── participantes.csv    qué código (P01 a P04) corresponde a qué persona
```

Configuración al crearla:

- Acceso general "restringido". Solo entran las cuatro cuentas agregadas, no cualquiera que tenga la liga.
- En la configuración de compartir, desactivar la opción que deja a los editores cambiar permisos y compartir. Así solo quien administra decide quién entra.
- Los cuatro pueden subir y renombrar. Por acuerdo del equipo, borrar lo hace solo quien administra.
- Si alguien sincroniza la carpeta con su computadora, esa copia cuenta como copia local y se borra en la misma fecha.
- Drive conserva lo borrado en la papelera unos 30 días. Al borrar los videos al final del curso, también se vacía la papelera.

### 5. El sistema no guarda video

Cuando el sistema corre, procesa los cuadros en memoria y no los escribe a disco. La bitácora guarda solo eventos (tipo, inicio, fin, duración). Esto importa en la demo presencial: si un profesor se sienta frente a la cámara, no queda grabado.

La plantilla de calibración es una imagen del rostro. Vive en memoria y se pierde al cerrar el programa.

### 6. Datos de ajuste y datos de evaluación, separados

Los videos se dividen en dos grupos desde el principio y la división queda escrita en `datos/manifiesto.csv`:

- **Ajuste.** Se usan para elegir umbrales y depurar.
- **Evaluación.** No se miran hasta la fase 3. Las métricas del reporte salen solo de aquí.

De preferencia la división se hace por persona: dos integrantes en ajuste y dos en evaluación. Si los umbrales se ajustan con los mismos videos con que se reportan resultados, las métricas salen mejor de lo que el sistema merece, y eso es justo lo que el enunciado pide evitar.

### 7. Trazabilidad de cada número

Cada tabla de resultados del reporte debe poder reproducirse. Para eso, cada corrida de evaluación guarda junto a sus resultados:

- La etiqueta o el commit del código con que se corrió.
- Una copia de los parámetros de `config.py`.
- La lista de videos usados.

### 8. Retención y borrado

| Dato | Se conserva hasta | Quién lo borra |
|---|---|---|
| Videos del equipo | Que se asiente la calificación final | Quien administra la carpeta |
| Videos de los profesores | Lo que ellos indiquen | Quien administra la carpeta |
| Copias locales en `datos/videos/` | La misma fecha | Cada integrante |
| Datasets de Kaggle locales | Sin límite, son públicos | Cada integrante |
| Anotaciones, bitácoras, métricas | Sin límite, no tienen datos personales | No se borran |

## Cobertura y sesgos

Un sistema probado con cuatro personas no está probado para todas. El reporte debe declarar con qué se probó. Esta tabla se llena al grabar:

| Condición | Cubierta en los videos |
|---|---|
| Número de personas | |
| Con lentes | |
| Luz de salón | |
| Luz baja | |
| Contraluz | |
| Distancias a la cámara | |
| Cabello o barba que tape parte del rostro | |

Lo que no esté cubierto se escribe como limitación en la ficha del sistema (`algoritmos_y_modelos.md`).

## Pendientes de este documento

- [x] Cerrar la decisión D20: Google Drive, administra Margarita, los cuatro con edición.
- [ ] Crear la carpeta en Drive con la configuración de la regla 4.
- [ ] Llenar el inventario de los dos datasets de Kaggle.
- [ ] Preguntar a los profesores si los videos de prueba que entreguen tienen alguna restricción de uso.
- [ ] Reunir los cuatro consentimientos antes de grabar.
