-- =====================================================================
-- MySQL - Factura y detalle de factura
-- Ejecutar con:  mysql -u root -p < dbs/03_mysql.sql
-- =====================================================================

CREATE DATABASE IF NOT EXISTS billing
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE billing;

DROP TABLE IF EXISTS detalle_factura;
DROP TABLE IF EXISTS factura;

CREATE TABLE factura (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  client_document     VARCHAR(32)    NOT NULL,
  employee_document   VARCHAR(32)    NOT NULL,
  payment_method      ENUM('CASH','CARD','TRANSFER') NOT NULL,
  subtotal            DECIMAL(12,2)  NOT NULL,
  tax_rate            DECIMAL(5,4)   NOT NULL DEFAULT 0.1900,
  tax                 DECIMAL(12,2)  NOT NULL,
  total               DECIMAL(12,2)  NOT NULL,
  created_at          DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_factura_client   (client_document),
  INDEX idx_factura_employee (employee_document),
  INDEX idx_factura_created  (created_at)
) ENGINE=InnoDB;

CREATE TABLE detalle_factura (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  invoice_id      INT            NOT NULL,
  product_sku     VARCHAR(64)    NOT NULL,
  product_name    VARCHAR(200)   NOT NULL,
  quantity        INT            NOT NULL CHECK (quantity > 0),
  unit_price      DECIMAL(12,2)  NOT NULL CHECK (unit_price >= 0),
  line_total      DECIMAL(12,2)  NOT NULL,
  CONSTRAINT fk_detalle_factura
    FOREIGN KEY (invoice_id) REFERENCES factura(id) ON DELETE CASCADE,
  INDEX idx_det_sku (product_sku)
) ENGINE=InnoDB;

-- --------- Facturas semilla ---------
INSERT INTO factura (client_document, employee_document, payment_method,
                     subtotal, tax_rate, tax, total)
VALUES
  ('C100','E001','CARD',     2555000, 0.19,  485450,  3040450),
  ('C101','E001','CASH',      850000, 0.19,  161500,  1011500),
  ('C102','E002','TRANSFER', 1500000, 0.19,  285000,  1785000),
  ('C103','E002','CASH',      230000, 0.19,   43700,   273700);

INSERT INTO detalle_factura (invoice_id, product_sku, product_name, quantity, unit_price, line_total) VALUES
  (1,'P-001','Laptop Lenovo IdeaPad 3',         1, 2500000, 2500000),
  (1,'P-002','Mouse inalámbrico Logitech M170', 1,   55000,   55000),
  (2,'P-005','Smartphone Samsung Galaxy A15',   1,  850000,  850000),
  (3,'P-004','Monitor LG 24" Full HD',          2,  720000, 1440000),
  (3,'P-002','Mouse inalámbrico Logitech M170', 1,   55000,   55000),
  (3,'L-001','Libro: Clean Architecture',       1, 120000,  120000),
  (4,'P-003','Teclado mecánico Redragon Kumara',1,  230000,  230000);

-- Re-cálculo defensivo de subtotal/IVA/total a partir de las líneas
UPDATE factura f
JOIN (
  SELECT invoice_id,
         ROUND(SUM(line_total),2)              AS sub,
         ROUND(SUM(line_total) * 0.19,2)       AS iv,
         ROUND(SUM(line_total) * 1.19,2)       AS tot
  FROM detalle_factura
  GROUP BY invoice_id
) d ON d.invoice_id = f.id
SET f.subtotal = d.sub, f.tax = d.iv, f.total = d.tot;
