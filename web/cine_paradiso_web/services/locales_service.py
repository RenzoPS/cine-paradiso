from cine_paradiso_web.services.api_service import llamar_api


def listar_locales() -> dict:
    return llamar_api(
        'GET',
        'locales',
    )
