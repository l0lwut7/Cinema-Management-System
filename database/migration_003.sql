-- Migration 003: Add rows and cols to SALOON table
-- Enables layout-aware seat generation during saloon creation.
-- Run once: mysql -u root -p cinema_db < database/migration_003.sql

USE cinema_db;

ALTER TABLE SALOON
    ADD COLUMN `rows` INT NOT NULL DEFAULT 0,
    ADD COLUMN `cols` INT NOT NULL DEFAULT 0;
