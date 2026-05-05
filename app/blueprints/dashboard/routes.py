from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from werkzeug.security import check_password_hash, generate_password_hash

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
        movie["image_url"] = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80"
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
        flash("Please fill in all required profile fields.", "error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed.", "error")
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
            flash("This email is already used by another account.", "error")
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

        flash("Profile updated successfully.", "success")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    except Exception as e:
        connection.rollback()
        flash(str(e), "error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    finally:
        cursor.close()
        connection.close()

def get_user_booking_stats(user_id):
    connection = get_db_connection()
    if connection is None:
        return {
            "total_bookings": 0,
            "movies_watched": 0,
            "total_spent": 0.00
        }

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COUNT(DISTINCT b.booking_id) AS total_bookings,
            COALESCE(SUM(DISTINCT b.total_amount), 0) AS total_spent
        FROM booking b
        LEFT JOIN ticket t
            ON b.booking_id = t.booking_id
        LEFT JOIN screening s
            ON t.screening_id = s.screening_id
        LEFT JOIN payment p
            ON b.booking_id = p.booking_id
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
        JOIN ticket t
            ON b.booking_id = t.booking_id
        JOIN screening s
            ON t.screening_id = s.screening_id
        JOIN movie m
            ON s.movie_id = m.movie_id
        LEFT JOIN saloon sa
            ON s.theater_id = sa.theater_id
           AND s.saloon_number = sa.number
        LEFT JOIN payment p
            ON b.booking_id = p.booking_id
        WHERE b.user_id = %s
        GROUP BY
            b.booking_id,
            b.created_at,
            b.total_amount,
            p.status,
            m.movie_id,
            m.title,
            s.start_time,
            sa.type
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

        if hasattr(start_time, "strftime"):
            booking["date_display"] = start_time.strftime("%b %d, %Y")
            booking["time_display"] = start_time.strftime("%I:%M %p").lstrip("0")
        else:
            booking["date_display"] = str(start_time)
            booking["time_display"] = ""

        payment_status = booking.get("payment_status")

        if payment_status == "Refunded":
            booking["status"] = "Refunded"
            booking["status_class"] = "bg-gray-500/20 text-gray-400"
            booking["action"] = "none"
        elif start_time and start_time > __import__("datetime").datetime.now():
            booking["status"] = "Upcoming"
            booking["status_class"] = "bg-amber/20 text-amber"
            booking["action"] = "refund"
        else:
            booking["status"] = "Completed"
            booking["status_class"] = "bg-emerald-500/20 text-emerald-400"
            booking["action"] = "ticket"

        title = booking.get("movie_title") or "Movie"
        words = title.split()
        if len(words) >= 2:
            booking["movie_code"] = words[0][0].upper() + words[1][0].upper()
        else:
            booking["movie_code"] = title[:2].upper()

        booking["total_amount"] = float(booking["total_amount"] or 0)

    return bookings

@dashboard_bp.route("/dashboard/password", methods=["POST"], strict_slashes=False)
def update_password():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("Please fill in all password fields.", "error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    if len(new_password) < 8:
        flash("New password must be at least 8 characters.", "error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed.", "error")
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
            flash("Current password is incorrect.", "error")
            return redirect(url_for("dashboard.dashboard") + "#profile")

        cursor.execute(
            """
            UPDATE user
            SET password_hash = %s
            WHERE user_id = %s
            """,
            (generate_password_hash(new_password), session["user_id"])
        )

        connection.commit()
        flash("Password updated successfully.", "success")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    except Exception as e:
        connection.rollback()
        flash(str(e), "error")
        return redirect(url_for("dashboard.dashboard") + "#profile")

    finally:
        cursor.close()
        connection.close()