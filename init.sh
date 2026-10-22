#!/usr/bin/env bash
# ./init.sh instala y levanta todo; ./init.sh --instalar solo instala.

set -euo pipefail

cd "$(dirname "$0")"

paso() { echo; echo "==> $1"; }
ok() { echo "    ok: $1"; }
error() { echo "    ERROR: $1" >&2; exit 1; }

paso "Verificando requisitos"
command -v python3 > /dev/null || error "Falta Python 3. Instalalo y volvé a correr el script."
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || error "Hace falta Python 3.10 o superior. Tenés $(python3 --version)."
ok "$(python3 --version)"
command -v docker > /dev/null || error "Falta Docker. Instalalo o levantá MySQL a mano (ver README)."
docker compose version > /dev/null || error "Falta Docker Compose."
ok "$(docker compose version)"

paso "Configurando el .env"
if [ -f .env ]; then
    ok "ya existe, no se toca"
else
    cp .env.example .env
    ok "creado a partir de .env.example"
fi

paso "Creando el entorno virtual en .venv"
if [ -d .venv ]; then
    ok "ya existe"
else
    python3 -m venv .venv || error "No se pudo crear. En Debian/Ubuntu: sudo apt install python3-venv"
    ok "creado"
fi

paso "Instalando dependencias de la API y de la web"
.venv/bin/python -m pip install --upgrade pip > /dev/null
.venv/bin/python -m pip install -r api/requirements.txt -r web/requirements.txt
ok "dependencias instaladas"

if [ "${1:-}" = "--instalar" ]; then
    paso "Listo. Para levantar todo: ./init.sh"
    exit 0
fi

paso "Levantando MySQL en Docker (la primera vez tarda porque carga init.sql y catalogo.sql)"
docker compose up -d --wait db || error "MySQL no arrancó. Mirá el detalle con: docker compose logs db"
ok "MySQL listo"

trap 'trap - EXIT INT TERM; echo; echo "==> Frenando la API y la web"; kill 0' EXIT INT TERM

paso "Levantando la API y la web"
.venv/bin/python api/app.py &
.venv/bin/python web/app.py &

API_PORT=$(grep -E '^API_PORT=' .env | cut -d= -f2)
WEB_PORT=$(grep -E '^WEB_PORT=' .env | cut -d= -f2)
ok "API: http://localhost:${API_PORT:-5000}/cine_paradiso_api"
ok "Web: http://localhost:${WEB_PORT:-5001}"
echo "    Ctrl+C para frenar"

wait -n
