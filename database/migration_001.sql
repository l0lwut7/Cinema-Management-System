-- Migration 001: Add poster_url to movie table + new genres
-- Safe to run against an existing cinema_db (no data loss).
-- Run once: mysql -u root -p cinema_db < database/migration_001.sql

USE cinema_db;

-- Add poster_url column (IF NOT EXISTS supported in MySQL 8+ via
-- a conditional; for older MySQL use the two-step pattern below)
ALTER TABLE MOVIE ADD COLUMN poster_url VARCHAR(500) NULL;

-- Add the 6 new genres.  INSERT IGNORE skips rows whose `name`
-- already exists (the UNIQUE constraint on genre.name protects us).
INSERT IGNORE INTO GENRE (name) VALUES
    ('Horror'),
    ('Fantasy'),
    ('Romance'),
    ('Thriller'),
    ('Animation'),
    ('Adventure');