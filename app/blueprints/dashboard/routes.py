from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

from app.db import get_db_connection

dashboard_bp = Blueprint("dashboard", __name__)


def get_user_favorite_movies(user_id):
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT
            m.movie_id AS id,
            m.title,
            m.duration_mins AS duration,
            m.rating_age,
            m.release_date,
            m.summary AS synopsis,
            m.poster_url,
            GROUP_CONCAT(DISTINCT g.name SEPARATOR ', ') AS genres,
            GROUP_CONCAT(DISTINCT f.name SEPARATOR ', ') AS format
        FROM CUSTOMER_FAVORITE_MOVIE cfm
        JOIN MOVIE m ON cfm.movie_id = m.movie_id
        LEFT JOIN MOVIE_GENRE mg ON m.movie_id = mg.movie_id
        LEFT JOIN GENRE g ON mg.genre_id = g.genre_id
        LEFT JOIN MOVIE_FORMAT mf ON m.movie_id = mf.movie_id
        LEFT JOIN FORMAT f ON mf.format_id = f.format_id
        WHERE cfm.user_id = %s
        GROUP BY m.movie_id
        ORDER BY m.title ASC
    """
    cursor.execute(query, (user_id,))
    movies = cursor.fetchall()
    cursor.close()
    connection.close()

    for movie in movies:
        movie["runtime_label"] = str(movie["duration"]) + " min" if movie["duration"] else "TBA"
        movie["avg_rating"] = 0
        movie["is_favorited"] = True

    return movies


def get_current_user_profile(user_id):
    connection = get_db_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            u.user_id,
            u.first_name,
            u.last_name,
            u.email,
            u.phone_number,
            u.password_hash,
            c.birth_date,
            c.membership_tier
        FROM user u
        LEFT JOIN customer c ON u.user_id = c.user_id
        WHERE u.user_id = %s
        """,
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        first_initial = user["first_name"][0].upper() if user.get("first_name") else ""
        last_initial = user["last_name"][0].upper() if user.get("last_name") else ""
        user["initials"] = first_initial + last_initial

    return user


@dashboard_bp.route("/dashboard", strict_slashes=False)
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    user = get_current_user_profile(user_id)
    favorite_movies = get_user_favorite_movies(user_id)
    booking_stats = get_user_booking_stats(user_id)
    recent_bookings = get_user_recent_bookings(user_id)

    return render_template(
        "dashboard/dashboard.html",
        user=user,
        user_name=session.get("user_name", "User"),
        favorite_movies=favorite_movies,
        booking_stats=booking_stats,
        recent_bookings=recent_bookings
    )


@dashboard_bp.route("/dashboard/profile", methods=["POST"], strict_slashes=False)
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    phone_number = request.form.get("phone_number", "").strip()
    birth_date = request.form.get("birth_date", "").strip()

    if not first_name or not last_name or not email:
        flash("Please fill in all required profile fields.", "profile_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed.", "profile_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT user_id
            FROM user
            WHERE email = %s AND user_id != %s
            """,
            (email, session["user_id"])
        )
        existing_user = cursor.fetchone()

        if existing_user:
            flash("This email is already used by another account.", "profile_error")
            return redirect(url_for("dashboard.dashboard") + "#profile")

        cursor.execute(
            """
            UPDATE user
            SET first_name = %s,
                last_name = %s,
                email = %s,
                phone_number = %s
            WHERE user_id = %s
            """,
            (first_name, last_name, email, phone_number, session["user_id"])
        )

        cursor.execute(
            """
            UPDATE customer
            SET birth_date = %s
            WHERE user_id = %s
            """,
            (birth_date or None, session["user_id"])
        )

        connection.commit()
        session["user_name"] = first_name

        flash("Profile updated successfully.", "profile_success")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    except Exception as e:
        connection.rollback()
        flash(str(e), "profile_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    finally:
        cursor.close()
        connection.close()

def get_user_booking_stats(user_id):
    connection = get_db_connection()
    if connection is None:
        return {"total_bookings": 0, "total_spent": 0.00}

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            COUNT(b.booking_id) AS total_bookings,
            COALESCE(SUM(b.total_amount), 0) AS total_spent
        FROM booking b
        LEFT JOIN payment p ON b.booking_id = p.booking_id
        WHERE b.user_id = %s
          AND (p.status IS NULL OR p.status != 'Refunded')
        """,
        (user_id,)
    )
    stats = cursor.fetchone()
    cursor.close()
    connection.close()
    return {
        "total_bookings": stats["total_bookings"] or 0,
        "total_spent": float(stats["total_spent"] or 0)
    }


def get_user_recent_bookings(user_id):
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            b.booking_id,
            b.booking_code,
            b.created_at,
            b.total_amount,
            p.status AS payment_status,
            m.movie_id,
            m.title AS movie_title,
            s.start_time,
            sa.type AS saloon_type,
            GROUP_CONCAT(
                CONCAT(t.row_letter, t.seat_number)
                ORDER BY t.row_letter ASC, t.seat_number ASC
                SEPARATOR ', '
            ) AS seats
        FROM booking b
        LEFT JOIN payment p ON b.booking_id = p.booking_id
        LEFT JOIN screening s ON b.screening_id = s.screening_id
        LEFT JOIN movie m ON s.movie_id = m.movie_id
        LEFT JOIN saloon sa
            ON s.theater_id = sa.theater_id
           AND s.saloon_number = sa.number
        LEFT JOIN ticket t ON b.booking_id = t.booking_id
        WHERE b.user_id = %s
        GROUP BY
            b.booking_id, b.booking_code, b.created_at, b.total_amount,
            p.status, m.movie_id, m.title, s.start_time, sa.type
        ORDER BY b.created_at DESC
        LIMIT 10
        """,
        (user_id,)
    )

    bookings = cursor.fetchall()
    cursor.close()
    connection.close()

    for booking in bookings:
        start_time = booking["start_time"]

        if start_time and hasattr(start_time, "strftime"):
            booking["date_display"] = start_time.strftime("%b %d, %Y")
            booking["time_display"] = start_time.strftime("%I:%M %p").lstrip("0")
        else:
            booking["date_display"] = "—"
            booking["time_display"] = ""

        payment_status = booking.get("payment_status")

        if payment_status == "Refunded":
            booking["status"] = "Refunded"
            booking["status_class"] = "bg-gray-500/20 text-gray-400"
            booking["action"] = "none"
        elif start_time and start_time > datetime.now():
            booking["status"] = "Upcoming"
            booking["status_class"] = "bg-amber/20 text-amber"
            booking["action"] = "refund"
        else:
            booking["status"] = "Completed"
            booking["status_class"] = "bg-emerald-500/20 text-emerald-400"
            booking["action"] = "ticket"

        title = booking.get("movie_title") or "Movie"
        words = title.split()
        booking["movie_code"] = (
            words[0][0].upper() + words[1][0].upper() if len(words) >= 2 else title[:2].upper()
        )

        booking["total_amount"] = float(booking["total_amount"] or 0)
        booking["booking_code"] = booking.get("booking_code") or booking["booking_id"]

    return bookings

@dashboard_bp.route("/dashboard/password", methods=["POST"], strict_slashes=False)
def update_password():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("Please fill in all password fields.", "password_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    if new_password != confirm_password:
        flash("New passwords do not match.", "password_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    if len(new_password) < 8:
        flash("New password must be at least 8 characters.", "password_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed.", "password_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT password_hash
            FROM user
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )
        user = cursor.fetchone()

        if user is None or not check_password_hash(user["password_hash"], current_password):
            flash("Current password is incorrect.", "password_error")
            return redirect(url_for("dashboard.dashboard") + "#profile")

        cursor.execute(
            """
            UPDATE user
            SET password_hash = %s
            WHERE user_id = %s
            """,
            (generate_password_hash(new_password), session["user_id"])
        )

        if cursor.rowcount != 1:
            connection.rollback()
            flash("Password update could not be completed. Please try again.", "password_error")
            return redirect(url_for("dashboard.dashboard") + "#profile")

        connection.commit()
        flash("Password updated successfully.", "password_success")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    except Exception as e:
        connection.rollback()
        print("Dashboard password update error:", e)
        flash("An unexpected error occurred while updating password.", "password_error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    finally:
        cursor.close()
        connection.close()


@dashboard_bp.route("/dashboard/booking-tickets/<int:booking_id>", strict_slashes=False)
def get_booking_tickets(booking_id):
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT b.booking_id, b.booking_code, b.total_amount,
                   m.title AS movie_name, s.start_time, s.base_price
            FROM booking b
            JOIN screening s ON b.screening_id = s.screening_id
            JOIN movie m ON s.movie_id = m.movie_id
            WHERE b.booking_id = %s AND b.user_id = %s
            """,
            (booking_id, session["user_id"])
        )
        booking = cursor.fetchone()

        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        start = booking["start_time"]
        one_hour_before = start - timedelta(hours=1)
        if datetime.now() >= one_hour_before:
            return jsonify({"error": "Refund window has closed (must request at least 1 hour before screening)"}), 403

        cursor.execute(
            """
            SELECT ticket_code, row_letter, seat_number
            FROM ticket
            WHERE booking_id = %s
            ORDER BY row_letter, seat_number
            """,
            (booking_id,)
        )
        tickets = [
            {"ticket_code": t["ticket_code"], "seat": f"{t['row_letter']}{t['seat_number']}"}
            for t in cursor.fetchall()
        ]

        return jsonify({
            "booking_code":  booking.get("booking_code") or booking_id,
            "movie":         booking["movie_name"],
            "start_display": start.strftime("%b %d, %Y • %I:%M %p").lstrip("0") if hasattr(start, "strftime") else str(start),
            "total_amount":  float(booking["total_amount"]),
            "base_price":    float(booking["base_price"]),
            "tickets":       tickets,
        })
    finally:
        cursor.close()
        conn.close()


@dashboard_bp.route("/dashboard/refund", methods=["POST"], strict_slashes=False)
def process_refund():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.get_json()
    ticket_codes = data.get("ticket_codes", []) if data else []
    reason = (data.get("reason") or "").strip() if data else ""

    if not ticket_codes:
        return jsonify({"success": False, "message": "No tickets selected"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        placeholders = ", ".join(["%s"] * len(ticket_codes))
        cursor.execute(
            f"""
            SELECT t.ticket_id, t.ticket_code, t.booking_id,
                   t.row_letter, t.seat_number, s.start_time, s.base_price
            FROM ticket t
            JOIN booking b ON t.booking_id = b.booking_id
            JOIN screening s ON t.screening_id = s.screening_id
            WHERE t.ticket_code IN ({placeholders}) AND b.user_id = %s
            """,
            (*ticket_codes, session["user_id"])
        )
        validated = cursor.fetchall()

        if len(validated) != len(ticket_codes):
            return jsonify({"success": False, "message": "One or more tickets not found or not yours"}), 404

        start_time     = validated[0]["start_time"]
        one_hour_before = start_time - timedelta(hours=1)
        if datetime.now() >= one_hour_before:
            return jsonify({"success": False, "message": "Refund window has closed (must request at least 1 hour before screening)"}), 403

        booking_id    = validated[0]["booking_id"]
        base_price    = float(validated[0]["base_price"])
        refund_amount = base_price * len(validated)

        ids_to_delete = [t["ticket_id"] for t in validated]
        del_ph = ", ".join(["%s"] * len(ids_to_delete))
        cursor.execute(f"DELETE FROM ticket WHERE ticket_id IN ({del_ph})", ids_to_delete)

        cursor.execute(
            "UPDATE booking SET total_amount = GREATEST(0, total_amount - %s) WHERE booking_id = %s",
            (refund_amount, booking_id)
        )

        cursor.execute("SELECT COUNT(*) AS remaining FROM ticket WHERE booking_id = %s", (booking_id,))
        remaining = cursor.fetchone()["remaining"]
        if remaining == 0:
            cursor.execute("UPDATE payment SET status = 'Refunded' WHERE booking_id = %s", (booking_id,))

        conn.commit()
        return jsonify({"success": True, "message": "Refund processed successfully"}), 200

    except Exception as e:
        print(f"Customer refund error: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"success": False, "message": "Error processing refund"}), 500

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass