-- Modulo 06 - Servicios
SET NAMES utf8mb4;

USE cine_paradiso;

CREATE TABLE IF NOT EXISTS servicio (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100)  NOT NULL,
    descripcion VARCHAR(255)  NULL,
    precio      DECIMAL(10,2) NOT NULL CHECK (precio > 0),
    imagen_url  VARCHAR(255)  NULL,
    activo      TINYINT(1)    NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Datos de ejemplo (van en el seed)
INSERT INTO servicio (nombre, descripcion, precio, imagen_url, activo) VALUES
    ('Combo Mega', 'Balde de pochoclos gigante + 2 gaseosas medianas', 12000.00, NULL, 1),
    ('Buffet Bar', 'Hamburguesas, panchos, snacks y bebidas variadas', 8500.00, NULL, 1),
    ('Pase Estacionamiento', 'Estadia cubierta de 3 horas en predio cerrado', 5000.00, NULL, 1),
    ('Acceso VIP Lounge', 'Espera exclusiva en sala VIP con sillones y Wi-Fi', 6000.00, NULL, 1);

-- PENDIENTE: activar cuando exista la tabla `compra` (modulo 05).
-- El precio queda como snapshot: cambiar servicio.precio no altera compras anteriores.
--
-- CREATE TABLE IF NOT EXISTS compra_servicio (
--     id              INT AUTO_INCREMENT PRIMARY KEY,
--     compra_id       INT           NOT NULL,
--     servicio_id     INT           NOT NULL,
--     cantidad        INT           NOT NULL CHECK (cantidad > 0),
--     precio_unitario DECIMAL(10,2) NOT NULL,
--     UNIQUE KEY uq_compra_servicio (compra_id, servicio_id),
--     CONSTRAINT fk_cs_compra   FOREIGN KEY (compra_id)   REFERENCES compra(id),
--     CONSTRAINT fk_cs_servicio FOREIGN KEY (servicio_id) REFERENCES servicio(id)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
