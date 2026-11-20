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

CREATE TABLE butacas (
    id_butaca INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_sala INT NOT NULL,
    fila CHAR(2) NOT NULL,
    numero INT NOT NULL,
    CONSTRAINT fk_butaca_sala FOREIGN KEY (fk_id_sala) REFERENCES salas(id_sala),
    CONSTRAINT uk_sala_fila_numero UNIQUE (fk_id_sala, fila, numero)
);

CREATE TABLE peliculas (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    tmdb_id INT UNIQUE,
    titulo VARCHAR(150) NOT NULL,
    sinopsis TEXT,
    poster_url VARCHAR(255),
    duracion_min INT,
    clasificacion VARCHAR(10),
    genero VARCHAR(50),
    disponible_desde DATETIME,
    disponible_hasta DATETIME
);

CREATE TABLE funciones (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_pelicula INT NOT NULL,
    fk_id_sala INT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_funcion_pelicula FOREIGN KEY (fk_id_pelicula) REFERENCES peliculas(id_pelicula),
    CONSTRAINT fk_funcion_sala FOREIGN KEY (fk_id_sala) REFERENCES salas(id_sala),
    CONSTRAINT chk_funciones_precio CHECK (precio >= 0)
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol ENUM('cliente', 'admin') NOT NULL DEFAULT 'cliente',
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- El estado es de la compra. El total, el número de factura (id_compra) y el QR se calculan.
CREATE TABLE compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_usuario INT NOT NULL,
    fk_id_funcion INT NOT NULL,
    estado ENUM('pendiente', 'pagada', 'usada', 'cancelada', 'vencida') NOT NULL DEFAULT 'pendiente',
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_compra_usuario FOREIGN KEY (fk_id_usuario) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_compra_funcion FOREIGN KEY (fk_id_funcion) REFERENCES funciones(id_funcion)
);

-- Una butaca está ocupada en una función si existe su entrada.
-- Al vencer o cancelar la compra se borran sus entradas y las butacas quedan libres.
CREATE TABLE entradas (
    id_entrada INT AUTO_INCREMENT PRIMARY KEY,
    fk_id_compra INT NOT NULL,
    fk_id_funcion INT NOT NULL,
    fk_id_butaca INT NOT NULL,
    CONSTRAINT fk_entrada_compra FOREIGN KEY (fk_id_compra) REFERENCES compras(id_compra),
    CONSTRAINT fk_entrada_funcion FOREIGN KEY (fk_id_funcion) REFERENCES funciones(id_funcion),
    CONSTRAINT fk_entrada_butaca FOREIGN KEY (fk_id_butaca) REFERENCES butacas(id_butaca),
    CONSTRAINT uk_funcion_butaca UNIQUE (fk_id_funcion, fk_id_butaca)
);

CREATE TABLE servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_servicios_precio CHECK (precio >= 0)
);

CREATE TABLE compras_servicios (
    fk_id_compra INT NOT NULL,
    fk_id_servicio INT NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (fk_id_compra, fk_id_servicio),
    CONSTRAINT fk_cs_compra FOREIGN KEY (fk_id_compra) REFERENCES compras(id_compra),
    CONSTRAINT fk_cs_servicio FOREIGN KEY (fk_id_servicio) REFERENCES servicios(id_servicio),
    CONSTRAINT chk_cantidad_positiva CHECK (cantidad > 0)
);
