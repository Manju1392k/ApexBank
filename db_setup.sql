-- =======================================================
-- SQL Script for Setting Up the ApexBank Database in MySQL
-- =======================================================

-- 1. Create Database if it does not already exist
CREATE DATABASE IF NOT EXISTS apex_bank_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. Select Database
USE apex_bank_db;

-- 3. (Optional) Create a dedicated banking app user
-- Uncomment and update the password below if you wish to use a dedicated MySQL user:
-- CREATE USER IF NOT EXISTS 'apex_user'@'localhost' IDENTIFIED BY 'BankingSecurePass2026!';
-- GRANT ALL PRIVILEGES ON apex_bank_db.* TO 'apex_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 4. Verification Check
SHOW TABLES;
