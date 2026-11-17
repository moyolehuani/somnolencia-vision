# Registro de decisiones

Aquí se anota cada decisión del proyecto con su razón. Sirve para dos cosas: que nadie tenga que adivinar por qué algo se hizo así, y que en la defensa cualquier integrante pueda justificarlo.

Estados posibles:

- **Tomada.** Ya se trabaja con ella.
- **Provisional.** Se trabaja con un valor por omisión mientras alguien confirma.
- **Pendiente.** Bloquea trabajo hasta que se resuelva.

Cuando una decisión cambie, se edita su renglón, se anota la fecha y se avisa al equipo.

## Resumen

| ID | Decisión | Estado | Quién decide |
|---|---|---|---|
| D01 | Arquitectura clásica en dos capas (percepción y temporal) | Tomada | Equipo |
| D02 | Los algoritmos principales son los de las prácticas 3 a 7 | Tomada | Equipo |
| D03 | El proyecto no usa redes ni modelos preentrenados, ni dentro ni fuera del sistema | Tomada | Margarita |
| D04 | Repositorio privado; los videos viven fuera del repositorio | Tomada | Margarita |
| D05 | Documentación y nombres en el código en español | Tomada | Margarita |
| D06 | Python para todo lo que se entrega; MATLAB solo para explorar | Tomada | Equipo |
| D07 | El rostro se localiza con plantilla de calibración, no con detector | Tomada | Equipo |
| D08 | Interfaz con ventanas y deslizadores de OpenCV | Provisional | Equipo |
| D09 | PERCLOS no cuenta los parpadeos normales | **Pendiente** | Profesores |
| D10 | Interpretación de las bandas de distracción | **Pendiente** | Profesores |
| D11 | Duración mínima para contar un bostezo | **Pendiente** | Equipo, con cita |
| D12 | La alerta suena durante el evento, no al terminar | Tomada | Equipo |
| D13 | Estado `SIN_DATO` cuando no se puede medir | Tomada | Equipo |
| D14 | Rostro no encontrado cuenta como distracción | Provisional | Equipo |
| D15 | Umbrales de apertura de ojos (cierre 0.20, reapertura 0.35) | Provisional | Frente 2 |
| D16 | Antirrebote: huecos de hasta 2 cuadros no parten un evento | Provisional | Frente 4 |
| D17 | Los umbrales se fijan antes de evaluar y no se ajustan con los videos de prueba | Tomada | Equipo |
| D18 | Videos en 1280×720 a 30 cuadros por segundo; el sistema trabaja en 640×360; rostro normalizado a 128×160 | Provisional | Frente 1 |
| D19 | SIFT con RANSAC queda como extra opcional | Tomada | Equipo |
| D20 | Videos en Google Drive; administra Margarita; los cuatro con permiso de edición | Tomada | Margarita |
| D21 | Los videos se borran al terminar el curso | Provisional | Equipo |
| D22 | Reparto de frentes entre los cuatro | **Pendiente** | Equipo |
| D23 | Meta interna: todo funcionando el 2 de diciembre | Tomada | Margarita |
| D24 | Equipo y cámara que se usarán en la demo | **Pendiente** | Equipo |
| D25 | Calibración en dos pasos: ojos abiertos y ojos cerrados | Provisional | Frentes 1 y 2 |
| D26 | Qué uso se le da al dataset de distracción de Kaggle | **Pendiente** | Equipo, tras inventariarlo |
| D27 | Los cuatro integrantes aceptan ser grabados y aparecer en el reporte y en el video | Tomada | Cada integrante |
| D28 | La apertura de ojos se mide con la razón entre bordes verticales y horizontales | Tomada | Equipo |
| D29 | Cómo arranca el sistema con un video que no trae calibración | **Pendiente** | Profesores y equipo |
| D30 | PERCLOS durante los primeros 30 s de la sesión | Provisional | Frente 4 |
| D31 | Medida de apertura de la boca | **Pendiente** | Frente 3 |
| D32 | La plantilla del rostro usa solo la parte de arriba de la cara | Provisional | Frente 1 |
| D33 | La iluminación se mide en la parte de arriba del rostro y se corrige en todo el rostro | Provisional | Frente 2 |

## Detalle de las decisiones tomadas y provisionales

### D01. Arquitectura clásica en dos capas

El enunciado pide al menos cuatro algoritmos vistos en clase implementados por el equipo y califica con 5 un sistema que sea solo una red. La separación en dos capas se explica en `arquitectura.md`.

### D02. Algoritmos de las prácticas

Se usan especificación de histograma (P4), filtros espaciales (P5), pirámides y Fourier (P6) y transformación geométrica con mapeo inverso (P3). Son cinco técnicas que el equipo ya implementó y puede defender. Si antes de la entrega hay una práctica de segmentación o de movimiento, puede entrar como mejora de `ojos.py` o `cabeza.py` sin cambiar lo demás.

### D03. Sin redes entrenadas por el equipo

Decidida el 16 de noviembre. El enunciado no pide una red y califica con 5 un sistema que sea solo eso. Se consideró entrenar un clasificador propio de apoyo con Kaggle y se descartó: entrenarlo, validarlo y defenderlo cuesta más tiempo del que aporta.

También se consideró usar un modelo preentrenado de puntos faciales fuera del sistema, solo para comparar, y se descartó el mismo día. Era una biblioteca más que instalar y un tema más que defender, y la evaluación se sostiene con las anotaciones hechas a mano. La carpeta `referencia/` que lo contenía se borró.

### D06. Python

Decidida el 16 de noviembre. Los cuatro trabajan cómodos en Python, y todo lo que se entrega (el sistema, las pruebas, la verificación y la evaluación) va en Python.

Se consideró combinar Python y MATLAB y se descartó para el entregable, por cuatro razones:

- La demo corre en una sola computadora. Con dos lenguajes hay que instalar, licenciar y probar dos entornos, y cualquiera de los dos puede fallar ese día.
- El sistema procesa video en vivo dentro de un solo ciclo. Pasar cada cuadro de un lenguaje al otro es lento y frágil.
- Las funciones cómodas de MATLAB para imágenes (`imfilter`, `imhistmatch`, `normxcorr2`) son justo las funciones preestablecidas que el enunciado no deja usar como algoritmo propio.
- En la defensa cualquier integrante debe poder explicar cualquier parte. Un solo lenguaje lo facilita.

MATLAB sí puede usarse para explorar una idea antes de programarla, por ejemplo para ver cómo se ve un perfil de gradiente. Ese código no entra al repositorio y la versión que cuenta es la de Python.

### D07. Plantilla de calibración en vez de detector

Un detector de rostros general necesitaría segmentación por color de piel (no vista en las prácticas) o una red (penalizada). Con calibración, el rostro se sigue por correlación sobre la pirámide, que sí son técnicas de las prácticas. El costo es que el sistema sirve para una persona por sesión.

### D08. Interfaz con OpenCV

Las ventanas y deslizadores de OpenCV (`cv2.imshow`, `cv2.createTrackbar`) bastan para mostrar el overlay y cambiar parámetros en vivo, que es lo que pide el video demostrativo. No hay que aprender otra biblioteca. Si sobra tiempo se puede pasar a Tkinter sin tocar el resto.

### D12. Alerta durante el evento

La categoría de un parpadeo (normal, lento, microsueño) solo se conoce cuando el ojo vuelve a abrirse. Pero avisar hasta entonces no sirve. Por eso la alerta se dispara mientras el cierre sigue: un aviso al cruzar 1.5 s, que es el umbral de alerta de la literatura citada en el enunciado, y la alerta máxima al cruzar 7 s.

### D13. Estado SIN_DATO

Cuando el rostro no se ve de frente, la medición de ojos no es confiable. En vez de reportar "cerrado", el módulo marca `valido = False` y la capa temporal usa `SIN_DATO`. Ese tiempo no cuenta para PERCLOS ni abre parpadeos. Sin esto, cada giro de cabeza se contaría como un cierre de ojos.

### D14. Rostro no encontrado cuenta como distracción

Si la plantilla frontal no aparece, lo más probable es que la persona volteó. El riesgo es contar como distracción una falla del seguimiento por mala luz. Se revisa con los videos de prueba.

### D15. Umbrales de apertura

El ojo se declara cerrado cuando la apertura baja de 0.20 (es decir, 80% cerrado respecto a la calibración, que es el criterio habitual de PERCLOS) y se declara abierto de nuevo cuando sube de 0.35. Usar dos umbrales evita que una medición que oscila cerca del límite genere parpadeos falsos.

### D16. Antirrebote

Si en medio de un cierre largo aparece uno o dos cuadros clasificados como abiertos, se consideran ruido y el evento sigue. Sin esto, un microsueño de 8 s podría contarse como dos parpadeos lentos de 4 s.

### D17. Umbrales fijados antes de evaluar

El enunciado dice que sus umbrales se eligieron antes de la evaluación, a partir de la literatura. Se sigue el mismo criterio con los propios: se ajustan con un grupo de videos de ajuste y se reportan resultados sobre un grupo distinto que no se tocó. Ver `evaluacion.md`.

### D18. Resoluciones

Los videos se graban en 1280×720 a 30 cuadros por segundo, que es lo que entrega casi cualquier webcam. El sistema reduce cada cuadro a la mitad, 640×360, y trabaja ahí. La pirámide queda en 640×360, 320×180 y 160×90. Las especificaciones completas de grabación están en `datos/README.md`.

### D20. Carpeta compartida de videos

Decidida el 16 de noviembre. Los videos y los consentimientos viven en una carpeta de Google Drive que administra Margarita. Los cuatro integrantes tienen permiso de edición. La configuración recomendada está en `datos_y_gobernanza.md`.

### D27. Consentimiento del equipo

Los cuatro integrantes aceptaron ser grabados y aparecer en las figuras del reporte y en el video demostrativo. Aun así cada quien llena y firma el formato de `datos_y_gobernanza.md` antes de grabar, para que quede por escrito.

### D21. Borrado de videos

Los videos muestran rostros del equipo. Se conservan hasta que se asiente la calificación final y después se borran de la carpeta compartida. Ver `datos_y_gobernanza.md`.

### D25. Calibración en dos pasos

Pedir también dos segundos con los ojos cerrados da la referencia de "cerrado" de esa persona, que junto con la de "abierto" convierte la medida de ojos en una apertura entre 0 y 1. Cuesta dos segundos más al inicio. Si en las pruebas resulta innecesario, se regresa a un solo paso y se usa la referencia general de `config.py`.

### D28. Medida de ojos

Decidida el 16 de noviembre, con datos. El diseño inicial medía la separación entre los picos del perfil del gradiente vertical. Se probó con 84 recortes de ojos de Kaggle y no separó abiertos de cerrados mejor que el azar.

Se compararon otras medidas con la mitad de las imágenes y se eligió la razón entre bordes verticales y horizontales alrededor de la banda más oscura del ojo. Con la otra mitad dio F1 de 0.88, y 0.89 al intercambiar las mitades. Después se corrió con el dataset completo (1452 imágenes) y dio 0.86 y 0.84, debajo de la meta de 0.90 pero estable. Usa los mismos filtros de la práctica 5. Explicación en `algoritmos_y_modelos.md`.

### D30. PERCLOS al inicio

Mientras la sesión lleva menos de 30 s, PERCLOS se calcula sobre el tiempo transcurrido, y no se reporta antes de 10 s. La consecuencia es que al principio es nervioso: a los 11 s de sesión, un cierre de 1 s ya da 9% y dispara el aviso. La alternativa es no reportar PERCLOS hasta tener 30 s completos, cambiando `PERCLOS_TIEMPO_MINIMO_S` a 30. Queda provisional hasta verlo en vivo.

### D32. Plantilla sin la boca

La plantilla con la que se sigue el rostro usa el 65% superior de la caja: frente, ojos y nariz. Si incluyera la boca, un bostezo haría que el rostro dejara de parecerse a su plantilla, el sistema lo tomaría por un giro de cabeza y el bostezo no se contaría.

**Riesgo que queda abierto.** Los ojos sí están en la plantilla, así que cerrarlos también baja el parecido. Con la cara dibujada el puntaje baja de 0.91 a 0.70 al cerrar los ojos, y el umbral de distracción está en 0.50. Si con una persona real bajara de 0.50, un cierre de ojos se tomaría por distracción, los ojos quedarían sin dato y un microsueño no se detectaría. Es lo primero que hay que mirar con el primer video real. Si pasa, las salidas son bajar el umbral de distracción o quitar la zona de los ojos de la plantilla.

### D33. Dónde se mide la iluminación

La especificación de histograma supone que la imagen y la referencia muestran lo mismo y que solo cambió la luz. Con el rostro completo eso no se cumple: al abrir la boca hay más pixeles oscuros, y la especificación los aclara como si fueran un cambio de luz. Se vio al correr el sistema completo: el bostezo de la escena dibujada no se detectaba.

La solución fue armar la tabla de niveles de gris con la parte de arriba del rostro, que casi no cambia, y aplicarla al rostro completo. Solo la boca usa el rostro corregido, porque su medida depende de un umbral de gris fijo. La medida de ojos es un cociente y no lo necesita.

## Detalle de las decisiones pendientes

### D09. PERCLOS y los parpadeos normales

**El problema.** Una persona despierta parpadea unas 17 veces por minuto y cada parpadeo dura alrededor de 0.3 s. Eso suma 5.1 s con los ojos cerrados por minuto, es decir 8.5%. El umbral de alerta del enunciado es 8%. Si PERCLOS cuenta todos los cuadros con ojos cerrados, una persona despierta puede estar en alerta permanente.

**Opciones.**

1. PERCLOS cuenta solo cierres mayores a 0.5 s. Es la propuesta.
2. PERCLOS cuenta todo cuadro con ojos cerrados.

**Mientras se resuelve.** Se programa con un interruptor en `config.py` (`PERCLOS_CUENTA_PARPADEOS_NORMALES = False`) para poder cambiarlo sin tocar código.

**Pregunta para los profesores.** "¿PERCLOS debe incluir los parpadeos normales de hasta 0.5 s, o solo los cierres más largos?"

### D10. Bandas de distracción

**El problema.** El enunciado dice que los episodios de distracción "se agrupan en bandas de duración (0.5, 1.0, 1.5 y 2.0 s)" pero no dice si esos números son el inicio o el fin de cada banda.

**Propuesta.** Menos de 0.5 s no se cuenta. Después: de 0.5 a menos de 1.0 s, de 1.0 a menos de 1.5 s, de 1.5 a menos de 2.0 s, y 2.0 s o más.

**Pregunta para los profesores.** "¿Las bandas de distracción son intervalos que empiezan en 0.5, 1.0, 1.5 y 2.0 s, y los giros menores a 0.5 s no se cuentan?"

### D11. Duración mínima del bostezo

**El problema.** El enunciado dice que los bostezos se cuentan como eventos pero no da una duración mínima. Sin ella, hablar o reír se cuenta como bostezo.

**Mientras se resuelve.** Valor provisional de 1.5 s en `config.py`. Falta buscar una fuente que lo respalde y anotarla, igual que el enunciado respalda sus umbrales.

### D22. Reparto de frentes

Los cuatro frentes están en `plan_de_trabajo.md`. Falta poner un nombre en cada uno.

### D26. Dataset de distracción

**El problema.** La medición de cabeza compara cada cuadro contra la plantilla frontal de la persona calibrada. Eso no puede aplicarse a fotos sueltas de otras personas, que es lo que trae un dataset de imágenes. La distracción se evalúa entonces con los videos propios del guion G4.

**Qué falta.** Inventariar el dataset (paso 0.7) y decidir si sirve para algo más, por ejemplo como ejemplos visuales en el reporte. También preguntar a los profesores si usar los dos datasets es obligatorio o si son un apoyo.

### D24. Equipo de la demo

Falta decidir en qué computadora y con qué cámara se presenta. Importa porque el ensayo final y las mediciones de desempeño deben hacerse en ese mismo equipo.

### D29. Videos sin calibración

**El problema.** El sistema arranca con una calibración: la persona pone la cara en un recuadro, mira al frente y cierra los ojos. Eso funciona en la demo en vivo. Pero el enunciado dice que se proporcionarán videos de prueba, y un video ya grabado no trae esa secuencia. Además, las imágenes de bostezo de Kaggle muestran personas dentro de un auto, con el rostro pequeño y visto de lado. Si los videos de prueba son así, la calibración como está diseñada no aplica.

**Propuesta.** Un segundo modo de arranque para archivos de video:

1. Quien opera el sistema marca el rostro con el ratón en el primer cuadro. Es parte de la interfaz, no un algoritmo.
2. Esa caja se toma como plantilla.
3. Para los ojos se usan las referencias generales de `config.py` (0.72 y 0.41), que salieron del dataset de Kaggle y funcionaron sin calibración.

**Qué falta.** Preguntar a los profesores cómo serán los videos de prueba y si se permite marcar el rostro a mano. La pregunta está en `guia_de_supervision.md`.

### D31. Medida de la boca

**El problema.** El diseño inicial usaba para la boca la misma medida que para los ojos (separación de picos), y esa medida se descartó. Las imágenes de bostezo de Kaggle no sirven para probar otra, porque son escenas completas y no recortes de boca.

**Propuesta.** Medir el alto de la zona oscura de la boca, descrito en `somnolencia/percepcion/README.md`.

**Qué falta.** Probarla con los videos del guion G3 antes de darla por buena.
