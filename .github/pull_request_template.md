## Tarea

<!-- Link a la tarjeta de Trello. Sin tarjeta no hay PR -->

## Qué cambia

<!-- Qué hiciste y por qué, en dos o tres líneas -->

## Cómo probarlo

<!-- Endpoint, pantalla o pasos para verificar que anda -->

## Checklist

- [ ] La rama sale de `develop` y el PR apunta a `develop`
- [ ] Probé los cambios con la base levantada
- [ ] Sin ORM, sin fetch/axios en el navegador, sin variables globales
- [ ] SQL con parámetros (`:nombre`), nunca con f-strings
- [ ] Si toqué la base: actualicé `init.sql` o `catalogo.sql`
- [ ] Si agregué o cambié un endpoint: actualicé `api/docs/swagger.yaml`
- [ ] No subo `.env`, `.venv/` ni `__pycache__/`
