-- Creación de la base y las tablas. Docker lo ejecuta solo la primera vez que crea el volumen.

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS cine_paradiso
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cine_paradiso;
