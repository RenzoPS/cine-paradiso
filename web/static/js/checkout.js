function formatear(total) {
    const minutos = String(Math.floor(total / 60)).padStart(2, '0');
    const segundos = String(total % 60).padStart(2, '0');
    return `${minutos}:${segundos}`;
}

function iniciarAviso(aviso) {
    const contador = aviso.querySelector('.checkout-contador');
    const contenedor = aviso.closest('.mis-entradas-card') || document;
    const botonConfirmar = contenedor.querySelector('[data-confirmar]');
    const fin = Date.now() + Number(aviso.dataset.segundos) * 1000;

    function actualizar() {
        const restantes = Math.max(0, Math.round((fin - Date.now()) / 1000));

        if (restantes === 0) {
            aviso.textContent = 'La reserva venció';
            if (botonConfirmar) {
                botonConfirmar.disabled = true;
            }
            clearInterval(intervalo);
            return;
        }

        contador.textContent = formatear(restantes);
    }

    const intervalo = setInterval(actualizar, 1000);
    actualizar();
}

function iniciarContador() {
    const avisos = document.querySelectorAll('.checkout-aviso[data-segundos]');
    avisos.forEach(iniciarAviso);
}

iniciarContador();