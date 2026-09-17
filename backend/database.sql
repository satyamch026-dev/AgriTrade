-- =========================================================
-- AGRITRADE DATABASE
-- Simple MySQL schema for the AgriTrade DBMS college project
-- =========================================================

CREATE DATABASE IF NOT EXISTS agritrade;
USE agritrade;

-- ---------------------------------------------------------
-- CUSTOMERS
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    phone       VARCHAR(20),
    address     VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- PRODUCTS
-- (variety / purchase_price / selling_price / minimum_stock
--  are kept because the existing Products page already uses them)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id     INT AUTO_INCREMENT PRIMARY KEY,
    product_name   VARCHAR(100) NOT NULL,
    category       VARCHAR(50)  NOT NULL,
    variety        VARCHAR(100),
    unit           VARCHAR(20)  NOT NULL DEFAULT 'kg',
    purchase_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    selling_price  DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
    minimum_stock  DECIMAL(10,2) NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------
-- PURCHASES (stock bought from a supplier)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS purchases (
    purchase_id   INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    product_id    INT NOT NULL,
    quantity      DECIMAL(10,2) NOT NULL,
    rate          DECIMAL(10,2) NOT NULL,
    total_amount  DECIMAL(12,2) NOT NULL,
    purchase_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- ---------------------------------------------------------
-- SALES (stock sold to a customer)
-- 'status' was added because the existing Dashboard page
-- already displays a Completed / Pending badge per sale.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    sale_id      INT AUTO_INCREMENT PRIMARY KEY,
    customer_id  INT NOT NULL,
    product_id   INT NOT NULL,
    quantity     DECIMAL(10,2) NOT NULL,
    rate         DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    sale_date    DATE NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'Completed',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

-- ---------------------------------------------------------
-- PAYMENTS (money received against a sale)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    customer_id    INT NOT NULL,
    sale_id        INT,
    amount         DECIMAL(12,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    payment_date   DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (sale_id)     REFERENCES sales(sale_id)
);

-- =========================================================
-- SAMPLE DATA
-- (mirrors the values that used to be hard-coded in the
-- AgriTrade frontend, so the site looks the same after the
-- switch to MySQL)
-- =========================================================

INSERT INTO products (product_name, category, variety, unit, purchase_price, selling_price, stock_quantity, minimum_stock) VALUES
('Paddy',            'Grain',    'PR-126',        'kg', 22, 25, 12450, 1000),
('Basmati Rice',     'Rice',     '1121 Basmati',  'kg', 70, 78, 5200,  1000),
('Non-Basmati Rice', 'Rice',     'Sona Masuri',   'kg', 40, 45, 3100,  1000),
('Wheat',            'Grain',    'Lokwan',        'kg', 26, 29, 8750,  1200),
('Maize',            'Grain',    'Hybrid',        'kg', 20, 23, 1200,  1500),
('Mustard',          'Oil Seed', 'Yellow Mustard','kg', 57, 62, 680,   1000);

INSERT INTO customers (name, phone, address) VALUES
('Sharma Traders',   '9876500001', 'Ludhiana, Punjab'),
('ABC Foods',        '9876500002', 'Karnal, Haryana'),
('Punjab Rice Co.',  '9876500003', 'Amritsar, Punjab'),
('Gupta Traders',    '9876500004', 'Delhi'),
('Kisan Foods',      '9876500005', 'Chandigarh');

-- Sales rows mirror the "Recent Transactions" table that used
-- to be hard-coded on the Dashboard page.
INSERT INTO sales (customer_id, product_id, quantity, rate, total_amount, sale_date, status) VALUES
(1, 1, 1200, 37.67, 45200, '2026-09-12', 'Completed'),
(2, 2, 930,  77.96, 72500, '2026-09-11', 'Completed'),
(3, 4, 1150, 33.70, 38750, '2026-09-10', 'Completed'),
(4, 5, 3800, 24.00, 91200, '2026-09-09', 'Pending'),
(5, 1, 1450, 37.66, 54600, '2026-09-08', 'Completed');

INSERT INTO purchases (supplier_name, product_id, quantity, rate, total_amount, purchase_date) VALUES
('Green Fields Farms',  1, 5000, 21, 105000, '2026-08-20'),
('Haryana Grain Depot', 4, 4000, 25, 100000, '2026-08-22'),
('Sunrise Agro',        6, 1000, 55, 55000,  '2026-08-25');

INSERT INTO payments (customer_id, sale_id, amount, payment_status, payment_date) VALUES
(1, 1, 45200, 'Paid',    '2026-09-12'),
(2, 2, 72500, 'Paid',    '2026-09-11'),
(3, 3, 38750, 'Paid',    '2026-09-10'),
(4, 4, 40000, 'Partial', '2026-09-09'),
(5, 5, 54600, 'Paid',    '2026-09-08');
