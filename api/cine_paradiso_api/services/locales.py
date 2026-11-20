from ..repositories import locales as db_locales


def listar_locales() -> dict:
    return {'locales': db_locales.listar_locales()}
