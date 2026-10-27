-- Creación de la base y las tablas. Docker lo ejecuta solo la primera vez que crea el volumen.

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS cine_paradiso;

USE cine_paradiso;

CREATE TABLE locales (
    id_local INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    direccion VARCHAR(150) NOT NULL
);

CREATE TABLE salas (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_local INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    CONSTRAINT fk_sala_local FOREIGN KEY (fk_id_local) REFERENCES locales(id_local)
);

CREATE TABLE generos (
    id_genero INT AUTO_INCREMENT PRIMARY KEY,
    tmdb_id INT UNIQUE, -- ID para consultas con la API
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE peliculas (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    tmdb_id INT UNIQUE, -- ID para consultas con la API
    titulo VARCHAR(150) NOT NULL,
    sinopsis TEXT,
    poster_url VARCHAR(255),
    duracion_min INT,
    clasificacion VARCHAR(10),
    disponible_desde DATETIME,
    disponible_hasta DATETIME,
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE peliculas_generos (
    fk_id_pelicula INT NOT NULL,
    fk_id_genero INT NOT NULL,
    PRIMARY KEY (fk_id_pelicula, fk_id_genero),
    CONSTRAINT fk_pg_pelicula FOREIGN KEY (fk_id_pelicula) REFERENCES peliculas(id_pelicula),
    CONSTRAINT fk_pg_genero FOREIGN KEY (fk_id_genero) REFERENCES generos(id_genero)
);

CREATE TABLE funciones (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_pelicula INT NOT NULL,
    fk_id_sala INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_funcion_pelicula FOREIGN KEY (fk_id_pelicula) REFERENCES peliculas(id_pelicula),
    CONSTRAINT fk_funcion_sala FOREIGN KEY (fk_id_sala) REFERENCES salas(id_sala)
);

CREATE TABLE butacas (
    id_butaca INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_sala INT NOT NULL,
    fila CHAR(2) NOT NULL,
    numero INT NOT NULL,
    CONSTRAINT fk_butaca_sala FOREIGN KEY (fk_id_sala) REFERENCES salas(id_sala),
    CONSTRAINT uk_sala_fila_numero UNIQUE (fk_id_sala, fila, numero)
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'cliente') NOT NULL,
    fecha_creacion DATETIME NOT NULL
);

CREATE TABLE compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_usuario INT NOT NULL,
    fk_id_funcion INT NOT NULL,
    estado ENUM('pendiente', 'pagada', 'usada', 'cancelada', 'vencida') NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    numero_factura VARCHAR(20) UNIQUE,
    qr_token VARCHAR(255) UNIQUE,
    fecha_creacion DATETIME NOT NULL,
    fecha_vencimiento DATETIME,
    fecha_pago DATETIME,
    fecha_validacion DATETIME,
    fecha_cancelacion DATETIME,
    CONSTRAINT fk_compra_usuario FOREIGN KEY (fk_id_usuario) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_compra_funcion FOREIGN KEY (fk_id_funcion) REFERENCES funciones(id_funcion)
);

CREATE TABLE entradas (
    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_compra INT NOT NULL,
    fk_id_funcion INT NOT NULL,
    fk_id_butaca INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    ocupada TINYINT NULL,
    CONSTRAINT fk_entrada_compra FOREIGN KEY (fk_id_compra) REFERENCES compras(id_compra),
    CONSTRAINT fk_entrada_funcion FOREIGN KEY (fk_id_funcion) REFERENCES funciones(id_funcion),
    CONSTRAINT fk_entrada_butaca FOREIGN KEY (fk_id_butaca) REFERENCES butacas(id_butaca),
    CONSTRAINT uk_funcion_butaca_ocupada UNIQUE (fk_id_funcion, fk_id_butaca, ocupada)
);

CREATE TABLE servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE compras_servicios (
    fk_id_compra INT NOT NULL,
    fk_id_servicio INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (fk_id_compra, fk_id_servicio),
    CONSTRAINT fk_cs_compra FOREIGN KEY (fk_id_compra) REFERENCES compras(id_compra),
    CONSTRAINT fk_cs_servicio FOREIGN KEY (fk_id_servicio) REFERENCES servicios(id_servicio)
);
