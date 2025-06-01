
-- Створення бази даних
CREATE DATABASE IF NOT EXISTS datetime_app 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Використання бази даних
USE datetime_app;

-- Створення таблиці користувачів
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Створення таблиці обчислень
CREATE TABLE IF NOT EXISTS calculations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    calculation_type VARCHAR(50) NOT NULL,
    input_data TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Створення індексів для оптимізації
CREATE INDEX idx_user_calculations ON calculations(user_id, created_at);
CREATE INDEX idx_calculation_type ON calculations(calculation_type);
CREATE INDEX idx_username ON users(username);

-- Вставка тестового користувача (опціонально)
INSERT INTO users (username, password_hash, email) VALUES 
('admin', SHA2('admin123', 256), 'admin@example.com'),
('test_user', SHA2('test123', 256), 'test@example.com');

-- Показати створені таблиці
SHOW TABLES;

-- Показати структуру таблиць
DESCRIBE users;
DESCRIBE calculations;