-- ==============================================================================
-- CINEMA MANAGEMENT SYSTEM - SEED DATA
-- Covers all 25+ Page Flows (Admin, Staff, Customer, Auth, Analytics) along the 7 Core Modules (Infrastructure, Identity, Catalog, Scheduling, Transactions, Engagement, Analytics)
-- Designed to provide comprehensive test coverage for all major features and edge cases.
-- ==============================================================================
USE cinema_db;

-- ------------------------------------------------------------------------------
-- 1. UTILITY PROCEDURES
-- ------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS GenerateSeats;
DELIMITER //
CREATE PROCEDURE GenerateSeats(IN t_id INT, IN s_num INT, IN num_rows INT, IN seats_per_row INT)
BEGIN
    DECLARE current_row INT DEFAULT 0;
    DECLARE current_col INT DEFAULT 1;
    DECLARE row_char VARCHAR(1);

    WHILE current_row < num_rows DO
        SET row_char = CHAR(65 + current_row);
        SET current_col = 1;
        
        WHILE current_col <= seats_per_row DO
            INSERT INTO SEAT (theater_id, saloon_number, row_letter, number, type) 
            VALUES (t_id, s_num, row_char, current_col, 'Standard');
            SET current_col = current_col + 1;
        END WHILE;
        
        SET current_row = current_row + 1;
    END WHILE;
END //
DELIMITER ;

-- ------------------------------------------------------------------------------
-- 2. INFRASTRUCTURE & BUSINESS RULES (Admin Flow)
-- ------------------------------------------------------------------------------
INSERT INTO THEATER (theater_id, name, phone_number, address) VALUES
(1, 'Mavibahçe', '555-1111', 'Mavibahçe AVM, İzmir'),
(2, 'Hilltown', '555-2222', 'Hilltown AVM, İzmir');

INSERT INTO SALOON (theater_id, number, capacity, type, is_active) VALUES
(1, 1, 50, 'IMAX', TRUE),
(1, 2, 30, 'Standard', TRUE),
(2, 1, 40, 'Gold Class', TRUE);

-- Generate the physical seat grids
CALL GenerateSeats(1, 1, 5, 10); -- Mavibahçe S1: Rows A-E, 10 seats
CALL GenerateSeats(1, 2, 3, 10); -- Mavibahçe S2: Rows A-C, 10 seats
CALL GenerateSeats(2, 1, 4, 10); -- Hilltown S1: Rows A-D, 10 seats

-- Deals and Consumables (Business Rules CMS)
INSERT INTO DEAL (deal_id, name, discount_percent, valid_until) VALUES 
(1, 'Student Discount', 15.00, '2026-12-31'),
(2, 'VIP Member Special', 25.00, '2026-12-31');

INSERT INTO CONSUMABLE (consumable_id, name, unit_price, stock_quantity) VALUES
(1, 'Large Popcorn', 8.50, 500),
(2, 'Medium Soda', 5.00, 500),
(3, 'Nachos', 7.00, 200);

-- ------------------------------------------------------------------------------
-- 3. IDENTITY & AUTHENTICATION (Auth Flow & Staff CMS)
-- ------------------------------------------------------------------------------
-- Create Base Users
INSERT INTO `USER` (user_id, first_name, last_name, phone_number, email, password_hash) VALUES
(1, 'Alice', 'Smith', '555-0001', 'alice@email.com', 'hashed1'),
(2, 'Bob', 'Jones', '555-0002', 'bob@email.com', 'hashed2'),
(3, 'Charlie', 'Brown', '555-0003', 'charlie@email.com', 'hashed3'),
(4, 'Diana', 'Prince', '555-0004', 'diana.admin@cinema.com', 'hashed4'),
(5, 'Evan', 'Wright', '555-0005', 'evan.staff@cinema.com', 'hashed5'),
(6, 'Fiona', 'Gallagher', '555-0006', 'fiona.new@cinema.com', 'hashed6');

-- Assign Customers
INSERT INTO CUSTOMER (user_id, birth_date, loyalty_points, membership_tier) VALUES
(1, '1990-05-14', 1500, 'VIP'),        -- Alice: Target for Top Spender Dashboard
(2, '1985-10-22', 200, 'standard'),    -- Bob: Standard user
(3, '2001-01-08', 50, 'standard');     -- Charlie: New user

-- Assign Staff (Tests the Admin Staff Management & Staff Login flows)
INSERT INTO EMPLOYEE (user_id, role, salary, account_status, auth_level, work_shift, theater_id) VALUES
(4, 'System Admin', 8500.00, 'active', 3, 'All', NULL),                 -- Diana: Full Admin (Auth 3)
(5, 'Ticket Counter', 3500.00, 'active', 1, 'Morning', 1),              -- Evan: Active Staff at Mavibahçe
(6, 'Usher', 3000.00, 'pending', 1, 'Evening', 2);                      -- Fiona: Pending Admin Approval!

-- ------------------------------------------------------------------------------
-- 4. MOVIE CATALOG & METADATA (Discovery Flow)
-- ------------------------------------------------------------------------------
-- Lookup Tables
INSERT INTO GENRE (genre_id, name) VALUES (1, 'Sci-Fi'), (2, 'Action'), (3, 'Drama'), (4, 'Comedy');
INSERT INTO FORMAT (format_id, name) VALUES (1, '2D'), (2, '3D'), (3, 'IMAX');

-- Movie 1: "Vizyondaki" (Now Showing)
INSERT INTO MOVIE (title, director, duration_mins, rating_age, release_date, summary) 
VALUES ('Dune: Part Two', 'Denis Villeneuve', 166, 'PG-13', '2024-03-01', 'Paul Atreides unites with Chani.');
SET @movie_active = LAST_INSERT_ID();

INSERT INTO MOVIE_RUN (movie_id, start_date, end_date) VALUES (@movie_active, '2024-03-01', '2026-12-31');
INSERT INTO MOVIE_GENRE (movie_id, genre_id) VALUES (@movie_active, 1), (@movie_active, 2);
INSERT INTO MOVIE_FORMAT (movie_id, format_id) VALUES (@movie_active, 1), (@movie_active, 3);
INSERT INTO MOVIE_CAST (movie_id, cast_name) VALUES (@movie_active, 'Timothee Chalamet'), (@movie_active, 'Zendaya');

-- Movie 2: "Yakında" (Coming Soon)
INSERT INTO MOVIE (title, director, duration_mins, rating_age, release_date, summary) 
VALUES ('Avatar 3', 'James Cameron', 190, 'PG-13', '2026-12-19', 'Return to Pandora.');
SET @movie_future = LAST_INSERT_ID();

INSERT INTO MOVIE_RUN (movie_id, start_date, end_date) VALUES (@movie_future, '2026-12-19', '2027-05-01');
INSERT INTO MOVIE_GENRE (movie_id, genre_id) VALUES (@movie_future, 1), (@movie_future, 2);
INSERT INTO MOVIE_FORMAT (movie_id, format_id) VALUES (@movie_future, 2), (@movie_future, 3);
INSERT INTO MOVIE_CAST (movie_id, cast_name) VALUES (@movie_future, 'Sam Worthington');

-- Movie 3: Past Movie (For User History & Reviews)
INSERT INTO MOVIE (title, director, duration_mins, rating_age, release_date, summary) 
VALUES ('Interstellar', 'Christopher Nolan', 169, 'PG-13', '2014-11-07', 'Space exploration.');
SET @movie_past = LAST_INSERT_ID();

INSERT INTO MOVIE_RUN (movie_id, start_date, end_date) VALUES (@movie_past, '2014-11-07', '2015-02-01');
INSERT INTO MOVIE_GENRE (movie_id, genre_id) VALUES (@movie_past, 1), (@movie_past, 3);
INSERT INTO MOVIE_FORMAT (movie_id, format_id) VALUES (@movie_past, 3);
INSERT INTO MOVIE_CAST (movie_id, cast_name) VALUES (@movie_past, 'Matthew McConaughey');

-- ------------------------------------------------------------------------------
-- 5. SCREENINGS (Scheduling CMS)
-- ------------------------------------------------------------------------------
-- Active Screenings for Booking Flow
INSERT INTO SCREENING (movie_id, theater_id, saloon_number, start_time, base_price, is_subtitled) 
VALUES (@movie_active, 1, 1, '2026-10-15 19:00:00', 18.00, FALSE);
SET @screening_dune_downtown = LAST_INSERT_ID();

INSERT INTO SCREENING (movie_id, theater_id, saloon_number, start_time, base_price, is_subtitled) 
VALUES (@movie_active, 2, 1, '2026-10-15 20:30:00', 20.00, TRUE);
SET @screening_dune_uptown = LAST_INSERT_ID();

-- ------------------------------------------------------------------------------
-- 6. TRANSACTIONS HUB (Bookings, Tickets, Payments, Consumables)
-- ------------------------------------------------------------------------------
-- TRANSACTION 1: Alice books 2 seats for Dune + Popcorn (USED TICKETS - Arrived 15 mins early)
INSERT INTO BOOKING (user_id, deal_id, total_amount) VALUES (1, NULL, 44.50); 
SET @booking_1 = LAST_INSERT_ID();

INSERT INTO TICKET (booking_id, screening_id, theater_id, saloon_number, row_letter, seat_number, ticket_type, scanned_at) VALUES 
(@booking_1, @screening_dune_downtown, 1, 1, 'D', 4, 'VIP', '2026-10-15 18:45:00'),
(@booking_1, @screening_dune_downtown, 1, 1, 'D', 5, 'VIP', '2026-10-15 18:45:00');

INSERT INTO BOOKING_CONSUMABLE (booking_id, consumable_id, quantity) VALUES (@booking_1, 1, 1);
INSERT INTO PAYMENT (booking_id, method, status) VALUES (@booking_1, 'Credit Card', 'Completed');

-- TRANSACTION 2: Bob books Dune using Student Discount (UNUSED TICKET - Pending Scan)
INSERT INTO BOOKING (user_id, deal_id, total_amount) VALUES (2, 1, 15.30); 
SET @booking_2 = LAST_INSERT_ID();

INSERT INTO TICKET (booking_id, screening_id, theater_id, saloon_number, row_letter, seat_number, ticket_type, scanned_at) VALUES 
(@booking_2, @screening_dune_uptown, 2, 1, 'A', 1, 'Student', NULL);

INSERT INTO PAYMENT (booking_id, method, status) VALUES (@booking_2, 'Cash', 'Completed');

-- TRANSACTION 3: A Refunded Booking (To test the Staff Refund Management Flow)
INSERT INTO BOOKING (user_id, deal_id, total_amount) VALUES (3, NULL, 18.00); 
SET @booking_refund = LAST_INSERT_ID();

INSERT INTO TICKET (booking_id, screening_id, theater_id, saloon_number, row_letter, seat_number, ticket_type, scanned_at) VALUES 
(@booking_refund, @screening_dune_downtown, 1, 1, 'A', 10, 'Standard', NULL);

INSERT INTO PAYMENT (booking_id, method, status) VALUES (@booking_refund, 'Credit Card', 'Refunded');

-- ------------------------------------------------------------------------------
-- 7. ENGAGEMENT (User Profile & Movie Details)
-- ------------------------------------------------------------------------------
-- Reviews (Tests AVG() aggregation on Film Detail Page)
INSERT INTO REVIEW (user_id, movie_id, rating, comment) VALUES
(1, @movie_active, 5, 'Visually stunning!'),
(2, @movie_active, 4, 'A bit long, but great.'),
(1, @movie_past, 5, 'Nolan is a genius.');

-- Favorites (Tests User Profile Favorites list M:N)
INSERT INTO CUSTOMER_FAVORITE_MOVIE (user_id, movie_id) VALUES
(1, @movie_active), 
(1, @movie_past),
(2, @movie_future);