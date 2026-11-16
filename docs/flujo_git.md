# Flujo de trabajo con Git

Este documento supone que no todos han usado Git. Quien ya lo domina puede saltar a "Reglas del equipo".

## La idea en un párrafo

Git guarda la historia del código. GitHub guarda una copia en línea que todos comparten. La versión oficial es la rama `main`. Nadie trabaja directo sobre `main`: cada tarea se hace en una rama aparte, que es una copia de trabajo, y cuando está lista se pide a otra persona que la revise antes de unirla. Esa petición se llama pull request.

## Preparación, una sola vez

### Para quien crea el repositorio (Margarita)

1. En GitHub, crear un repositorio nuevo llamado `somnolencia-vision`, **privado**, sin README ni `.gitignore` (ya vienen en este esqueleto).
2. En la terminal, dentro de la carpeta del esqueleto:

```bash
git init
git add .
git status          # revisar que no aparezca nada raro en la lista
git commit -m "Esqueleto del proyecto y documentación"
git branch -M main
git remote add origin <URL del repositorio>
git push -u origin main
```

3. En GitHub, en la configuración del repositorio, sección de colaboradores, invitar a los tres integrantes.
4. Si la cuenta lo permite, activar la protección de la rama `main` para exigir una revisión antes de unir. En repositorios privados esa opción depende del plan de GitHub. Si no está disponible, la regla se cumple de palabra.

### Para todos

```bash
git config --global user.name "Nombre Apellido"
git config --global user.email "correo con el que entras a GitHub"
git clone <URL del repositorio>
cd somnolencia-vision
```

Si la terminal pide contraseña y la rechaza: GitHub no acepta la contraseña de la cuenta desde la terminal. Lo más sencillo es instalar GitHub Desktop, iniciar sesión ahí y clonar desde esa aplicación. Todo lo que sigue también se puede hacer con sus botones.

## Trabajo diario

### 1. Empezar una tarea

```bash
git switch main
git pull                              # traer lo último
git switch -c ojos/gradiente-vertical # crear la rama de la tarea
```

El nombre de la rama es `modulo/descripcion-corta`. Ejemplos: `rostro/calibracion`, `temporal/perclos`, `docs/inventario-kaggle`.

### 2. Guardar avances

```bash
git status                            # ver qué cambió
git add somnolencia/percepcion/gradiente.py
git commit -m "Agrega gradiente vertical con núcleo de Sobel"
```

Se agregan archivos por nombre. Antes de cada `commit` se lee la lista de `git status`. Si aparece un video, una imagen o un cuaderno con salidas, no se agrega.

Los mensajes dicen qué hace el cambio, en una línea: "Agrega...", "Corrige...", "Cambia...".

### 3. Subir la rama

```bash
git push -u origin ojos/gradiente-vertical
```

La primera vez lleva `-u origin nombre-de-la-rama`. Después basta `git push`.

### 4. Pedir revisión

En GitHub aparece un botón para abrir un pull request desde la rama recién subida. En la descripción se escribe:

- Qué hace el cambio.
- Cómo se probó.
- Qué paso del plan de trabajo cubre.

Se elige a un integrante como revisor.

### 5. Revisar

Quien revisa comprueba la lista de abajo, deja comentarios si algo falta y aprueba cuando está bien. Después se une con el botón "Merge" y se borra la rama.

### 6. Volver a empezar

```bash
git switch main
git pull
```

## Lista de revisión de un pull request

- [ ] Hace lo que dice el README de su carpeta.
- [ ] Respeta el contrato: los módulos de percepción entregan `Medicion`.
- [ ] No hay números sueltos en el código. Los umbrales están en `config.py`.
- [ ] Si es un algoritmo propio, trae su verificación contra OpenCV.
- [ ] Las pruebas pasan (`pytest`).
- [ ] No hay videos, imágenes de rostros ni cuadernos con salidas.
- [ ] Quien revisa entendió el código. Si no lo entendió, se pide una explicación o comentarios. Todos deben poder defenderlo.

## Situaciones comunes

### Mi rama se quedó atrás de main

```bash
git switch main
git pull
git switch ojos/gradiente-vertical
git merge main
```

### Git dice que hay conflicto

Pasa cuando dos personas cambiaron las mismas líneas. Git marca el archivo así:

```
<<<<<<< HEAD
lo que tengo yo
=======
lo que hay en main
>>>>>>> main
```

Se edita el archivo para dejar la versión correcta, se borran las tres líneas de marcas y después:

```bash
git add archivo_con_conflicto.py
git commit -m "Resuelve conflicto con main"
```

Si no queda claro cuál versión es la buena, se pregunta a quien escribió la otra. Los conflictos son raros si cada frente toca solo sus archivos.

### Hice commit de algo por error y todavía no hago push

```bash
git reset --soft HEAD~1     # deshace el último commit y conserva los cambios
```

### Subí un video o una imagen con rostros

Avisar a Margarita de inmediato. Borrarlo en un commit nuevo no lo quita del historial.

## Reglas del equipo

1. Nadie hace `push` directo a `main`.
2. Ramas cortas: una tarea, uno o dos días. Es mejor unir seguido que acumular una semana de cambios.
3. Cada frente edita solo sus archivos. Si hay que tocar el de otro frente, se avisa.
4. `config.py` y `tipos.py` los edita el frente 4. Si otro frente necesita un parámetro nuevo, lo pide o lo propone en su pull request.
5. Los cuadernos se suben sin salidas.
6. Nunca `git push --force` sobre `main`.
7. Todo pull request lo revisa alguien que no lo escribió.
