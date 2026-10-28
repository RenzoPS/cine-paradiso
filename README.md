# Cine Paradiso

Sistema de venta de entradas para Cine Paradiso: una cadena de 3 locales con
salas de distintas capacidades que proyecta películas clásicas. Incluye la
cartelera, la compra de entradas y servicios con QR por mail, y un backoffice
para administrar películas, funciones y servicios, validar el ingreso y ver
dashboards.

Proyecto integrador de Introducción al Desarrollo de Software (FIUBA),
cátedra Lanzillotta, 2.º cuatrimestre 2026.

## Integrantes

| Nombre | Padrón | GitHub |
|--------|--------|--------|
| Alvaro | _completar_ | [@Alvaro17-max](https://github.com/Alvaro17-max) |
| Gabi | _completar_ | [@gsaavedrag-bot](https://github.com/gsaavedrag-bot) |
| Ivan Angulo Farias | 107047 | [@ivan-af9](https://github.com/ivan-af9) |
| Luis Gerardo Zambrano Vera | 97605 | [@luiszambrano-dev](https://github.com/luiszambrano-dev) |
| Martin Alejandro Campuzano Jorquera | 115327 | [@martin-bits](https://github.com/martin-bits) |
| Nicole Gómez Uriol | _completar_ | [@nicolealison](https://github.com/nicolealison) |
| Renzo Piris Saporito | 116276 | [@RenzoPS](https://github.com/RenzoPS) |
| Sami | _completar_ | [@shadigonsalezazanero-debug](https://github.com/shadigonsalezazanero-debug) |
| Valentina Rivarola | 115957 | [@vrivarolaa](https://github.com/vrivarolaa) |

## Herramientas

| Componente | Uso | Versión |
|------------|-----|---------|
| Python | API y web | 3.10 o superior |
| Flask | API REST (JSON) y web (templates Jinja) | 3.1.3 |
| SQLAlchemy (solo Core, sin ORM) | Conexión y ejecución de SQL escrito a mano con `text()` | 2.1.5 |
| mysql-connector-python | Driver de MySQL que usa SQLAlchemy | 26.7.0 |
| requests | Comunicación del web con la API | 2.34.2 |
| python-dotenv | Lectura del `.env` | 1.2.4 |
| MySQL | Base de datos | 8 (imagen `mysql:8`) |
| Docker Compose | Levantar MySQL sin instalarlo | v2 o superior |

Las versiones de Python están fijadas en `api/requirements.txt` y
`web/requirements.txt`.

## Arquitectura

```
navegador  ──HTML──>  web (Flask + Jinja, :5001)  ──requests/JSON──>  API (Flask, :5000)  ──SQL──>  MySQL (:3306)
```

- La **API** expone recursos REST en JSON bajo `/cine_paradiso_api`.
- El **web** es otra app Flask que arma las páginas con templates Jinja y le
  pide los datos a la API con `requests`, desde Python.
- El navegador nunca habla con la API: la consigna prohíbe `fetch`, `axios` y
  `XMLHttpRequest`. El JavaScript del front es solo para interacción visual.
- Sin ORM: el SQL se escribe a mano en `repositories/`. SQLAlchemy se usa
  solo para la conexión y para ejecutar ese SQL con `text()`, sin modelos ni
  clases que mapeen tablas.

## Cómo levantarlo

### Opción rápida: `init.sh` (Linux, macOS, WSL)

Requisitos: Python 3.10+, Docker y Docker Compose.

```bash
git clone https://github.com/RenzoPS/cine-paradiso.git
cd cine-paradiso
./init.sh
```

El script va mostrando cada paso:

1. Verifica Python y Docker.
2. Crea el `.env` a partir de `.env.example`, si no existe.
3. Crea el entorno virtual `.venv` e instala las dependencias de la API y del web.
4. Levanta MySQL en Docker y espera a que termine de cargar el esquema.
5. Levanta la API y el web.

Con `./init.sh --instalar` solo instala, sin levantar nada. `Ctrl+C` frena la
API y el web; la base queda corriendo (`docker compose stop` para frenarla).

| Qué | URL |
|-----|-----|
| Web | http://localhost:5001 |
| Backoffice | http://localhost:5001/admin |
| API | http://localhost:5000/cine_paradiso_api |

### Paso a paso (o en Windows)

```bash
cp .env.example .env              # Windows: copy .env.example .env
docker compose up -d --wait db

python3 -m venv .venv             # Windows: python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r api/requirements.txt -r web/requirements.txt
```

Después, en dos terminales con el entorno activado:

```bash
python api/app.py
python web/app.py
```

### Sin Docker

Con un MySQL 8 instalado localmente, cargar los scripts en orden y ajustar los
datos de conexión en el `.env`:

```bash
mysql -u root -p < api/db/init.sql       # crea la base cine_paradiso y las tablas
mysql -u root -p < api/db/catalogo.sql   # carga los datos fijos del sistema
```

### Si cambia el esquema

MySQL ejecuta `init.sql` y `catalogo.sql` **solo la primera vez**, cuando crea el
volumen. Si alguien mergea un cambio en esos archivos, hay que recrear la base
(borra los datos locales):

```bash
docker compose down -v && docker compose up -d --wait db
```

### Si algo falla

| Error | Solución |
|-------|----------|
| `ensurepip is not available` | Debian/Ubuntu: `sudo apt install python3-venv` |
| `externally-managed-environment` | Estás instalando fuera del `.venv`. Activalo primero |
| `port is already allocated` en el 3306 | Ya tenés otro MySQL corriendo. Cambiá `DB_PORT` en el `.env` |

## Estructura

```
cine-paradiso/
├── init.sh                      instala y levanta todo
├── docker-compose.yml           MySQL con el esquema y los datos iniciales
├── .env.example                 variables de entorno (copiar como .env)
├── docs/                        mockups e informe
├── api/
│   ├── app.py                   arranque de la API, registra los blueprints
│   ├── requirements.txt
│   ├── db/
│   │   ├── init.sql             script de creación: base y tablas
│   │   └── catalogo.sql         script de carga: datos fijos del sistema
│   ├── docs/swagger.yaml        contrato de la API (OpenAPI 3)
│   └── cine_paradiso_api/
│       ├── constants.py         configuración, formatos y códigos de error
│       ├── utils.py             ErrorAPI y validaciones comunes
│       ├── paginacion.py        _limit, _offset y enlaces de los listados
│       ├── routes/              endpoints HTTP (blueprints)
│       ├── validators/          validación del input
│       ├── services/            lógica de negocio
│       └── repositories/        SQL; __init__.py tiene la conexión y las primitivas
└── web/
    ├── app.py                   arranque del web, registra los blueprints
    ├── requirements.txt
    ├── templates/               templates Jinja (base.html, páginas por recurso)
    │   └── components/          piezas reutilizables con {% include %}
    ├── static/
    │   ├── css/
    │   ├── js/                  solo interacción visual, nunca llamadas a la API
    │   └── images/
    └── cine_paradiso_web/
        ├── constants.py         configuración, incluida la URL de la API
        ├── routes/              páginas (blueprints)
        └── services/            llamadas a la API con requests
```

Un archivo por recurso en cada capa. El flujo de una request es:

```
web:  routes/  ->  services/  ──requests──>  api:  routes/  ->  services/  ->  repositories/
      (página)     (pide a la API)                  (HTTP)      (negocio)       (SQL)
```

## Endpoints

Todos cuelgan de `/cine_paradiso_api`. El contrato completo está en
[`api/docs/swagger.yaml`](api/docs/swagger.yaml), que se puede ver en
[editor.swagger.io](https://editor.swagger.io) o con la extensión "Swagger
Viewer" de VS Code.

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| POST | `/auth/registro` | Alta de cliente | Público |
| POST | `/auth/login` | Devuelve un token firmado con el rol y la expiración | Público |
| GET | `/usuarios/me` | Datos del usuario logueado | Cliente |
| PUT | `/usuarios/me` | Editar los datos propios | Cliente |
| GET | `/usuarios/me/historial` | Consumos (entradas y servicios) y películas vistas | Cliente |
| GET | `/usuarios` | Listado de usuarios | Admin |
| PATCH | `/usuarios/{id_usuario}/rol` | Dar o quitar el rol de admin | Admin |
| GET | `/peliculas/tmdb?q=` | Busca películas en TMDB | Admin |
| POST | `/peliculas` | Importa una película de TMDB por `tmdb_id`, con géneros y póster | Admin |
| GET | `/peliculas` | Listado de películas. Con `?en_cartel=true` es la cartelera; filtros por local, fecha y género | Público |
| GET | `/peliculas/{id_pelicula}` | Detalle: sinopsis, póster, duración y clasificación | Público |
| PUT | `/peliculas/{id_pelicula}` | Editar sinopsis, póster, clasificación y período en cartel | Admin |
| DELETE | `/peliculas/{id_pelicula}` | Baja lógica | Admin |
| GET | `/generos` | Géneros disponibles | Público |
| GET | `/locales` | Listado de locales | Público |
| POST | `/locales/{id_local}/salas` | Alta de una sala en un local | Admin |
| PUT | `/salas/{id_sala}` | Editar una sala | Admin |
| POST | `/salas/{id_sala}/butacas` | Genera la grilla de butacas (filas × columnas) | Admin |
| GET | `/salas/{id_sala}/butacas` | Butacas y capacidad de la sala | Admin |
| GET | `/funciones` | Funciones disponibles, con filtros por película, local y fecha | Público |
| GET | `/funciones/{id_funcion}` | Detalle de una función: película, sala, local, fecha y precio | Público |
| POST | `/funciones` | Programar una función | Admin |
| PUT | `/funciones/{id_funcion}` | Editar una función | Admin |
| DELETE | `/funciones/{id_funcion}` | Baja de una función sin ventas | Admin |
| GET | `/funciones/{id_funcion}/butacas` | Mapa de butacas de la función: libres y ocupadas | Público |
| GET | `/servicios` | Servicios activos | Público |
| POST | `/servicios` | Alta de un servicio | Admin |
| PUT | `/servicios/{id_servicio}` | Modificar un servicio | Admin |
| DELETE | `/servicios/{id_servicio}` | Baja lógica de un servicio | Admin |
| POST | `/compras` | Reserva butacas y crea la compra `pendiente`. 409 si alguna ya se ocupó | Cliente |
| GET | `/compras` | Compras del usuario logueado | Cliente |
| GET | `/compras/{id_compra}` | Detalle de una compra | Cliente |
| DELETE | `/compras/{id_compra}` | Abandonar una compra pendiente y liberar las butacas | Cliente |
| PUT | `/compras/{id_compra}/servicios` | Servicios y cantidades de una compra pendiente | Cliente |
| POST | `/compras/{id_compra}/confirmar` | Pasa la compra a `pagada`, genera la factura y envía el mail con el QR | Cliente |
| GET | `/compras/{id_compra}/factura` | Datos de la factura | Cliente |
| GET | `/compras/{id_compra}/qr` | Imagen PNG del QR | Cliente |
| POST | `/compras/{id_compra}/cancelar` | Cancela si está dentro del plazo y libera las butacas | Cliente |
| POST | `/compras/validar` | Valida el QR en el ingreso a la sala y marca la compra como `usada` | Admin |
| GET | `/estadisticas/ocupacion?por=funcion\|pelicula` | Ocupación por función o por película | Admin |
| GET | `/estadisticas/ventas-por-genero` | Ventas por género | Admin |
| GET | `/estadisticas/franjas-horarias` | Franjas horarias más vendidas | Admin |
| GET | `/estadisticas/cancelaciones` | Cancelaciones por período y por película | Admin |

Todos los endpoints tienen seguridad: los públicos piden la API key del web,
y los de cliente y admin, además, el token del login. Sin token o con el token
vencido responden 401, y si el rol no alcanza, 403.

Si un endpoint cambia al implementarlo, se actualiza acá en el mismo PR.

El esquema de tablas está en [`docs/esquema-de-tablas.png`](docs/esquema-de-tablas.png)
(fuente editable en `docs/esquema-de-tablas.drawio`, se abre en
[app.diagrams.net](https://app.diagrams.net)).

Los listados admiten `_limit` (entre 1 y 100, por defecto 10) y `_offset`
(mayor o igual a cero, por defecto 0), y devuelven los datos bajo una clave
descriptiva junto a `_total` y un objeto `_links` con `_first`, `_prev`,
`_next` y `_last`.

Las fechas viajan en ISO 8601 con desplazamiento fijo de GMT-3:
`2026-11-18T20:30:00-03:00`.

### Formato de error

```json
{
  "errors": [
    {
      "code": "invalid.min.value",
      "message": "Valor por debajo del minimo permitido",
      "level": "error",
      "description": "El parametro '_limit' debe ser mayor o igual a 1. Se recibio: 0"
    }
  ]
}
```

## Hitos

| Hito | Fecha | Entrega |
|------|-------|---------|
| 1 | 26/10 | Supuestos, alcance, backlog, mockups, esquema de tablas, endpoints y repositorio |
| 2 | 02/11 | Endpoints desarrollados, tablas SQL y templates |
| 3 | 09/11 | Integración front y back, login y acceso al backoffice |
| 4 | 18/11 | Primera versión funcional |
| 5 | 25/11 | Primera entrega y defensa |
| 6 | 30/11 | Defensas y consultas |
| 7 | 02/12 | Segunda entrega y defensa |

## Cómo trabajar en este repo

Ver [CONTRIBUTING.md](CONTRIBUTING.md).
