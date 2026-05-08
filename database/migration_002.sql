-- Migration 002: Add visibility_status to movie table
-- Controls where each movie appears for customers.
-- Run once: mysql -u root -p cinema_db < database/migration_002.sql

USE cinema_db;

ALTER TABLE MOVIE
    ADD COLUMN visibility_status
        ENUM('now_showing', 'coming_soon', 'catalog_only')
        NOT NULL DEFAULT 'catalog_only';
