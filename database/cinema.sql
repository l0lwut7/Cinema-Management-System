-- ==============================================================================
-- CINEMA MANAGEMENT SYSTEM DATABASE SCHEMA
-- ==============================================================================

-- This schema file is intentionally non-destructive.
-- Select the target database before running it (for example, via your SQL client,
-- connection configuration, or a separate local-development reset script).

DROP DATABASE IF EXISTS cinema_db;
CREATE DATABASE cinema_db;
USE cinema_db;

-- ------------------------------------------------------------------------------
-- 1. INDEPENDENT ENTITIES & ISA HIERARCHY
-- ------------------------------------------------------------------------------

-- Be sure about the VARCHAR sizes and data types based on expected input lengths and formats in a real-world application. Adjust as necessary for your specific use case or constraints.
CREATE TABLE IF NOT EXISTS USER (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CUSTOMER (
    user_id INT PRIMARY KEY,
    birth_date DATE,
    loyalty_points INT DEFAULT 0,
    membership_tier VARCHAR(50) DEFAULT 'Standard',
    FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS THEATER (
    theater_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    address TEXT
);

-- ON DELETE SET NULL for theater_id in EMPLOYEE allows employees to remain in the system even if their associated theater is deleted, while still maintaining data integrity by nullifying the theater reference.
CREATE TABLE IF NOT EXISTS EMPLOYEE (
    user_id INT PRIMARY KEY,
    role VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2),
    account_status VARCHAR(50) DEFAULT 'Active',
    auth_level INT DEFAULT 1,
    work_shift VARCHAR(100),
    theater_id INT,
    FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (theater_id) REFERENCES THEATER(theater_id) ON DELETE SET NULL
);

-- ------------------------------------------------------------------------------
-- 2. WEAK ENTITIES (SALOON & SEAT)
-- ------------------------------------------------------------------------------

-- So capacity can be derived from counting the number of seats associated with a saloon, but it can also be useful to have it as a separate attribute for quick reference and to enforce constraints on seat creation.
CREATE TABLE IF NOT EXISTS SALOON (
    theater_id INT,
    number INT,
    capacity INT NOT NULL,
    type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (theater_id, number),
    FOREIGN KEY (theater_id) REFERENCES THEATER(theater_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS SEAT (
    theater_id INT,
    saloon_number INT NOT NULL,
    row_letter VARCHAR(1) NOT NULL,
    number INT NOT NULL,
    type VARCHAR(50) DEFAULT 'Standard',
    PRIMARY KEY (theater_id, saloon_number, row_letter, number),
    FOREIGN KEY (theater_id, saloon_number) REFERENCES SALOON(theater_id, number) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 3. MOVIE CATALOG & METADATA
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS MOVIE (
    movie_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    director VARCHAR(255),
    duration_mins INT NOT NULL,
    rating_age VARCHAR(10),
    release_date DATE,
    summary TEXT
);

-- The MOVIE_CAST table allows for a many-to-many relationship between movies and their cast members, as a movie can have multiple cast members and a cast member can be in multiple movies. The cast_name is stored as a VARCHAR, but in a more complex system, you might want to have a separate CAST_MEMBER table with its own unique ID and additional attributes (like date of birth, biography, etc.) for better data management and integrity.
CREATE TABLE IF NOT EXISTS MOVIE_CAST (
    movie_id INT,
    cast_name VARCHAR(255),
    PRIMARY KEY (movie_id, cast_name),
    FOREIGN KEY (movie_id) REFERENCES MOVIE(movie_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS GENRE (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- The MOVIE_GENRE table allows for a many-to-many relationship between movies and genres, as a movie can belong to multiple genres and a genre can be associated with multiple movies. This design provides flexibility in categorizing movies and allows for more complex queries (e.g., finding all movies in a specific genre or all genres associated with a specific movie).
CREATE TABLE IF NOT EXISTS MOVIE_GENRE (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES MOVIE(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES GENRE(genre_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS FORMAT (
    format_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- The MOVIE_FORMAT table allows for a many-to-many relationship between movies and formats, as a movie can be available in multiple formats (e.g., 2D, 3D, IMAX) and a format can be associated with multiple movies. This design provides flexibility in categorizing movies by their available formats and allows for more complex queries (e.g., finding all movies available in a specific format or all formats associated with a specific movie).
CREATE TABLE IF NOT EXISTS MOVIE_FORMAT (
    movie_id INT,
    format_id INT,
    PRIMARY KEY (movie_id, format_id),
    FOREIGN KEY (movie_id) REFERENCES MOVIE(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (format_id) REFERENCES FORMAT(format_id) ON DELETE CASCADE
);

-- The MOVIE_RUN table captures the scheduling of movies in the theater, allowing for multiple runs of the same movie with different start and end dates. This design provides flexibility in managing movie showtimes and allows for more complex queries (e.g., finding all movies currently running or all runs of a specific movie).
CREATE TABLE IF NOT EXISTS MOVIE_RUN (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT chk_movie_run_dates CHECK (end_date >= start_date),
    FOREIGN KEY (movie_id) REFERENCES MOVIE(movie_id) ON DELETE CASCADE
);

-- The CUSTOMER_FAVORITE_MOVIE table allows customers to mark movies as their favorites, creating a many-to-many relationship between customers and movies. This design provides flexibility in managing customer preferences and allows for more complex queries (e.g., finding all favorite movies of a specific customer or all customers who have marked a specific movie as a favorite).
CREATE TABLE IF NOT EXISTS CUSTOMER_FAVORITE_MOVIE (
    user_id INT,
    movie_id INT,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES CUSTOMER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES MOVIE(movie_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 4. BUSINESS RULES & RETAIL
-- ------------------------------------------------------------------------------

-- The DEAL table captures promotional offers that can be applied to bookings, allowing for flexibility in managing discounts and promotions. The discount_percent field allows for percentage-based discounts, while the valid_until field allows for time-limited offers. This design provides the ability to create various types of deals and apply them to customer bookings, enhancing the marketing capabilities of the cinema.
CREATE TABLE IF NOT EXISTS DEAL (
    deal_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    discount_percent DECIMAL(5,2) NOT NULL CHECK (discount_percent BETWEEN 0 AND 100),
    valid_until DATE
);

-- The CONSUMABLE table captures items that can be sold at the cinema, such as popcorn, drinks, and candy. The unit_price field allows for pricing of each consumable item, while the stock_quantity field allows for inventory management. This design provides the ability to manage consumable items effectively and integrate them into the booking process (e.g., allowing customers to add consumables to their bookings).
CREATE TABLE IF NOT EXISTS CONSUMABLE (
    consumable_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0
);

-- ------------------------------------------------------------------------------
-- 5. CORE TRANSACTIONS (SCREENING, BOOKING, TICKET, REVIEW)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS SCREENING (
    screening_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    theater_id INT NOT NULL,
    saloon_number INT NOT NULL,
    start_time DATETIME NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    is_subtitled BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (movie_id) REFERENCES MOVIE(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (theater_id, saloon_number) REFERENCES SALOON(theater_id, number) ON DELETE CASCADE
);

CREATE INDEX idx_screening_id_theater_saloon
    ON SCREENING(screening_id, theater_id, saloon_number);

CREATE INDEX idx_screening_theater_saloon_start_time
    ON SCREENING(theater_id, saloon_number, start_time);

CREATE INDEX idx_screening_movie_start_time
    ON SCREENING(movie_id, start_time);

CREATE TABLE IF NOT EXISTS BOOKING (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    deal_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES CUSTOMER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (deal_id) REFERENCES DEAL(deal_id) ON DELETE SET NULL
);

CREATE INDEX idx_booking_user_created_at
    ON BOOKING(user_id, created_at);

CREATE TABLE IF NOT EXISTS TICKET (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    screening_id INT NOT NULL,
    theater_id INT NOT NULL,
    saloon_number INT NOT NULL,
    row_letter VARCHAR(1) NOT NULL,
    seat_number INT NOT NULL,
    ticket_type VARCHAR(50) DEFAULT 'Standard',
    scanned_at DATETIME DEFAULT NULL,
    
    -- Foreign Keys to link the Ticket to the exact Seat and Screening
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (screening_id)
        REFERENCES SCREENING(screening_id) ON DELETE CASCADE,
    FOREIGN KEY (theater_id, saloon_number, row_letter, seat_number) 
        REFERENCES SEAT(theater_id, saloon_number, row_letter, number) ON DELETE CASCADE,
        
    -- UNIQUE CONSTRAINT: Prevents double-booking the exact same seat for the exact same screening!
    UNIQUE (screening_id, theater_id, saloon_number, row_letter, seat_number)
);

CREATE INDEX idx_ticket_booking_id
    ON TICKET(booking_id);

CREATE TABLE IF NOT EXISTS PAYMENT (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    method VARCHAR(50) NOT NULL DEFAULT 'Credit Card',
    status VARCHAR(50) DEFAULT 'Completed',
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE
);

CREATE TABLE BOOKING_CONSUMABLE (
    booking_id INT,
    consumable_id INT,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    PRIMARY KEY (booking_id, consumable_id),
    FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (consumable_id) REFERENCES CONSUMABLE(consumable_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS REVIEW (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    FOREIGN KEY (user_id) REFERENCES CUSTOMER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES MOVIE(movie_id) ON DELETE CASCADE
);

CREATE VIEW IF NOT EXISTS Active_Movies AS
SELECT m.movie_id, m.title, m.director, m.duration_mins, m.release_date
FROM MOVIE m
JOIN MOVIE_RUN mr ON m.movie_id = mr.movie_id
JOIN MOVIE_GENRE mg ON m.movie_id = mg.movie_id
WHERE CURRENT_DATE BETWEEN mr.start_date AND mr.end_date;

-- GROUP_CONCAT is used to aggregate multiple genres into a single comma-separated string for each movie. This allows the view to display all genres associated with each active movie in a more readable format, rather than having multiple rows for movies that belong to multiple genres.
CREATE VIEW IF NOT EXISTS Coming_Soon_Movies AS
SELECT m.movie_id, m.title, m.director, m.duration_mins, m.release_date, GROUP_CONCAT(g.name SEPARATOR ', ') AS genres
FROM MOVIE m
JOIN MOVIE_RUN mr ON m.movie_id = mr.movie_id
LEFT JOIN MOVIE_GENRE mg ON m.movie_id = mg.movie_id
LEFT JOIN GENRE g ON mg.genre_id = g.genre_id
WHERE mr.start_date > CURRENT_DATE
GROUP BY m.movie_id, m.title, m.director, m.duration_mins, m.release_date;

-- Speeds up checking if a movie is active or coming soon
CREATE INDEX idx_movierun_dates ON MOVIE_RUN(start_date, end_date);
-- Speeds up the JOIN between MOVIE and MOVIE_RUN
CREATE INDEX idx_movierun_movie_id ON MOVIE_RUN(movie_id);
-- Speeds up the "Sort by Release Date" feature on the frontend
CREATE INDEX idx_movie_release_date ON MOVIE(release_date);