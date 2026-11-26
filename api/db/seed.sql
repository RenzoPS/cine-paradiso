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
(3, 'Estacionamiento', 'Estacionamiento cubierto durante la función', 2500.00, TRUE);


-- Datos de prueba. Fechas relativas a cuando se crea la base.
SET @hoy = DATE(UTC_TIMESTAMP() - INTERVAL 3 HOUR);

INSERT INTO peliculas (id_pelicula, tmdb_id, titulo, sinopsis, poster_url, duracion_min, clasificacion, genero) VALUES
(1, 27205, 'Origen',
    'Dom Cobb es un ladrón hábil, el mejor de todos, especializado en el peligroso arte de extracción: el robo de secretos valiosos desde las profundidades del subconsciente durante el estado de sueño cuando la mente está más vulnerable. Esta habilidad excepcional de Cobb le ha hecho un jugador codiciado en el traicionero nuevo mundo de espionaje corporativo, pero al mismo tiempo, le ha convertido en un fugitivo internacional y ha tenido que sacrificar todo que le importaba. Ahora a Cobb se le ofrece una oportunidad para redimirse. Con un último trabajo podría recuperar su vida anterior, pero solamente si logra lo imposible.',
    'https://image.tmdb.org/t/p/w500/tXQvtRWfkUUnWJAn2tN3jERIUG.jpg', 148, '+13', 'Acción'),
(2, 157336, 'Interstellar',
    'Un grupo de exploradores hacen uso de un agujero de gusano recientemente descubierto para superar las limitaciones de los viajes espaciales tripulados y vencer las inmensas distancias que tiene un viaje interestelar.',
    'https://image.tmdb.org/t/p/w500/d1QKiYtceF3GDtxvTFXFAqwwah9.jpg', 169, '+13', 'Aventura'),
(3, 862, 'Toy Story',
    'Los juguetes de Andy, un niño de seis años, temen que haya llegado su hora y que un nuevo regalo de cumpleaños les sustituya en el corazón de su dueño. Woody, un vaquero que ha sido hasta ahora el juguete favorito de Andy, trata de tranquilizarlos hasta que aparece Buzz Lightyear, un héroe espacial dotado de todo tipo de avances tecnológicos. Woody es relegado a un segundo plano, pero su constante rivalidad se transformará en una gran amistad cuando ambos se pierden en la ciudad sin saber cómo volver a casa.',
    'https://image.tmdb.org/t/p/w500/jvn7wy3RSNEXnFSXLpH2of2LcV6.jpg', 77, 'ATP', 'Familia'),
(4, 603, 'Matrix',
    'Thomas Anderson lleva una doble vida: por el día es programador en una importante empresa de software, y por la noche un hacker informático llamado Neo. Su vida no volverá a ser igual cuando unos misteriosos personajes le inviten a descubrir la respuesta a la pregunta que no le deja dormir: ¿qué es Matrix?',
    'https://image.tmdb.org/t/p/w500/8rT9kG2EYkZpJmYCuTJNnPDEube.jpg', 138, '+16', 'Acción'),
(5, 238, 'El padrino',
    'Don Vito Corleone, conocido dentro de los círculos del hampa como "El Padrino", es el patriarca de una de las cinco familias que ejercen el mando de la Cosa Nostra en Nueva York (Estados Unidos) durante la década de 1940. Don Corleone tiene cuatro hijos: una chica, Connie, y tres varones; Sonny, Michael y Fredo. Cuando Vito reclina intervenir en el negocio de estupefacientes, empieza una cruenta lucha de violentos episodios entre las distintas familias del crimen organizado.',
    'https://image.tmdb.org/t/p/w500/5HlLUsmsv60cZVTzVns9ICZD6zU.jpg', 175, '+16', 'Drama');

-- En cartel
UPDATE peliculas
SET disponible_desde = @hoy - INTERVAL 14 DAY,
    disponible_hasta = TIMESTAMP(@hoy + INTERVAL 30 DAY, '23:59:59')
WHERE id_pelicula IN (1, 2, 3);

-- Dada de baja
UPDATE peliculas
SET disponible_desde = @hoy - INTERVAL 30 DAY,
    disponible_hasta = TIMESTAMP(@hoy - INTERVAL 1 DAY, '23:59:59')
WHERE id_pelicula = 4;

-- Próximamente
UPDATE peliculas
SET disponible_desde = @hoy + INTERVAL 7 DAY,
    disponible_hasta = TIMESTAMP(@hoy + INTERVAL 37 DAY, '23:59:59')
WHERE id_pelicula = 5;

INSERT INTO funciones (id_funcion, fk_id_pelicula, fk_id_sala, fecha_hora, precio, cancelada) VALUES
(1, 4, 1, TIMESTAMP(@hoy - INTERVAL 1 DAY, '21:00:00'), 6500.00, FALSE),
(2, 1, 1, TIMESTAMP(@hoy + INTERVAL 2 DAY, '20:00:00'), 7500.00, FALSE),
(3, 3, 2, TIMESTAMP(@hoy + INTERVAL 2 DAY, '17:00:00'), 7000.00, FALSE),
(4, 2, 3, TIMESTAMP(@hoy + INTERVAL 3 DAY, '21:00:00'), 8000.00, FALSE),
(5, 2, 4, TIMESTAMP(@hoy + INTERVAL 2 DAY, '20:00:00'), 6500.00, TRUE);

-- Compras del cliente (id 2)
INSERT INTO compras (id_compra, fk_id_usuario, fk_id_funcion, estado, fecha_hora, cancelada_por) VALUES
(1, 2, 1, 'usada', TIMESTAMP(@hoy - INTERVAL 3 DAY, '18:00:00'), NULL),
(2, 2, 1, 'vencida', TIMESTAMP(@hoy - INTERVAL 3 DAY, '19:00:00'), NULL),
(3, 2, 1, 'cancelada', TIMESTAMP(@hoy - INTERVAL 4 DAY, '12:00:00'), 'cliente'),
(4, 2, 2, 'pagada', TIMESTAMP(@hoy - INTERVAL 1 DAY, '18:00:00'), NULL),
(5, 2, 3, 'pagada', TIMESTAMP(@hoy - INTERVAL 1 DAY, '19:00:00'), NULL),
(6, 2, 4, 'pagada', TIMESTAMP(@hoy - INTERVAL 1 DAY, '20:00:00'), NULL),
(7, 2, 5, 'cancelada', TIMESTAMP(@hoy - INTERVAL 1 DAY, '21:00:00'), 'admin');

INSERT INTO entradas (fk_id_compra, fk_id_funcion, fk_id_butaca)
SELECT c.id_compra, c.fk_id_funcion, b.id_butaca
FROM compras c
JOIN funciones f ON f.id_funcion = c.fk_id_funcion
JOIN butacas b ON b.fk_id_sala = f.fk_id_sala
WHERE (c.id_compra, b.fila, b.numero) IN (
    (1, 'E', 6), (1, 'E', 7),
    (4, 'D', 5), (4, 'D', 6),
    (5, 'C', 3), (5, 'C', 4), (5, 'C', 5), (5, 'C', 6),
    (6, 'F', 5)
);

INSERT INTO compras_servicios (fk_id_compra, fk_id_servicio, cantidad) VALUES
(1, 1, 2),
(4, 1, 2),
(4, 3, 1);
