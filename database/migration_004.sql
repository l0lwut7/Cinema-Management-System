-- Migration 004: booking_code, ticket_code, and screening snapshot on BOOKING
-- Adds the partial-refund ID hierarchy: a random 6-digit booking_code and
-- a composite ticket_code (<booking_code><row><seat>) used for refunds/scanning.
-- Run once: mysql -u root -p cinema_db < database/migration_004.sql

USE cinema_db;

-- 1. booking_code: random 6-digit display ID, set by the application on INSERT.
ALTER TABLE BOOKING ADD COLUMN booking_code INT UNIQUE;

-- 2. screening_id snapshot so booking history can display movie/time info
--    even after all tickets are deleted during a full refund.
ALTER TABLE BOOKING ADD COLUMN screening_id INT NULL;
ALTER TABLE BOOKING
    ADD CONSTRAINT fk_booking_screening_snap
    FOREIGN KEY (screening_id) REFERENCES SCREENING(screening_id) ON DELETE SET NULL;

-- 3. ticket_code: human-readable composite ID (e.g. "162253A4").
ALTER TABLE TICKET ADD COLUMN ticket_code VARCHAR(20) UNIQUE;

-- 4. Backfill booking_code for existing rows (offset keeps values in 6-digit range).
UPDATE BOOKING SET booking_code = 100000 + booking_id WHERE booking_code IS NULL;

-- 5. Backfill screening_id on BOOKING from the first ticket of each booking.
UPDATE BOOKING b
INNER JOIN (
    SELECT booking_id, MIN(screening_id) AS snap_sid
    FROM TICKET
    GROUP BY booking_id
) sub ON b.booking_id = sub.booking_id
SET b.screening_id = sub.snap_sid
WHERE b.screening_id IS NULL;

-- 6. Backfill ticket_code for all existing tickets.
UPDATE TICKET t
JOIN BOOKING b ON t.booking_id = b.booking_id
SET t.ticket_code = CONCAT(b.booking_code, t.row_letter, t.seat_number)
WHERE t.ticket_code IS NULL;
