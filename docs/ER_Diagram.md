erDiagram
    %% --- ISA HIERARCHY (USER / CUSTOMER / EMPLOYEE) ---
    USER ||--o| CUSTOMER : "ISA"
    USER ||--o| EMPLOYEE : "ISA"
    
    USER {
        int user_id PK
        string first_name
        string last_name
        string phone_number
        string email
        string password
        datetime created_at
    }
    CUSTOMER {
        int user_id PK, FK
        date birth_date
        int loyalty_points
        string membership_tier
    }
    EMPLOYEE {
        int user_id PK, FK
        string role
        decimal salary
        string account_status
        int auth_level
        string work_shift
        int theater_id FK
    }

    %% --- THEATER & WEAK ENTITIES (SALOON, SEAT) ---
    THEATER ||--o{ SALOON : "has"
    SALOON ||--o{ SEAT : "contains"
    THEATER ||--o{ EMPLOYEE : "works_at"

    THEATER {
        int theater_id PK
        string name
        string phone_number
        string address
    }
    SALOON {
        int theater_id PK, FK
        int number PK
        int capacity
        string type
        boolean isActive
    }
    SEAT {
        int theater_id PK, FK
        int saloon_number PK, FK
        string row_letter PK
        int number PK
        string type
    }

    %% --- MOVIE & METADATA ---
    MOVIE ||--o{ MOVIE_CAST : "has"
    GENRE ||--o{ MOVIE_GENRE : "of"
    MOVIE ||--o{ MOVIE_GENRE : "of"
    FORMAT ||--o{ MOVIE_FORMAT : "with"
    MOVIE ||--o{ MOVIE_FORMAT : "with"
    MOVIE ||--o{ MOVIE_RUN : "plays"
    CUSTOMER ||--o{ CUSTOMER_FAVORITE_MOVIE : "favorites"
    MOVIE ||--o{ CUSTOMER_FAVORITE_MOVIE : "favorites"

    MOVIE {
        int movie_id PK
        string title
        string director
        int duration_mins
        string rating_age
        date release_date
        string summary
    }
    MOVIE_CAST {
        int movie_id PK, FK
        string cast_name PK
    }
    GENRE {
        int genre_id PK
        string name
    }
    MOVIE_GENRE {
        int movie_id PK, FK
        int genre_id PK, FK
    }
    FORMAT {
        int format_id PK
        string name
    }
    MOVIE_FORMAT {
        int movie_id PK, FK
        int format_id PK, FK
    }
    MOVIE_RUN {
        int run_id PK
        int movie_id FK
        date start_date
        date end_date
    }
    CUSTOMER_FAVORITE_MOVIE {
        int user_id PK, FK
        int movie_id PK, FK
    }

    %% --- TRANSACTIONS (BOOKING, SCREENING, TICKET, REVIEW) ---
    MOVIE ||--o{ SCREENING : "shows"
    SALOON ||--o{ SCREENING : "takes_place_in"
    CUSTOMER ||--o{ BOOKING : "makes"
    BOOKING ||--|{ TICKET : "contains"
    BOOKING ||--|| PAYMENT : "via"
    DEAL ||--o{ BOOKING : "applies_to"
    CUSTOMER ||--o{ REVIEW : "submit"
    MOVIE ||--o{ REVIEW : "of"

    SCREENING {
        int screening_id PK
        int movie_id FK
        int theater_id FK
        int saloon_number FK
        datetime start_time
        decimal base_price
        boolean isSubtitled
    }
    BOOKING {
        int booking_id PK
        int user_id FK
        int deal_id FK
        datetime timestamp
        decimal total_amount
    }
    TICKET {
        int ticket_id PK
        int booking_id FK
        int screening_id FK
        int seat_row_letter
        int seat_number
        string ticket_type
    }
    PAYMENT {
        int payment_id PK
        int booking_id FK
        string method
        string status
    }
    DEAL {
        int deal_id PK
        string name
        decimal discount_percent
        date valid_until
    }
    REVIEW {
        int review_id PK
        int user_id FK
        int movie_id FK
        int rating
        string comment
    }

    %% --- RETAIL (CONSUMABLES) ---
    BOOKING ||--o{ BOOKING_CONSUMABLE : "added"
    CONSUMABLE ||--o{ BOOKING_CONSUMABLE : "added"

    CONSUMABLE {
        int consumable_id PK
        string name
        decimal unit_price
        int stock_quantity
    }
    BOOKING_CONSUMABLE {
        int booking_id PK, FK
        int consumable_id PK, FK
        int quantity
    }
