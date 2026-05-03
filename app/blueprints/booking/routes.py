from flask import Blueprint, render_template, request, abort, jsonify, session
from app.db import get_db_connection



booking_bp = Blueprint("booking", __name__)


def fetch_movie_for_booking(movie_id):
    connection = get_db_connection()

    if connection is None:
        abort(500)

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            movie_id AS id,
            title,
            director,
            duration_mins AS duration,
            rating_age,
            release_date,
            summary AS synopsis
        FROM movie
        WHERE movie_id = %s
    """

    cursor.execute(query, (movie_id,))
    movie = cursor.fetchone()

    cursor.close()
    connection.close()

    if movie is None:
        abort(404)

    movie["runtime_label"] = str(movie["duration"]) + " min"
    movie["image_url"] = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80"

    return movie


def fetch_screenings_for_movie(movie_id):
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            s.screening_id,
            s.movie_id,
            s.theater_id,
            t.name AS theater_name,
            t.address AS theater_address,
            s.saloon_number,
            sa.capacity AS saloon_capacity,
            sa.type AS saloon_type,
            s.start_time,
            s.base_price,
            s.is_subtitled
        FROM screening s
        JOIN theater t
            ON s.theater_id = t.theater_id
        JOIN saloon sa
            ON s.theater_id = sa.theater_id
           AND s.saloon_number = sa.number
        WHERE s.movie_id = %s
          AND s.start_time >= NOW()
        ORDER BY s.start_time ASC
    """

    cursor.execute(query, (movie_id,))
    screenings = cursor.fetchall()

    cursor.close()
    connection.close()

    return screenings


def group_screenings_by_theater(screenings):
    grouped = {}

    for screening in screenings:
        theater_id = screening["theater_id"]

        if theater_id not in grouped:
            grouped[theater_id] = {
                "theater_id": theater_id,
                "theater_name": screening["theater_name"],
                "theater_address": screening["theater_address"],
                "screenings": []
            }

        grouped[theater_id]["screenings"].append(screening)

    return list(grouped.values())


@booking_bp.route("/booking")
def booking():
    movie_id = request.args.get("movie_id", type=int)

    if movie_id is None:
        abort(400)

    movie = fetch_movie_for_booking(movie_id)
    screenings = fetch_screenings_for_movie(movie_id)
    consumables = fetch_consumables()
    theaters_with_screenings = group_screenings_by_theater(screenings)

    for screening in screenings:
        if hasattr(screening["start_time"], "strftime"):
            screening["start_time_display"] = screening["start_time"].strftime("%Y-%m-%d %H:%M")
        else:
            screening["start_time_display"] = str(screening["start_time"])

        screening["base_price"] = float(screening["base_price"])

    return render_template(
        "booking/booking.html",
        movie_id=movie_id,
        movie=movie,
        screenings=screenings,
        theaters_with_screenings=theaters_with_screenings,
        consumables = consumables
    )

def fetch_screening_detail(screening_id):
    connection = get_db_connection()

    if connection is None:
        abort(500)

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            s.screening_id,
            s.movie_id,
            m.title AS movie_title,
            m.duration_mins,
            s.theater_id,
            t.name AS theater_name,
            t.address AS theater_address,
            s.saloon_number,
            sa.capacity AS saloon_capacity,
            sa.type AS saloon_type,
            s.start_time,
            s.base_price,
            s.is_subtitled
        FROM screening s
        JOIN movie m
            ON s.movie_id = m.movie_id
        JOIN theater t
            ON s.theater_id = t.theater_id
        JOIN saloon sa
            ON s.theater_id = sa.theater_id
           AND s.saloon_number = sa.number
        WHERE s.screening_id = %s
    """

    cursor.execute(query, (screening_id,))
    screening = cursor.fetchone()

    cursor.close()
    connection.close()

    if screening is None:
        abort(404)

    return screening


def fetch_seats_for_screening(screening):
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            seat.row_letter,
            seat.number AS seat_number,
            seat.type AS seat_type,
            CASE
                WHEN ticket.ticket_id IS NULL THEN 0
                ELSE 1
            END AS is_occupied
        FROM seat
        LEFT JOIN ticket
            ON seat.theater_id = ticket.theater_id
           AND seat.saloon_number = ticket.saloon_number
           AND seat.row_letter = ticket.row_letter
           AND seat.number = ticket.seat_number
           AND ticket.screening_id = %s
        WHERE seat.theater_id = %s
          AND seat.saloon_number = %s
        ORDER BY seat.row_letter ASC, seat.number ASC
    """

    cursor.execute(
        query,
        (
            screening["screening_id"],
            screening["theater_id"],
            screening["saloon_number"]
        )
    )

    seats = cursor.fetchall()

    cursor.close()
    connection.close()

    return seats


def group_seats_by_row(seats):
    grouped = {}

    for seat in seats:
        row_letter = seat["row_letter"]

        if row_letter not in grouped:
            grouped[row_letter] = []

        grouped[row_letter].append(seat)

    return grouped

@booking_bp.route("/booking/seats/<int:screening_id>")
def select_seats(screening_id):
    screening = fetch_screening_detail(screening_id)
    seats = fetch_seats_for_screening(screening)
    seats_by_row = group_seats_by_row(seats)

    return render_template(
        "booking/seats.html",
        screening=screening,
        seats=seats,
        seats_by_row=seats_by_row
    )


@booking_bp.route("/booking/create", methods=["POST"])
def create_booking():
    print("BOOKING CREATE ROUTE CALLED")
    print("SESSION USER ID:", session.get("user_id"))
    print("REQUEST JSON:", request.get_json())
    data = request.get_json()

    screening_id = data.get("screening_id")
    selected_seats = data.get("selected_seats")
    selected_consumables = data.get("consumables", {})
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "success": False,
            "message": "Please login before booking."
        }), 401
    if not screening_id or not selected_seats:
        return jsonify({
            "success": False,
            "message": "screening_id and selected_seats are required"
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed"
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        # 1. Seans bilgisini al
        cursor.execute(
            """
            SELECT
                screening_id,
                theater_id,
                saloon_number,
                base_price
            FROM screening
            WHERE screening_id = %s
            """,
            (screening_id,)
        )

        screening = cursor.fetchone()

        if screening is None:
            return jsonify({
                "success": False,
                "message": "Screening not found"
            }), 404

        theater_id = screening["theater_id"]
        saloon_number = screening["saloon_number"]
        base_price = float(screening["base_price"])

        ticket_total = base_price * len(selected_seats)
        consumable_total = 0

        consumable_name_map = {
            "popcorn": "Large Popcorn",
            "soda": "Large Soda",
            "candy": "Candy Box",
            "hotdog": "Hot Dog"
        }

        selected_consumable_rows = []

        for item_key, quantity in selected_consumables.items():
            quantity = int(quantity)

            if quantity <= 0:
                continue

            consumable_name = consumable_name_map.get(item_key)

            if consumable_name is None:
                continue

            cursor.execute(
                """
                SELECT consumable_id,
                       name,
                       unit_price,
                       stock_quantity
                FROM consumable
                WHERE name = %s
                """,
                (consumable_name,)
            )

            consumable = cursor.fetchone()

            if consumable is None:
                connection.rollback()
                return jsonify({
                    "success": False,
                    "message": f"Consumable not found: {consumable_name}"
                }), 404

            if consumable["stock_quantity"] < quantity:
                connection.rollback()
                return jsonify({
                    "success": False,
                    "message": f"Not enough stock for {consumable_name}"
                }), 409

            unit_price = float(consumable["unit_price"])
            consumable_total += unit_price * quantity

            selected_consumable_rows.append({
                "consumable_id": consumable["consumable_id"],
                "quantity": quantity
            })

        service_fee = 2.50
        total_amount = ticket_total + consumable_total + service_fee

        # 2. Seçilen koltuklardan biri daha önce alınmış mı kontrol et
        for seat in selected_seats:
            row_letter = seat.get("row")
            seat_number = seat.get("number")

            cursor.execute(
                """
                SELECT ticket_id
                FROM ticket
                WHERE screening_id = %s
                  AND row_letter = %s
                  AND seat_number = %s
                """,
                (screening_id, row_letter, seat_number)
            )

            existing_ticket = cursor.fetchone()

            if existing_ticket:
                connection.rollback()
                return jsonify({
                    "success": False,
                    "message": f"Seat {row_letter}{seat_number} is already occupied"
                }), 409

        # 3. Booking kaydı oluştur
        cursor.execute(
            """
            INSERT INTO booking
            (user_id, deal_id, created_at, total_amount)
            VALUES (%s, NULL, NOW(), %s)
            """,
            (user_id, total_amount)
        )

        booking_id = cursor.lastrowid

        for item in selected_consumable_rows:
            cursor.execute(
                """
                INSERT INTO booking_consumable
                    (booking_id, consumable_id, quantity)
                VALUES (%s, %s, %s)
                """,
                (
                    booking_id,
                    item["consumable_id"],
                    item["quantity"]
                )
            )

            cursor.execute(
                """
                UPDATE consumable
                SET stock_quantity = stock_quantity - %s
                WHERE consumable_id = %s
                """,
                (
                    item["quantity"],
                    item["consumable_id"]
                )
            )

        # 4. Her seçilen koltuk için ticket kaydı oluştur
        for seat in selected_seats:
            row_letter = seat.get("row")
            seat_number = seat.get("number")

            cursor.execute(
                """
                INSERT INTO ticket
                (
                    booking_id,
                    screening_id,
                    theater_id,
                    saloon_number,
                    row_letter,
                    seat_number,
                    ticket_type,
                    scanned_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
                """,
                (
                    booking_id,
                    screening_id,
                    theater_id,
                    saloon_number,
                    row_letter,
                    seat_number,
                    "Standard"
                )
            )

        # 5. Payment kaydı oluştur
        cursor.execute(
            """
            INSERT INTO payment
            (booking_id, method, status)
            VALUES (%s, %s, %s)
            """,
            (booking_id, "Credit Card", "Paid")
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Booking created successfully",
            "booking_id": booking_id,
            "total_amount": total_amount
        }), 201

    except Exception as e:
        connection.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()


@booking_bp.route("/booking/occupied-seats/<int:screening_id>")
def get_occupied_seats(screening_id):
            connection = get_db_connection()

            if connection is None:
                return jsonify({
                    "success": False,
                    "message": "Database connection failed"
                }), 500

            cursor = connection.cursor(dictionary=True)

            try:
                cursor.execute(
                    """
                    SELECT row_letter,
                           seat_number
                    FROM ticket
                    WHERE screening_id = %s
                    """,
                    (screening_id,)
                )

                occupied_seats = cursor.fetchall()

                formatted_seats = []

                for seat in occupied_seats:
                    formatted_seats.append(
                        seat["row_letter"] + str(seat["seat_number"])
                    )

                return jsonify({
                    "success": True,
                    "occupied_seats": formatted_seats
                }), 200

            finally:
                cursor.close()
                connection.close()

def fetch_active_deals():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            deal_id,
            name,
            discount_percent,
            valid_until
        FROM deal
        WHERE valid_until >= CURDATE()
        ORDER BY discount_percent DESC
        """
    )

    deals = cursor.fetchall()

    cursor.close()
    connection.close()

    for deal in deals:
        deal["discount_percent"] = float(deal["discount_percent"])

        if hasattr(deal["valid_until"], "strftime"):
            deal["valid_until"] = deal["valid_until"].strftime("%Y-%m-%d")
        else:
            deal["valid_until"] = str(deal["valid_until"])

    return deals

def fetch_consumables():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            consumable_id,
            name,
            unit_price,
            stock_quantity
        FROM consumable
        ORDER BY consumable_id
        """
    )

    consumables = cursor.fetchall()

    cursor.close()
    connection.close()

    for item in consumables:
        item["unit_price"] = float(item["unit_price"])

    return consumables