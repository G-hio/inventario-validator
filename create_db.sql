-- Script: create_db.sql
CREATE DATABASE IF NOT EXISTS inventario_db;
USE inventario_db;
CREATE TABLE IF NOT EXISTS productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(50) NOT NULL,
  nombre VARCHAR(150),
  cantidad_registrada INT DEFAULT 0
);
CREATE TABLE IF NOT EXISTS inventario_fisico (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(50) NOT NULL,
  cantidad_fisica INT DEFAULT 0,
  fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO productos (sku, nombre, cantidad_registrada) VALUES
  ('SKU-001','Producto A', 100),
  ('SKU-002','Producto B', 50),
  ('SKU-003','Producto C', 75);
INSERT INTO inventario_fisico (sku, cantidad_fisica) VALUES
  ('SKU-001', 98),
  ('SKU-002', 50),
  ('SKU-003', 80);
