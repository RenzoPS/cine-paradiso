from cine_paradiso_web.services.api_service import llamar_api


def obtener_dashboard() -> dict:
    return llamar_api(
        'GET',
        'dashboard',
    )
