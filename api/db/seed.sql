-- Datos fijos que el sistema necesita para funcionar. Se ejecuta después de init.sql.

SET NAMES utf8mb4;

USE cine_paradiso;

-- Los 3 locales y sus salas son fijos: no tienen ABM.
INSERT INTO locales (id_local, nombre, direccion) VALUES
(1, 'Cine Paradiso - Centro', 'Av. Corrientes 1234, CABA'),
(2, 'Cine Paradiso - Norte', 'Av. Cabildo 2800, CABA'),
(3, 'Cine Paradiso - Sur', 'Av. Montes de Oca 900, CABA');

INSERT INTO salas (id_sala, fk_id_local, nombre) VALUES
(1, 1, 'Sala 1'),
(2, 1, 'Sala 2'),
(3, 2, 'Sala Principal'),
(4, 3, 'Sala 1');

-- Butacas: una por fila y número. Cada sala tiene su capacidad.
INSERT INTO butacas (fk_id_sala, fila, numero)
SELECT s.id_sala, f.fila, n.numero
FROM salas s
JOIN (SELECT 'A' AS fila, 1 AS orden UNION ALL SELECT 'B', 2 UNION ALL SELECT 'C', 3 UNION ALL SELECT 'D', 4
      UNION ALL SELECT 'E', 5 UNION ALL SELECT 'F', 6 UNION ALL SELECT 'G', 7 UNION ALL SELECT 'H', 8) f
JOIN (SELECT 1 AS numero UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
      UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10
      UNION ALL SELECT 11 UNION ALL SELECT 12) n
JOIN (SELECT 1 AS id_sala, 8 AS filas, 12 AS por_fila   -- 96 butacas
      UNION ALL SELECT 2, 6, 10                         -- 60 butacas
      UNION ALL SELECT 3, 7, 10                         -- 70 butacas
      UNION ALL SELECT 4, 5, 8) capacidad               -- 40 butacas
  ON capacidad.id_sala = s.id_sala
WHERE f.orden <= capacidad.filas
  AND n.numero <= capacidad.por_fila;

-- Usuarios de prueba. Contraseñas: Admin1234 y Cliente1234.
INSERT INTO usuarios (id_usuario, nombre, apellido, email, contrasena_hash, rol) VALUES
(1, 'Admin', 'Sistema', 'admin@cineparadiso.com', 'scrypt:32768:8:1$LUKaLpz8wTbEoaBU$b8614f0ff4800761f3fbe38253bdc1b6479fbebbf4289c0740751c94fa5f5c6c14737e38638f4847f9386b9e86ee422f0616390731a6f1bf9e8f43eeaca857e1', 'admin'),
(2, 'Juan', 'Pérez', 'cliente@correo.com', 'scrypt:32768:8:1$92zeqQ3TOtnotvPy$f3136c54db78a3d4604df8e18ce9fd084f98e1c62d4ffeb254c0cd5ec1ac4ba02b55fe211de013032e1285282530d9a7c9c383f17c9b8f848827f7b8bc903109', 'cliente');

INSERT INTO servicios (id_servicio, nombre, descripcion, precio, activo) VALUES
(1, 'Combo pochoclos + gaseosa', 'Balde de pochoclos grande y gaseosa de 1 L', 3500.00, TRUE),
(2, 'Chocolate', 'Barra de chocolate semiamargo de 100 g', 1500.00, TRUE),
(3, 'Estacionamiento', 'Estacionamiento cubierto durante la función', 2500.00, TRUE),
(4, 'Acceso VIP', 'Sala de espera VIP con sillones y bebida de cortesía', 6000.00, TRUE);

-- Películas de ejemplo del catálogo.
INSERT INTO peliculas (id_pelicula, tmdb_id, titulo, sinopsis, poster_url, duracion_min, clasificacion, genero, disponible_desde, disponible_hasta) VALUES
(1, 11216, 'Cinema Paradiso', 'Un cineasta recuerda su infancia y su amistad con el proyeccionista del cine de su pueblo.', 'https://image.tmdb.org/t/p/w500/example.jpg', 155, 'ATP', 'Drama', '2026-12-01 00:00:00', '2027-12-31 23:59:59'),
(2, 238, 'El Padrino', 'La historia de la familia Corleone, una de las más poderosas de la mafia italoamericana.', 'https://image.tmdb.org/t/p/w500/example.jpg', 175, '+16', 'Crimen', '2026-12-01 00:00:00', '2027-12-31 23:59:59'),
(3, 280, 'Casablanca', 'En el Casablanca ocupado durante la Segunda Guerra Mundial, un dueño de bar se reencuentra con un antiguo amor.', 'https://image.tmdb.org/t/p/w500/example.jpg', 102, 'ATP', 'Romance', '2026-12-01 00:00:00', '2027-12-31 23:59:59');

-- Función de ejemplo para la película 1 en la Sala 1 del local Centro.
INSERT INTO funciones (fk_id_pelicula, fk_id_sala, fecha_hora, precio)
VALUES (1, 1, '2027-01-01 20:00:00', 4500.00);
