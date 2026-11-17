# Guía de supervisión

Este documento es para quien coordina el proyecto. Explica qué significa supervisar un despliegue, qué revisar y cuándo, y qué decisiones siguen abiertas.

## Qué significa supervisar aquí

Supervisar no es escribir todo el código ni revisar cada línea. Es asegurarse de seis cosas:

1. **Las decisiones están escritas.** Si alguien pregunta por qué el umbral es 0.5 s, la respuesta está en `decisiones.md` o en `config.py`, no en la memoria de una persona.
2. **Las piezas embonan.** Cada módulo entrega lo que acordó entregar. Es el contrato de `arquitectura.md`.
3. **Cada pieza trae evidencia de que funciona.** Una prueba que pasa o una tabla de verificación. "A mí me corre" no cuenta.
4. **La integración ocurre pronto.** Juntar las piezas por primera vez tres días antes de la entrega es el error más común en proyectos de equipo. Por eso el plan tiene una primera integración el 26 de noviembre aunque los módulos estén incompletos.
5. **Los datos se manejan como se acordó.** Nada con rostros en el repositorio, consentimientos firmados, videos de ajuste y de evaluación separados.
6. **La demo se ensaya.** En el equipo real, con tiempo para corregir.

## Vocabulario mínimo

| Término | Qué significa aquí |
|---|---|
| Despliegue | Llevar el sistema a donde se va a usar. En este proyecto, la computadora de la demo |
| Contrato o interfaz | Acuerdo sobre qué recibe y qué entrega un módulo |
| Integración | Juntar los módulos y comprobar que funcionan como conjunto |
| Prueba unitaria | Programa pequeño que comprueba una función con una entrada cuya salida correcta se conoce |
| Regresión | Algo que funcionaba y dejó de funcionar por un cambio posterior. Las pruebas existen para detectarlo |
| Verificación | Comprobar que un algoritmo propio da lo mismo que una implementación de referencia |
| Evaluación | Medir qué tan bien cumple el sistema su objetivo con datos anotados |
| Etiqueta de versión | Nombre fijo para un punto exacto del código (`v1.0`) |
| Congelar | Dejar de agregar funciones. Solo se corrigen errores |
| Trazabilidad | Poder decir con qué código, parámetros y datos se obtuvo un resultado |
| Gobernanza de datos | Reglas sobre qué datos hay, quién accede, para qué se usan y cuándo se borran |
| Ruta crítica | Las tareas que, si se atrasan, atrasan la entrega |

## Rutina

### Cada lunes, reunión de 15 minutos

Cada integrante responde tres preguntas:

1. ¿Qué terminaste? Se muestra funcionando, no se describe.
2. ¿Qué sigue?
3. ¿Qué te está frenando?

Después se marcan las casillas de `plan_de_trabajo.md` y se actualiza `decisiones.md` si algo cambió.

### Cada jueves, integración

Alguien baja `main`, instala, corre `python revisar.py` y después el sistema completo. Si algo no corre, arreglarlo es la prioridad de todos.

### En cada hito

Se revisa la lista "qué debe existir" del hito en `plan_de_trabajo.md`. Si falta algo, se decide ese mismo día qué se recorta, con el orden de recorte del mismo documento.

## Cuándo un módulo está terminado

Un módulo está terminado cuando cumple todo esto:

- [ ] Hace lo que dice el README de su carpeta.
- [ ] Entrega el tipo acordado.
- [ ] Sus parámetros están en `config.py` con la razón de cada valor.
- [ ] Tiene verificación contra OpenCV si es un algoritmo propio.
- [ ] Tiene al menos una prueba automática.
- [ ] Se midió cuánto tarda por cuadro.
- [ ] Su responsable puede explicar cada paso sin leer el código.
- [ ] Otra persona lo revisó y está en `main`.

La penúltima casilla importa tanto como las demás. La defensa vale 20% y el enunciado dice que el propósito es demostrar dominio de los principios, no solo tener una aplicación que funcione.

## Riesgos

| Riesgo | Señal temprana | Qué hacer |
|---|---|---|
| El seguimiento del rostro falla con la luz del salón | En pruebas con otra luz el puntaje de correlación se cae sin que la persona se mueva | Correlacionar sobre la banda laplaciana, ensayar en el salón, recalibrar al llegar |
| La medición de ojos no distingue abierto de cerrado | El F1 por cuadro sale debajo de 0.8, o los perfiles de gradiente se ven iguales en ambos casos | Revisar la franja de ojos, el suavizado y el tamaño del rostro normalizado antes de cambiar de método |
| El sistema va lento | Menos de 10 cuadros por segundo en la primera integración | Medir por etapa, reducir la ventana de búsqueda, bajar la resolución |
| Cerrar los ojos se confunde con voltear | Con el primer video real, el puntaje de la cabeza baja de 0.5 al cerrar los ojos | Ver D32: bajar el umbral de distracción o quitar los ojos de la plantilla |
| El código funciona con la cara dibujada pero no con personas | Los eventos del primer video real no coinciden con el guion | Es de esperarse en la primera prueba. Mirar la vista de depuración para ver qué pieza falla: caja, recortes de ojos o umbrales |
| Nadie del equipo entiende el código que ya está escrito | No pueden explicar un archivo de su frente | Cada frente lee sus archivos esta semana y los explica a otro. Si algo no se entiende, se simplifica |
| Un módulo se atrasa y bloquea a los demás | Dos reuniones seguidas sin mostrar nada funcionando | El simulador permite seguir sin ese módulo. Reasignar ayuda |
| Las piezas no embonan al juntarlas | Un módulo entrega algo distinto de `Medicion` | Integración temprana y revisión del contrato en cada pull request |
| Se suben datos personales por error | Aparece un archivo de video o un cuaderno pesado en un pull request | Revisar `git status` antes de cada commit. La lista de revisión lo incluye |
| Las métricas salen bien en ajuste y mal en evaluación | Diferencia grande entre los dos grupos de videos | Es información útil. Se reporta tal cual y se explica |
| Alguien no puede defender su módulo | No logra explicarlo en el ensayo | Sesión en pareja para repasarlo. Simplificar el código si hace falta |
| Los profesores responden D09 o D10 distinto a lo supuesto | Respuesta distinta a la propuesta | Ambas están aisladas en `config.py`. Se cambia un valor y se repiten las pruebas |
| No hay fecha oficial y llega antes de lo esperado | Aviso de los profesores | La meta interna del 2 de diciembre ya deja margen. Recortar según el orden del plan |

## Qué preguntarle a cada frente

Cuando no sepas cómo va un frente, estas preguntas lo aclaran sin necesidad de leer su código:

- **Frente 1 (rostro).** ¿Qué pasa con la caja cuando volteo y regreso? ¿Cuánto tarda en reencontrar el rostro? ¿Cuánto baja el puntaje si apagamos una luz?
- **Frente 2 (ojos).** Enséñame el perfil de gradiente con el ojo abierto y con el ojo cerrado. ¿Qué apertura da con lentes?
- **Frente 3 (boca y cabeza).** ¿Qué apertura da la boca al hablar y al bostezar? ¿La correlación de fase recupera un desplazamiento que tú pusiste a mano?
- **Frente 4 (temporal).** ¿Qué prueba cubre el cierre de exactamente 0.5 s? ¿Qué pasa con PERCLOS en los primeros 30 s?

## Preguntas que te toca responder

Estas son decisiones tuyas o del equipo que siguen abiertas. Conforme las respondas, se anotan en `decisiones.md`.

1. **¿Quién toma cada frente?** (D22) El equipo lo decide. Los cuatro frentes están en `plan_de_trabajo.md`.
2. **¿En qué computadora y con qué cámara se presenta?** (D24) ¿Hay una segunda computadora de respaldo? Conviene decidirlo antes de grabar, porque los videos deben grabarse con esa cámara o una parecida.
3. **¿Cuántas horas por semana puede dedicar cada integrante?** Si son pocas, se aplica desde ahora el orden de recorte.
4. **¿El reporte se escribe en Overleaf con la plantilla de las prácticas?**
5. **¿Quién edita el video demostrativo?**
6. **¿Grabará alguien fuera del equipo?** Si es así, firma el mismo consentimiento.

Ya respondidas el 16 de noviembre: lenguaje (D06, Python), carpeta de videos (D20, Google Drive), consentimiento de los cuatro (D27) y modelos de IA (D03, no se usan).

## Preguntas para los profesores

Conviene enviarlas juntas esta semana.

1. ¿PERCLOS debe incluir los parpadeos normales de hasta 0.5 s, o solo los cierres más largos? (D09)
2. ¿Las bandas de distracción son intervalos que empiezan en 0.5, 1.0, 1.5 y 2.0 s, y los giros menores a 0.5 s no se cuentan? (D10)
3. ¿Hay una duración mínima para contar un bostezo? (D11)
4. ¿Es aceptable que el sistema se calibre con la persona al inicio de cada sesión?
5. ¿Cuenta como algoritmo propio la correlación de fase si la transformada de Fourier se calcula con NumPy?
6. ¿Cuál es la fecha de entrega y de la demostración?
7. ¿Cómo quieren recibir el software: archivo zip o acceso al repositorio?
8. ¿Cuándo entregan los videos de prueba y tienen alguna restricción de uso?
9. ¿Es obligatorio usar los dos datasets de Kaggle, o son un apoyo? (D26)
10. ¿Cómo serán los videos de prueba? ¿De frente con webcam, o dentro de un auto como las imágenes de bostezo de Kaggle? ¿Se permite que quien opera el sistema marque el rostro en el primer cuadro? (D29)
