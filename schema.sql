-- Sistema de Soporte Técnico
-- Autor: Gerardo Escamilla Cerda
-- Dominio 4 — Soporte Técnico
-- Fecha: Abril 2026

CREATE DATABASE IF NOT EXISTS soporte_db;
USE soporte_db;

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tecnicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    tecnico_id INT,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    prioridad ENUM('baja', 'media', 'alta', 'critica') NOT NULL DEFAULT 'media',
    estado ENUM('abierto', 'en_progreso', 'resuelto') NOT NULL DEFAULT 'abierto',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_ticket_tecnico FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id)
);

INSERT INTO clientes (nombre, email) VALUES
    ('Ana García', 'ana.garcia@empresa.com'),
    ('Luis Martínez', 'luis.martinez@empresa.com'),
    ('María López', 'maria.lopez@empresa.com');

INSERT INTO tecnicos (nombre, especialidad) VALUES
    ('Carlos Pérez', 'Redes y Conectividad'),
    ('Sofía Ramírez', 'Software y Aplicaciones'),
    ('Diego Torres', 'Hardware y Equipos');
