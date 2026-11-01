-- Datos fijos que el sistema necesita para funcionar. Se ejecuta después de init.sql.

SET NAMES utf8mb4;

USE cine_paradiso;

INSERT INTO locales (id_local, nombre, direccion) VALUES
(1, 'Cine Paradiso - Centro', 'Av. Corrientes 1234, CABA'),
(2, 'Cine Paradiso - Norte', 'Av. Cabildo 2800, CABA');

INSERT INTO salas (id_sala, fk_id_local, nombre) VALUES
(1, 1, 'Sala IMAX 1'),
(2, 1, 'Sala 2 - Tradicional'),
(3, 2, 'Sala Principal Norte');

INSERT INTO generos (id_genero, tmdb_id, nombre) VALUES
(1, 28, 'Acción'),
(2, 35, 'Comedia'),
(3, 18, 'Drama'),
(4, 878, 'Ciencia Ficción');


INSERT INTO peliculas (id_pelicula, tmdb_id, titulo, sinopsis, poster_url, duracion_min, clasificacion, disponible_desde, disponible_hasta, activa) VALUES
(1, 550, 'El Club de la Pelea', 'Un oficinista insomne y un vendedor de jabón despreocupado forman un club de lucha clandestino.', 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg', 139, 'SAM16', '2026-10-01 00:00:00', '2026-12-31 23:59:59', TRUE),
(2, 27205, 'Inception', 'Un ladrón que roba secretos corporativos a través del sueño recibe la tarea inversa de implantar una idea.', 'https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg', 148, 'SAM13', '2026-10-01 00:00:00', '2026-12-31 23:59:59', TRUE);


INSERT INTO peliculas_generos (fk_id_pelicula, fk_id_genero) VALUES
(1, 3),
(2, 1),
(2, 4);


INSERT INTO butacas (id_butaca, fk_id_sala, fila, numero) VALUES
(1, 1, 'A', 1),
(2, 1, 'A', 2),
(3, 1, 'A', 3),
(4, 1, 'B', 1),
(5, 1, 'B', 2);


INSERT INTO funciones (id_funcion, fk_id_pelicula, fk_id_sala, fecha_hora, precio, activa) VALUES
(1, 1, 1, '2026-11-10 18:30:00', 4500.00, TRUE),
(2, 2, 1, '2026-11-10 21:30:00', 5000.00, TRUE);

INSERT INTO usuarios (id_usuario, nombre, apellido, email, contrasena_hash, rol) VALUES
(1, 'Admin', 'Sistema', 'admin@cineparadiso.com', '$2b$12$e8...hashdemuestraexitoso...', 'admin'),
(2, 'Juan', 'Pérez', 'cliente@correo.com', '$2b$12$e8...hashdemuestraexitoso...', 'cliente');

INSERT INTO servicios (id_servicio, nombre, descripcion, precio, activo) VALUES
(1, 'Combo Balde + Bebida', 'Balde de pochoclos grandes y gaseosa de 1L', 3500.00, TRUE),
(2, 'Chocolate de la casa', 'Barra de chocolate semi-amargo 100g', 1500.00, TRUE);
