# `reporte/`

Aquí se organiza el reporte técnico (25% de la calificación) y el video demostrativo.

El texto del reporte se escribe en Overleaf con la plantilla de las prácticas. En esta carpeta va lo que conviene tener versionado junto al código.

```
reporte/
├── README.md          este archivo
├── figuras/           gráficas y diagramas sin rostros
└── guion_video.md     guion del video demostrativo
```

Las figuras que muestren un rostro se guardan solo en Overleaf, y solo de integrantes que lo autorizaron en su consentimiento.

## Estructura del reporte

El enunciado pide: introducción, descripción de los algoritmos, fundamentos matemáticos, metodología de implementación, pruebas experimentales, resultados, análisis de desempeño y conclusiones.

| Sección | Contenido | De dónde sale | Quién |
|---|---|---|---|
| 1. Introducción | Problema, enfoque por visión, alcance del sistema | Enunciado y `docs/arquitectura.md` | Margarita |
| 2. Arquitectura | Las dos capas, el diagrama, el recorrido de un cuadro | `docs/arquitectura.md` | Margarita |
| 3. Algoritmos y fundamentos | Una subsección por algoritmo propio: qué hace, sus ecuaciones, por qué se eligió, sus parámetros | `somnolencia/percepcion/README.md` y las prácticas | Cada frente los suyos |
| 4. Capa temporal | Estados, rastreador, PERCLOS, alertas, con los umbrales y su origen | `somnolencia/temporal/README.md`, `docs/decisiones.md` | Frente 4 |
| 5. Metodología de implementación | Organización en módulos, contrato entre ellos, vectorización, calibración | `docs/arquitectura.md` | Frente 4 |
| 6. Datos | Datasets, videos propios, división ajuste y evaluación, anotación, consentimiento | `docs/datos_y_gobernanza.md` | Margarita |
| 7. Pruebas experimentales | Los cuatro niveles de evaluación y cómo se hizo cada uno | `docs/evaluacion.md` | Frente 4 |
| 8. Resultados | Las tablas llenas | `evaluacion/resultados/` | Todos |
| 9. Análisis de desempeño | Tiempos por etapa, compromisos entre resolución, velocidad y exactitud | `evaluacion/desempeno.py` | Frente 1 |
| 10. Limitaciones | La ficha del sistema | `docs/algoritmos_y_modelos.md` | Margarita |
| 11. Conclusiones | Qué funcionó, qué no y qué se haría distinto | | Todos |
| Apéndice | Instrucciones de instalación y ejecución | `docs/despliegue_y_demo.md` | Frente 4 |

### Qué debe tener cada subsección de algoritmo

Para que las siete queden parejas:

1. Para qué se usa en el sistema.
2. Fundamento matemático, con sus ecuaciones.
3. Cómo se implementó y cómo se hizo eficiente.
4. Parámetros y por qué tienen ese valor.
5. Verificación contra OpenCV: tabla y una figura.
6. Una imagen del resultado dentro del sistema, tomada de la vista de depuración.

El enunciado da especial importancia a la interpretación de resultados y a los compromisos entre complejidad, calidad y velocidad. Cada subsección cierra con una o dos frases sobre eso.

### Puntos que el reporte debe decir de forma explícita

- Qué funciones de biblioteca se usaron y por qué (tabla de `docs/algoritmos_y_modelos.md`). El enunciado lo pide.
- Que ningún umbral se ajustó con los videos de evaluación.
- Que la etiqueta de microsueño describe ojos cerrados, no sueño confirmado.
- Con cuántas personas y en qué condiciones se probó.
- Los casos donde el sistema falla, con ejemplos.

## `guion_video.md`

**Aquí debe ir** el guion del video demostrativo, de 3 a 5 minutos, que muestra las operaciones principales y la modificación interactiva de parámetros.

Propuesta de estructura:

| Tiempo | Qué se muestra |
|---|---|
| 0:00 a 0:20 | Qué problema resuelve y cómo está organizado el sistema |
| 0:20 a 0:50 | Calibración en dos pasos |
| 0:50 a 1:40 | Vista de depuración: pirámide, seguimiento, rostro normalizado, perfiles de gradiente |
| 1:40 a 2:30 | Parpadeo normal, cierre con aviso, cierre largo con alerta crítica |
| 2:30 a 3:00 | Bostezo. Hablar no lo dispara |
| 3:00 a 3:30 | Giro de cabeza y bandas de distracción |
| 3:30 a 4:00 | PERCLOS subiendo de nivel |
| 4:00 a 4:40 | Cambio de un umbral con el deslizador y su efecto |
| 4:40 a 5:00 | Resultados principales y limitaciones |

El video muestra rostros, así que no se sube al repositorio. Se entrega por el medio que indiquen los profesores.

## Hecho cuando

- El reporte compila sin errores y cada tabla de resultados dice con qué versión del código se obtuvo.
- Alguien que no escribió una sección la leyó completa y la entendió.
- El video dura entre 3 y 5 minutos y muestra un parámetro cambiando en vivo.
