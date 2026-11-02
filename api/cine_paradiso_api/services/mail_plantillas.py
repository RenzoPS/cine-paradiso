CONFIRMACION_COMPRA = """\
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tu compra en Cine Paradiso</title>
</head>
<body bgcolor="#f2f2f2">
    <table width="100%" bgcolor="#f2f2f2" cellpadding="16" border="0">
        <tr>
            <td align="center">
                <table width="600" bgcolor="#ffffff" cellpadding="16" border="1" bordercolor="#1e1e1e">
                    <tr>
                        <td align="center">
                            <font face="Arial, Helvetica, sans-serif" color="#1e1e1e">
                                <font size="6"><b>Cine Paradiso</b></font>
                                <hr>
                                <b>{{ pelicula }}</b><br>
                                {{ sala }}<br>
                                {{ fecha_hora }}<br>
                                {{ butacas }}
                                <br><br>
                                <img src="cid:qr" width="200" height="200" alt="Tu código QR" border="1"><br>
                                <font size="2" color="#777777">Preséntelo en la puerta</font>
                                <hr>
                                <table width="100%" cellpadding="8" border="0">
                                    <tr><td>Entradas x{{ cantidad_entradas }}</td><td align="right">$ {{ total_entradas }}</td></tr>
                                    <tr><td>Servicios</td><td align="right">$ {{ total_servicios }}</td></tr>
                                    <tr><td><b>TOTAL – Factura N° {{ numero_factura }}</b></td><td align="right"><b>$ {{ total }}</b></td></tr>
                                </table>
                                <hr>
                                <table cellpadding="12" border="1" bordercolor="#1e1e1e">
                                    <tr><td><a href="{{ link_cancelar }}">Cancelar entrada</a></td></tr>
                                </table>
                                <br>
                                <font size="2" color="#777777">Podés cancelar la entrada hasta {{ horas_limite }} horas antes de la función.</font>
                            </font>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""