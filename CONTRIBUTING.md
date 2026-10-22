# Cómo trabajar en este repo

Guía para el equipo. Si nunca usaste git, seguí los pasos tal cual están.

## Reglas

1. **Nunca se pushea directo a `main` ni a `develop`.** Siempre rama + Pull Request.
2. `main` es lo que se entrega. Se trabaja sobre `develop`, y `develop` pasa a
   `main` antes de cada hito.
3. Antes de arrancar, SIEMPRE traer lo último de `develop`.
4. PR chico y temprano: apenas tengas un endpoint o una pantalla andando, abrilo.
5. Cada uno trabaja con su propia cuenta de GitHub. Se evalúa quién hizo qué.
6. Si algo no te cierra, preguntá en el grupo antes de inventar.

## Setup inicial (una sola vez)

```bash
git clone https://github.com/RenzoPS/cine-paradiso.git
cd cine-paradiso
./init.sh
```

Variantes para Windows y qué hacer si falla: [README](README.md#cómo-levantarlo).

Configurá tu nombre y el mail de tu cuenta de GitHub, si no lo hiciste nunca.
Si el mail no coincide, tus commits no te cuentan:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "el-mail-de-tu-cuenta@ejemplo.com"
```

## Ramas

| Rama | Para qué | Quién la toca |
|------|----------|---------------|
| `main` | Versión entregada en cada hito | Solo por PR desde `develop` |
| `develop` | Integración del trabajo de todos | Solo por PR desde tu rama |
| `tipo/descripcion` | Tu tarea | Vos |

Formato de tu rama: `tipo/descripcion-corta`, en
minúsculas y con guiones.

```
feat/mapa-de-butacas
fix/doble-reserva-de-butaca
docs/supuestos-hito-1
refactor/unificar-validaciones
```

Los tipos son los mismos que los de
los commits (abajo).

## Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/),
como pide la cátedra:

```
tipo(alcance): qué hiciste, en infinitivo
```

| Tipo | Cuándo |
|------|--------|
| `feat` | Funcionalidad nueva |
| `fix` | Corrección de un error |
| `refactor` | Cambio de código sin cambiar el comportamiento |
| `docs` | Documentación: README, swagger, informe, supuestos |
| `style` | CSS o formato, sin cambiar lógica |
| `test` | Pruebas |
| `chore` | Configuración, dependencias, scripts, Docker |

El alcance es el recurso o área que tocás: `auth`, `usuarios`, `peliculas`, `locales`, `salas`,
`funciones`, `cartelera`, `compras`, `servicios`, `qr`, `checkout`, `mails`,
`dashboards`, `db`, `front`, `infra`.

Bien:

```
feat(compras): agregar la reserva de butacas en una transacción
fix(funciones): rechazar funciones superpuestas en la misma sala
docs(swagger): documentar los endpoints de películas
refactor(front): extraer la tarjeta de película a un componente
```

Mal:

```
cambios
funca bien
mentira, ahora sí funca
feat: todo el tp
```

- Un commit por cambio con sentido: ni uno gigante al final, ni uno por línea.
- Dos commits no pueden tener el mismo mensaje.
- El mensaje tiene que decir qué cambió sin abrir el diff.

## El ciclo de trabajo

### 1. Traer lo último

```bash
git checkout develop
git pull origin develop
```

**Siempre**, antes de crear tu rama. Si trabajás sobre código viejo, después
el merge duele.

### 2. Crear tu rama

```bash
git checkout -b feat/mapa-de-butacas
```

### 3. Trabajar y commitear

```bash
git status                        # ver qué cambió
git add api/cine_paradiso_api/routes/compras.py   # sumar lo que corresponde
git commit -m "feat(compras): agregar GET /funciones/{id}/butacas"
```

Mirá el `git status` antes de `git add .`: si aparece algo que no tocaste a
propósito, no lo sumes.

### 4. Subir la rama

```bash
git push -u origin feat/mapa-de-butacas
```

La primera vez lleva `-u origin <rama>`. Después alcanza con `git push`.

### 5. Abrir el Pull Request

1. Entrá al repo en GitHub y hacé clic en **"Compare & pull request"**.
2. **Verificá que diga `base: develop` ← `compare: tu-rama`.** Si dice `base: main`, cambialo.
3. Título: igual que un commit. Por ejemplo, `feat(compras): mapa de butacas`.
4. En la descripción: qué cambia y cómo probarlo.
5. Pedile review a un compañero que no haya trabajado en ese cambio y avisá en el grupo.

### 6. Review

- Hace falta **1 aprobación** para mergear. No se aprueba el PR propio.
- Si te piden cambios, seguís en la misma rama, commiteás y pusheás. El PR se actualiza solo.
- Cuando está aprobado, el autor mergea con **"Create a merge commit"** (no
  squash, así queda cada commit con su autor) y borra la rama.

### 7. Después del merge

```bash
git checkout develop
git pull origin develop
```

Y arrancá la próxima rama desde ahí.

## Si aparece un conflicto

GitHub te va a decir *"This branch has conflicts that must be resolved"*.

**No toques nada y avisá en el grupo.** Un conflicto mal resuelto borra trabajo de otro.

Para evitarlos:

- `git pull origin develop` seguido, no una vez por semana.
- Trabajá en los archivos de tu tarea.
- Los archivos compartidos (`app.py`, `constants.py`, `init.sql`,
  `catalogo.sql`) se tocan poco y en PR chicos.

## Reglas de código

Estas reglas vienen de la consigna. Si se rompe alguna, se desaprueba.

- **Sin ORM.** Nada de SQLAlchemy ORM (`declarative_base`, `Session`, `Mapped`),
  SQLModel, Peewee ni clases que mapeen tablas. El SQL se escribe a mano en
  `repositories/` y se ejecuta con las primitivas de `repositories/__init__.py`,
  que usan SQLAlchemy Core solo para conectarse y ejecutar `text()`.
- **Sin `fetch`, `axios`, `XMLHttpRequest` ni promises en el navegador.** El web
  le pide datos a la API desde Python, con `requests`, en `services/`.
- **Sin variables globales** (`global`, listas o dicts globales que se modifican).
  Las constantes en MAYÚSCULAS en `constants.py` sí van.
- **Sin ciclos infinitos.**
- **Sin código repetido.** Si necesitás algo que ya está en otro archivo, se
  mueve a un lugar común y se reutiliza, no se copia.
- **Que no rompa ante el usuario.** Todo input se valida y todo error vuelve
  con un mensaje claro y el código HTTP que corresponde.
- **Fecha y hora en un solo `DATETIME`.**
- **Verbos HTTP correctos:** `GET` consulta, `POST` crea, `PUT`/`PATCH` modifica,
  `DELETE` borra. Respuestas en JSON con el código que corresponde (200, 201, 204,
  400, 401, 403, 404, 409).
- **Dos aplicaciones separadas.** `api/` y `web/` corren en procesos y puertos
  distintos, cada una con su `app.py`. Una sola app con todo junto desaprueba.

Y estas las pidió la cátedra en clase:

- **Blueprints desde el arranque, uno por dominio** (`peliculas.py`,
  `funciones.py`, `compras.py`), en la API y en el web. Un solo nivel, sin
  anidar. Un endpoint va en el blueprint del recurso del que sale: las entradas
  de una compra van en `compras`, no en `entradas`.
- **`url_for` siempre**, para los links entre páginas (con el nombre
  `blueprint.funcion`, no la ruta) y para los archivos de `static/`. Nunca rutas
  escritas a mano.
- **`base.html` + `{% extends %}`** para el esqueleto común, y lo que se repite
  (cards, botones, formularios) en `templates/components/` con `{% include %}`.
- **CSS en archivos de `static/css/`**, nada de `style="..."` ni `<style>`.
- **No se cambia la carpeta por defecto** de `templates/` ni de `static/`.
- **Sin frameworks de front** (React, Angular, Vue...) ni TypeScript. Bootstrap
  o Tailwind se pueden usar, pero hay que saber explicar cómo se integraron.
- **JavaScript solo para interacción visual:** `const`/`let` (nunca `var`),
  `===` en vez de `==`, y una variable no cambia de tipo.
- **No comentar línea por línea.** Un comentario explica el por qué de algo
  que no es obvio, no repite lo que dice el código.
- **Cada uno entiende el flujo completo.** En la defensa individual preguntan
  sobre lo que muestra tu GitHub y sobre cualquier parte de la app.

### SQL

Los valores van siempre como parámetros, nunca pegados al string:

```python
# Bien
ejecutar_consulta('SELECT id, titulo FROM peliculas WHERE id = :id', {'id': id_pelicula})

# Mal: inyección SQL
ejecutar_consulta(f'SELECT id, titulo FROM peliculas WHERE id = {id_pelicula}')
```

Si varias queries tienen que pasar todas juntas o ninguna (por ejemplo, una
compra con varias butacas), van dentro de `with transaccion() as conexion:`.

### Primitivas disponibles

No reinventes nada de esto en tu código:

| Dónde | Qué |
|-------|-----|
| `repositories/__init__.py` | `ejecutar_consulta`, `ejecutar_escalar`, `ejecutar_mutacion`, `transaccion`, `listar_paginado` |
| `paginacion.py` | `leer_parametros_paginacion`, `paginar` |
| `utils.py` | `ErrorAPI`, `validar_entero`, `validar_entero_positivo`, `validar_minimo`, `validar_maximo`, `validar_string_no_vacio`, `validar_email`, `validar_booleano`, `validar_opcion`, `validar_cuerpo_no_vacio`, `rechazar_campos_desconocidos`, `parsear_fecha_hora`, `parsear_fecha`, `formatear_fecha_hora` |

Un error de negocio se lanza con `ErrorAPI` desde cualquier capa y `app.py`
lo convierte en la respuesta JSON. Las routes no llevan `try/except`:

```python
raise ErrorAPI('pelicula.not.found', 'Pelicula no encontrada', f"No existe la pelicula '{id_pelicula}'", 404)
```

### Nombres

- Código, tablas, endpoints y templates en español y `snake_case`.
- Tablas y endpoints en plural: `peliculas`, `/funciones/{id_funcion}`.
- Handlers de la API con el verbo adelante: `get_peliculas`, `post_compra`.
- Funciones de services con verbo: `listar_peliculas`, `crear_compra`.
- Funciones de repositories según lo que hacen: `obtener_`, `insertar_`, `actualizar_`, `eliminar_`.

## Dónde va cada cosa

Un archivo por recurso en cada capa, con el nombre del recurso:

| Capa | API | Web |
|------|-----|-----|
| Endpoint o página | `api/cine_paradiso_api/routes/<recurso>.py` | `web/cine_paradiso_web/routes/<recurso>.py` |
| Validación | `api/cine_paradiso_api/validators/<recurso>.py` | |
| Negocio | `api/cine_paradiso_api/services/<recurso>.py` | `web/cine_paradiso_web/services/<recurso>.py` |
| SQL | `api/cine_paradiso_api/repositories/<recurso>.py` | |
| Templates | | `web/templates/<recurso>/`, y los componentes en `web/templates/components/` |
| Estilos y scripts | | `web/static/css/`, `web/static/js/`, `web/static/images/` |

```
routes/  ->  services/  ->  repositories/
 (HTTP)      (negocio)         (SQL)
```

Y en el mismo PR:

1. Registrar el blueprint en el `app.py` que corresponda.
2. Si hay tablas nuevas: `api/db/init.sql`, y si llevan datos fijos, `catalogo.sql`.
3. Documentar los endpoints en `api/docs/swagger.yaml` y en la tabla del README.

Si necesitás una dependencia nueva, agregala al `requirements.txt` que
corresponda con su versión exacta (`pip index versions <paquete>` te dice la
última) y avisá en el grupo, porque todos tienen que volver a correr `./init.sh`.

## Qué NO se commitea

Ya está en `.gitignore`, pero por las dudas:

- `.env`: configuración local, cada uno tiene el suyo.
- `.venv/`: miles de archivos, se regenera con `./init.sh`.
- `__pycache__/`: temporales de Python.
- Imágenes, PDFs o archivos que no son parte del proyecto.

Si ves alguno en `git status`, algo está mal. Avisá antes de commitear.
