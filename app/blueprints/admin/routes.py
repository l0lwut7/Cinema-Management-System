import os
import time as _time

from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from math import ceil
from app.db import get_db_connection

_POSTER_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'uploads', 'posters')
_ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

SALOON_LAYOUTS = {
    "small":  {"label": "Standard Small",  "capacity": 40,  "rows": 4,  "cols": 10, "type": "Standard"},
    "medium": {"label": "Standard Medium", "capacity": 80,  "rows": 8,  "cols": 10, "type": "Standard"},
    "large":  {"label": "IMAX Large",      "capacity": 150, "rows": 10, "cols": 15, "type": "IMAX"},
}

def _round_up_half_hour(dt):
    """Round a datetime UP to the nearest :00 or :30 boundary.

    Examples
    --------
    16:00 → 16:00   16:01 → 16:30   16:30 → 16:30   16:31 → 17:00
    """
    total_mins = dt.hour * 60 + dt.minute
    rounded = ceil(total_mins / 30) * 30
    return dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=rounded)

def _save_poster(file):
    """Save an uploaded poster file; return the URL path or None."""
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in _ALLOWED_IMAGE_EXT:
        return None
    os.makedirs(_POSTER_FOLDER, exist_ok=True)
    fname = f"{secure_filename(file.filename.rsplit('.', 1)[0])}_{int(_time.time())}.{ext}"
    file.save(os.path.join(_POSTER_FOLDER, fname))
    return f"/static/uploads/posters/{fname}"


admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/login", methods=["GET", "POST"], strict_slashes=False)
def login():
    if request.method == "GET":
        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for("admin.login"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.login"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                u.user_id,
                u.first_name,
                u.last_name,
                u.email,
                u.password_hash,
                e.role,
                e.account_status,
                e.auth_level
            FROM user u
            JOIN employee e ON u.user_id = e.user_id
            WHERE u.email = %s
            """,
            (username,)
        )

        admin_user = cursor.fetchone()

        if admin_user is None:
            flash("Invalid credentials", "error")
            return redirect(url_for("admin.login"))

        if admin_user["account_status"] != "Active":
            flash("This employee account is not active.", "error")
            return redirect(url_for("admin.login"))

        auth_level = int(admin_user["auth_level"])

        if auth_level < 3:
            flash("You do not have admin access.", "error")
            return redirect(url_for("admin.login"))

        if not check_password_hash(admin_user["password_hash"], password):
            flash("Invalid credentials", "error")
            return redirect(url_for("admin.login"))

        session["admin_id"] = admin_user["user_id"]
        session["admin_name"] = admin_user["first_name"]
        session["admin_role"] = admin_user["role"]
        session["admin_auth_level"] = admin_user["auth_level"]

        return redirect(url_for("admin.dashboard"))

    finally:
        cursor.close()
        connection.close()

@admin_bp.route("/admin/logout", strict_slashes=False)
def logout():
    session.pop("admin_id", None)
    session.pop("admin_name", None)
    session.pop("admin_role", None)
    session.pop("admin_auth_level", None)

    return redirect(url_for("admin.login"))

_VALID_PERIODS = {"today", "this_week", "this_month", "this_year", "all_time"}

def _parse_period(value, default):
    return value if value in _VALID_PERIODS else default

@admin_bp.route("/admin/dashboard", strict_slashes=False)
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    revenue_filter  = _parse_period(request.args.get("revenue_filter"),  "this_month")
    occupancy_filter = _parse_period(request.args.get("occupancy_filter"), "this_week")
    tickets_filter  = _parse_period(request.args.get("tickets_filter"),  "this_month")

    return render_template(
        "admin/dashboard.html",
        analytics_summary=fetch_analytics_summary(revenue_filter, occupancy_filter, tickets_filter),
        revenue_by_theater=fetch_revenue_by_theater(),
        vip_spenders=fetch_vip_spenders(),
        employees=fetch_employees(),
        movies=fetch_movies_for_admin(),
        upcoming_screenings=fetch_upcoming_screenings(),
        saloons=fetch_saloons(),
        consumables=fetch_consumables(),
        deals=fetch_deals(),
        vip_tier=get_vip_tier_info(),
        genres=fetch_genres(),
        formats=fetch_formats(),
        theaters=fetch_theaters(),
        saloon_layouts=SALOON_LAYOUTS,
        initial_tab=request.args.get("tab", "analytics"),
        current_admin_id=session.get("admin_id"),
        revenue_filter=revenue_filter,
        occupancy_filter=occupancy_filter,
        tickets_filter=tickets_filter,
    )

@admin_bp.route("/admin/api/analytics", strict_slashes=False)
def api_analytics():
    if "admin_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    revenue_filter  = _parse_period(request.args.get("revenue_filter"),  "this_month")
    occupancy_filter = _parse_period(request.args.get("occupancy_filter"), "this_week")
    tickets_filter  = _parse_period(request.args.get("tickets_filter"),  "this_month")

    return jsonify({
        "summary": fetch_analytics_summary(revenue_filter, occupancy_filter, tickets_filter),
        "chart": fetch_revenue_by_theater()
    })

@admin_bp.route("/admin/screenings/add", methods=["POST"], strict_slashes=False)
def add_screening():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    movie_id = request.form.get("movie_id", "").strip()
    saloon_value = request.form.get("saloon_value", "").strip()
    screening_date = request.form.get("screening_date", "").strip()
    screening_time = request.form.get("screening_time", "").strip()
    base_price = request.form.get("base_price", "").strip()
    is_subtitled = 1 if request.form.get("is_subtitled") == "on" else 0

    if not movie_id or not saloon_value or not screening_date or not screening_time or not base_price:
        flash("Please fill all required screening fields.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    try:
        theater_id, saloon_number = saloon_value.split("|")
        movie_id = int(movie_id)
        theater_id = int(theater_id)
        saloon_number = int(saloon_number)
        base_price = float(base_price)
        start_time = datetime.strptime(
            f"{screening_date} {screening_time}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        flash("Invalid screening data.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    if start_time <= datetime.now():
        flash("Screening date and time must be in the future.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    cursor = connection.cursor(dictionary=True)

    try:
        # ── 1. Validate movie exists and is schedulable ───────────────────────
        cursor.execute(
            """
            SELECT movie_id, visibility_status, duration_mins
            FROM movie
            WHERE movie_id = %s
            """,
            (movie_id,)
        )
        movie = cursor.fetchone()

        if not movie:
            flash("Selected movie does not exist.", "error")
            return redirect(url_for("admin.dashboard", tab="infrastructure"))

        if movie["visibility_status"] == "coming_soon":
            flash(
                "Cannot schedule screenings for a 'Coming Soon' movie. "
                "Change its visibility to 'Now Showing' or 'Catalog Only' first.",
                "error"
            )
            return redirect(url_for("admin.dashboard", tab="infrastructure"))

        # ── 2. Validate saloon is active ──────────────────────────────────────
        cursor.execute(
            """
            SELECT theater_id, number
            FROM saloon
            WHERE theater_id = %s AND number = %s AND is_active = 1
            """,
            (theater_id, saloon_number)
        )
        saloon = cursor.fetchone()

        if not saloon:
            flash("Selected saloon does not exist or is inactive.", "error")
            return redirect(url_for("admin.dashboard", tab="infrastructure"))

        # ── 3. Overlap detection with 30-minute rounding rule ─────────────────
        # Compute the blocked window for the new screening.
        new_end_raw = start_time + timedelta(minutes=int(movie["duration_mins"]))
        new_blocked_until = _round_up_half_hour(new_end_raw)

        # Fetch all existing screenings in the same saloon on the same calendar day.
        cursor.execute(
            """
            SELECT s.start_time, m.duration_mins
            FROM screening s
            JOIN movie m ON s.movie_id = m.movie_id
            WHERE s.theater_id = %s
              AND s.saloon_number = %s
              AND DATE(s.start_time) = %s
            """,
            (theater_id, saloon_number, start_time.date())
        )
        existing_screenings = cursor.fetchall()

        for ex in existing_screenings:
            ex_start = ex["start_time"]
            ex_end_raw = ex_start + timedelta(minutes=int(ex["duration_mins"]))
            ex_blocked_until = _round_up_half_hour(ex_end_raw)

            # Standard interval overlap: [A_start, A_end) ∩ [B_start, B_end) ≠ ∅
            # iff A_start < B_end AND B_start < A_end
            if start_time < ex_blocked_until and ex_start < new_blocked_until:
                flash(
                    f"Saloon conflict: an existing screening runs from "
                    f"{ex_start.strftime('%H:%M')} and blocks the saloon until "
                    f"{ex_blocked_until.strftime('%H:%M')} "
                    f"(movie duration + 30-min rounding). "
                    f"The earliest next slot is {ex_blocked_until.strftime('%H:%M')}.",
                    "error"
                )
                return redirect(url_for("admin.dashboard", tab="infrastructure"))

        # ── 4. Insert screening ───────────────────────────────────────────────
        cursor.execute(
            """
            INSERT INTO screening
                (movie_id, theater_id, saloon_number, start_time, base_price, is_subtitled)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            (
                movie_id,
                theater_id,
                saloon_number,
                start_time,
                base_price,
                is_subtitled
            )
        )

        # Keep movie_run in sync for backward compatibility.
        screening_date_only = start_time.date()
        cursor.execute(
            "SELECT start_date, end_date FROM movie_run WHERE movie_id = %s",
            (movie_id,)
        )
        existing_run = cursor.fetchone()

        if not existing_run:
            cursor.execute(
                """
                INSERT INTO movie_run (movie_id, start_date, end_date)
                VALUES (%s, %s, %s)
                """,
                (movie_id, screening_date_only, screening_date_only)
            )
        else:
            cursor.execute(
                """
                UPDATE movie_run
                SET start_date = LEAST(start_date, %s),
                    end_date   = GREATEST(end_date, %s)
                WHERE movie_id = %s
                """,
                (screening_date_only, screening_date_only, movie_id)
            )

        connection.commit()
        flash("Screening added successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Screening could not be added: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="infrastructure"))

@admin_bp.route("/admin/screenings/delete/<int:screening_id>", methods=["POST"], strict_slashes=False)
def delete_screening(screening_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT screening_id FROM screening WHERE screening_id = %s",
            (screening_id,)
        )
        screening = cursor.fetchone()

        if not screening:
            flash("Screening not found.", "error")
            return redirect(url_for("admin.dashboard", tab="infrastructure"))

        cursor.execute(
            "DELETE FROM screening WHERE screening_id = %s",
            (screening_id,)
        )
        connection.commit()
        flash("Screening deleted successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Screening could not be deleted: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="infrastructure"))

@admin_bp.route("/admin/saloons/add", methods=["POST"], strict_slashes=False)
def add_saloon():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    theater_id = request.form.get("theater_id", "").strip()
    layout_key = request.form.get("layout", "").strip()

    if not theater_id or layout_key not in SALOON_LAYOUTS:
        flash("Please select a theater and a valid layout template.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    try:
        theater_id = int(theater_id)
    except ValueError:
        flash("Invalid theater selection.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    layout = SALOON_LAYOUTS[layout_key]
    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT theater_id FROM theater WHERE theater_id = %s", (theater_id,))
        if not cursor.fetchone():
            flash("Selected theater does not exist.", "error")
            return redirect(url_for("admin.dashboard", tab="infrastructure"))

        cursor.execute(
            "SELECT COALESCE(MAX(number), 0) + 1 AS next_number FROM saloon WHERE theater_id = %s",
            (theater_id,)
        )
        next_number = cursor.fetchone()["next_number"]

        cursor.execute(
            """
            INSERT INTO saloon (theater_id, number, capacity, type, is_active, `rows`, `cols`)
            VALUES (%s, %s, %s, %s, TRUE, %s, %s)
            """,
            (theater_id, next_number, layout["capacity"], layout["type"], layout["rows"], layout["cols"])
        )

        row_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for r in range(layout["rows"]):
            row_letter = row_letters[r]
            for c in range(1, layout["cols"] + 1):
                cursor.execute(
                    """
                    INSERT INTO seat (theater_id, saloon_number, row_letter, number, type)
                    VALUES (%s, %s, %s, %s, 'Standard')
                    """,
                    (theater_id, next_number, row_letter, c)
                )

        connection.commit()
        flash(
            f"Saloon {next_number} created with {layout['capacity']} seats "
            f"({layout['rows']} rows × {layout['cols']} cols).",
            "success"
        )

    except Exception as error:
        connection.rollback()
        flash(f"Saloon could not be created: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="infrastructure"))

@admin_bp.route("/admin/saloons/delete/<int:theater_id>/<int:saloon_number>", methods=["POST"], strict_slashes=False)
def delete_saloon(theater_id, saloon_number):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="infrastructure"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT theater_id, number FROM saloon WHERE theater_id = %s AND number = %s",
            (theater_id, saloon_number)
        )
        if not cursor.fetchone():
            flash("Saloon not found.", "error")
            return redirect(url_for("admin.dashboard", tab="infrastructure"))

        # A. Future screenings in this saloon
        cursor.execute(
            """
            SELECT screening_id FROM screening
            WHERE theater_id = %s AND saloon_number = %s AND start_time > NOW()
            """,
            (theater_id, saloon_number)
        )
        future_screening_ids = [r["screening_id"] for r in cursor.fetchall()]
        screening_count = len(future_screening_ids)
        refund_count = 0

        if future_screening_ids:
            # B. Bookings that have tickets for those screenings
            ph = ",".join(["%s"] * len(future_screening_ids))
            cursor.execute(
                f"SELECT DISTINCT booking_id FROM ticket WHERE screening_id IN ({ph})",
                tuple(future_screening_ids)
            )
            booking_ids = [r["booking_id"] for r in cursor.fetchall()]
            refund_count = len(booking_ids)

            # C. Mark those payments as Refunded
            if booking_ids:
                ph_b = ",".join(["%s"] * len(booking_ids))
                cursor.execute(
                    f"UPDATE payment SET status = 'Refunded' WHERE booking_id IN ({ph_b})",
                    tuple(booking_ids)
                )

        # D+E. Delete saloon — cascades to SEAT, SCREENING → TICKET automatically
        cursor.execute(
            "DELETE FROM saloon WHERE theater_id = %s AND number = %s",
            (theater_id, saloon_number)
        )

        connection.commit()

        if screening_count > 0:
            flash(
                f"Saloon deleted. {screening_count} future screening(s) cancelled "
                f"and {refund_count} booking(s) marked as refunded.",
                "success"
            )
        else:
            flash("Saloon deleted successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Saloon could not be deleted: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="infrastructure"))

@admin_bp.route("/admin/movies/add", methods=["POST"], strict_slashes=False)
def add_movie():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    title = request.form.get("title", "").strip()
    director = request.form.get("director", "").strip()
    duration_mins = request.form.get("duration_mins", "").strip()
    rating_age = request.form.get("rating_age", "").strip()
    release_date = request.form.get("release_date", "").strip()
    summary = request.form.get("summary", "").strip()

    genre_ids = request.form.getlist("genre_ids")
    format_ids = request.form.getlist("format_ids")
    cast_members = [c.strip() for c in request.form.getlist("cast[]") if c.strip()]
    visibility_status = request.form.get("visibility_status", "catalog_only").strip()
    if visibility_status not in ("now_showing", "coming_soon", "catalog_only"):
        visibility_status = "catalog_only"

    if not title or not director or not duration_mins or not rating_age or not release_date:
        flash("Please fill all required movie fields.", "error")
        return redirect(url_for("admin.dashboard", tab="catalog"))

    try:
        duration_mins = int(duration_mins)
        rating_age = int(rating_age)
    except ValueError:
        flash("Duration and rating age must be valid numbers.", "error")
        return redirect(url_for("admin.dashboard", tab="catalog"))

    poster_url = _save_poster(request.files.get("poster"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="catalog"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            INSERT INTO movie
                (title, director, duration_mins, rating_age, release_date, summary, poster_url, visibility_status)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (title, director, duration_mins, rating_age, release_date, summary, poster_url, visibility_status)
        )

        movie_id = cursor.lastrowid

        for genre_id in genre_ids:
            cursor.execute(
                "INSERT INTO movie_genre (movie_id, genre_id) VALUES (%s, %s)",
                (movie_id, genre_id)
            )

        for format_id in format_ids:
            cursor.execute(
                "INSERT INTO movie_format (movie_id, format_id) VALUES (%s, %s)",
                (movie_id, format_id)
            )

        for cast_name in cast_members:
            cursor.execute(
                "INSERT INTO movie_cast (movie_id, cast_name) VALUES (%s, %s)",
                (movie_id, cast_name)
            )

        connection.commit()
        flash("Movie added successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Movie could not be added: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="catalog"))

@admin_bp.route("/admin/employees/add", methods=["POST"], strict_slashes=False)
def add_employee():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    phone_number = request.form.get("phone_number", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    role = request.form.get("role", "").strip()
    salary = request.form.get("salary", "").strip()
    auth_level = request.form.get("auth_level", "").strip()
    work_shift = request.form.get("work_shift", "").strip()
    theater_id = request.form.get("theater_id", "").strip()

    if not first_name or not last_name or not email or not password or not role or not auth_level:
        flash("Please fill all required employee fields.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    try:
        auth_level = int(auth_level)
    except ValueError:
        flash("Invalid auth level.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    if auth_level not in [1, 2, 3]:
        flash("Auth level must be 1, 2, or 3.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    salary_value = float(salary) if salary else 0.00
    theater_id_value = int(theater_id) if theater_id else None
    password_hash = generate_password_hash(password)

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT user_id FROM user WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            flash("A user with this email already exists.", "error")
            return redirect(url_for("admin.dashboard", tab="staff"))

        cursor.execute(
            """
            INSERT INTO user
                (first_name, last_name, phone_number, email, password_hash, created_at)
            VALUES
                (%s, %s, %s, %s, %s, NOW())
            """,
            (
                first_name,
                last_name,
                phone_number,
                email,
                password_hash
            )
        )

        new_user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO employee
                (user_id, role, salary, account_status, auth_level, work_shift, theater_id)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                new_user_id,
                role,
                salary_value,
                "Active",
                auth_level,
                work_shift,
                theater_id_value
            )
        )

        connection.commit()
        flash("Employee added successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Employee could not be added: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="staff"))

@admin_bp.route("/admin/employees/edit/<int:user_id>", methods=["POST"], strict_slashes=False)
def edit_employee(user_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    phone_number = request.form.get("phone_number", "").strip()
    email = request.form.get("email", "").strip()

    role = request.form.get("role", "").strip()
    salary = request.form.get("salary", "").strip()
    auth_level = request.form.get("auth_level", "").strip()
    account_status = request.form.get("account_status", "").strip()
    work_shift = request.form.get("work_shift", "").strip()
    theater_id = request.form.get("theater_id", "").strip()

    if not first_name or not last_name or not email or not role or not auth_level:
        flash("Please fill all required employee fields.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    try:
        auth_level = int(auth_level)
    except ValueError:
        flash("Invalid auth level.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    if auth_level not in [1, 2, 3]:
        flash("Auth level must be 1, 2, or 3.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    salary_value = float(salary) if salary else 0.00
    theater_id_value = int(theater_id) if theater_id else None

    if account_status not in ["Active", "Inactive"]:
        account_status = "Active"

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT user_id
            FROM user
            WHERE email = %s AND user_id != %s
            """,
            (email, user_id)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            flash("Another user already uses this email.", "error")
            return redirect(url_for("admin.dashboard", tab="staff"))

        cursor.execute(
            """
            UPDATE user
            SET
                first_name = %s,
                last_name = %s,
                phone_number = %s,
                email = %s
            WHERE user_id = %s
            """,
            (
                first_name,
                last_name,
                phone_number,
                email,
                user_id
            )
        )

        cursor.execute(
            """
            UPDATE employee
            SET
                role = %s,
                salary = %s,
                account_status = %s,
                auth_level = %s,
                work_shift = %s,
                theater_id = %s
            WHERE user_id = %s
            """,
            (
                role,
                salary_value,
                account_status,
                auth_level,
                work_shift,
                theater_id_value,
                user_id
            )
        )

        connection.commit()
        flash("Employee updated successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Employee could not be updated: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="staff"))

@admin_bp.route("/admin/employees/deactivate/<int:user_id>", methods=["POST"], strict_slashes=False)
def deactivate_employee(user_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    if session.get("admin_id") == user_id:
        flash("You cannot deactivate your own account.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="staff"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            UPDATE employee
            SET account_status = 'Inactive'
            WHERE user_id = %s
            """,
            (user_id,)
        )

        connection.commit()
        flash("Employee deactivated successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Employee could not be deactivated: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="staff"))

def fetch_employees():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT u.user_id,
               u.first_name,
               u.last_name,
               u.phone_number,
               u.email,
               e.role,
               e.salary,
               e.auth_level,
               e.account_status,
               e.work_shift,
               e.theater_id
        FROM employee e
                 JOIN user u
        ON e.user_id = u.user_id
        ORDER BY u.user_id DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    employees = []
    colors = ["crimson", "amber", "emerald", "sky"]

    for index, row in enumerate(rows):
        name = f"{row['first_name']} {row['last_name']}"
        initials = f"{row['first_name'][0]}{row['last_name'][0]}".upper()

        auth_level = int(row["auth_level"])

        if auth_level == 3:
            auth_label = "Admin"
            auth_color = "crimson"
        elif auth_level == 2:
            auth_label = "Moderator"
            auth_color = "amber"
        else:
            auth_label = "Staff"
            auth_color = "slate-600"

        employees.append({
            "id": row["user_id"],
            "initials": initials,
            "color": colors[index % len(colors)],
            "name": name,

            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "phone_number": row["phone_number"],
            "email": row["email"],

            "role": row["role"],
            "auth_level": auth_label,
            "auth_level_value": auth_level,
            "auth_color": auth_color,

            "salary": f"${float(row['salary']):,.2f}" if row["salary"] is not None else "$0.00",
            "salary_value": float(row["salary"]) if row["salary"] is not None else 0,

            "account_status": row["account_status"],
            "work_shift": row["work_shift"],
            "theater_id": row["theater_id"] if row["theater_id"] is not None else ""
        })

    return employees

def fetch_movies_for_admin():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            m.movie_id,
            m.title,
            m.director,
            m.duration_mins,
            m.rating_age,
            m.release_date,
            m.summary,
            m.poster_url,
            m.visibility_status,
            GROUP_CONCAT(DISTINCT g.name SEPARATOR ', ') AS genre_names,
            GROUP_CONCAT(DISTINCT g.genre_id SEPARATOR ',') AS genre_ids,
            GROUP_CONCAT(DISTINCT f.format_id SEPARATOR ',') AS format_ids,
            GROUP_CONCAT(DISTINCT mc.cast_name SEPARATOR ',') AS cast_names
        FROM movie m
        LEFT JOIN movie_genre mg ON m.movie_id = mg.movie_id
        LEFT JOIN genre g ON mg.genre_id = g.genre_id
        LEFT JOIN movie_format mf ON m.movie_id = mf.movie_id
        LEFT JOIN format f ON mf.format_id = f.format_id
        LEFT JOIN movie_cast mc ON m.movie_id = mc.movie_id
        GROUP BY
            m.movie_id,
            m.title,
            m.director,
            m.duration_mins,
            m.rating_age,
            m.release_date,
            m.summary,
            m.poster_url,
            m.visibility_status
        ORDER BY m.movie_id DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    movies = []
    genre_colors = ["crimson", "amber", "emerald", "sky"]

    for row in rows:
        raw_genres = row["genre_names"].split(", ") if row["genre_names"] else []

        genres = []
        for index, genre_name in enumerate(raw_genres):
            genres.append((genre_name, genre_colors[index % len(genre_colors)]))

        release_date = row["release_date"]
        release_date_value = release_date.strftime("%Y-%m-%d") if hasattr(release_date, "strftime") else str(release_date or "")

        movies.append({
            "id": row["movie_id"],
            "name": row["title"],
            "title": row["title"],
            "director": row["director"] or "",
            "duration_mins": row["duration_mins"],
            "duration": f"{row['duration_mins']} min",
            "rating_age": row["rating_age"],
            "release_date": release_date_value,
            "summary": row["summary"] or "",
            "poster_url": row["poster_url"] or "",
            "genres": genres,
            "genre_ids": row["genre_ids"] or "",
            "format_ids": row["format_ids"] or "",
            "cast": row["cast_names"] or "",
            "visibility_status": row["visibility_status"] or "catalog_only"
        })

    return movies

@admin_bp.route("/admin/movies/edit/<int:movie_id>", methods=["POST"], strict_slashes=False)
def edit_movie(movie_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    title = request.form.get("title", "").strip()
    director = request.form.get("director", "").strip()
    duration_mins = request.form.get("duration_mins", "").strip()
    rating_age = request.form.get("rating_age", "").strip()
    release_date = request.form.get("release_date", "").strip()
    summary = request.form.get("summary", "").strip()

    genre_ids = request.form.getlist("genre_ids")
    format_ids = request.form.getlist("format_ids")
    cast_members = [c.strip() for c in request.form.getlist("cast[]") if c.strip()]
    visibility_status = request.form.get("visibility_status", "catalog_only").strip()
    if visibility_status not in ("now_showing", "coming_soon", "catalog_only"):
        visibility_status = "catalog_only"

    if not title or not director or not duration_mins or not rating_age or not release_date:
        flash("Please fill all required movie fields.", "error")
        return redirect(url_for("admin.dashboard", tab="catalog"))

    try:
        duration_mins = int(duration_mins)
        rating_age = int(rating_age)
    except ValueError:
        flash("Duration and rating age must be valid numbers.", "error")
        return redirect(url_for("admin.dashboard", tab="catalog"))

    new_poster_url = _save_poster(request.files.get("poster"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="catalog"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT movie_id, poster_url FROM movie WHERE movie_id = %s",
            (movie_id,)
        )

        existing_movie = cursor.fetchone()

        if not existing_movie:
            flash("Movie not found.", "error")
            return redirect(url_for("admin.dashboard", tab="catalog"))

        poster_url = new_poster_url if new_poster_url else existing_movie["poster_url"]

        cursor.execute(
            """
            UPDATE movie
            SET title = %s, director = %s, duration_mins = %s,
                rating_age = %s, release_date = %s, summary = %s,
                poster_url = %s, visibility_status = %s
            WHERE movie_id = %s
            """,
            (title, director, duration_mins, rating_age, release_date, summary, poster_url, visibility_status, movie_id)
        )

        cursor.execute("DELETE FROM movie_genre WHERE movie_id = %s", (movie_id,))
        for genre_id in genre_ids:
            cursor.execute(
                "INSERT INTO movie_genre (movie_id, genre_id) VALUES (%s, %s)",
                (movie_id, genre_id)
            )

        cursor.execute("DELETE FROM movie_format WHERE movie_id = %s", (movie_id,))
        for format_id in format_ids:
            cursor.execute(
                "INSERT INTO movie_format (movie_id, format_id) VALUES (%s, %s)",
                (movie_id, format_id)
            )

        cursor.execute("DELETE FROM movie_cast WHERE movie_id = %s", (movie_id,))
        for cast_name in cast_members:
            cursor.execute(
                "INSERT INTO movie_cast (movie_id, cast_name) VALUES (%s, %s)",
                (movie_id, cast_name)
            )

        connection.commit()
        flash("Movie updated successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Movie could not be updated: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="catalog"))

@admin_bp.route("/admin/movies/delete/<int:movie_id>", methods=["POST"], strict_slashes=False)
def delete_movie(movie_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="catalog"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT movie_id FROM movie WHERE movie_id = %s", (movie_id,))
        movie = cursor.fetchone()

        if not movie:
            flash("Movie not found.", "error")
            return redirect(url_for("admin.dashboard", tab="catalog"))

        cursor.execute("DELETE FROM movie WHERE movie_id = %s", (movie_id,))
        connection.commit()
        flash("Movie deleted successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Movie could not be deleted: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="catalog"))

@admin_bp.route("/admin/consumables/add", methods=["POST"], strict_slashes=False)
def add_consumable():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    name = request.form.get("name", "").strip()
    unit_price = request.form.get("unit_price", "").strip()
    stock_quantity = request.form.get("stock_quantity", "").strip()

    if not name or not unit_price or not stock_quantity:
        flash("Please fill all required consumable fields.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    try:
        unit_price = float(unit_price)
        stock_quantity = int(stock_quantity)
    except ValueError:
        flash("Price and stock quantity must be valid numbers.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT consumable_id
            FROM consumable
            WHERE LOWER(name) = LOWER(%s)
            """,
            (name,)
        )

        existing_item = cursor.fetchone()

        if existing_item:
            flash("This consumable already exists.", "error")
            return redirect(url_for("admin.dashboard", tab="business"))

        cursor.execute(
            """
            INSERT INTO consumable
                (name, unit_price, stock_quantity)
            VALUES
                (%s, %s, %s)
            """,
            (name, unit_price, stock_quantity)
        )

        connection.commit()
        flash("Consumable added successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Consumable could not be added: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="business"))

def fetch_theaters():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT theater_id, name
        FROM theater
        ORDER BY name
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [{"id": row["theater_id"], "name": row["name"]} for row in rows]


def fetch_genres():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT genre_id, name
        FROM genre
        ORDER BY name
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows

def fetch_formats():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT format_id, name
        FROM format
        ORDER BY name
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def fetch_saloons():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            s.theater_id,
            t.name AS theater_name,
            s.number,
            s.capacity,
            s.type,
            s.is_active,
            s.rows,
            s.cols
        FROM saloon s
        JOIN theater t ON s.theater_id = t.theater_id
        ORDER BY s.theater_id, s.number
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    saloons = []

    for row in rows:
        is_active = bool(row["is_active"])
        rows_count = int(row["rows"] or 0)
        cols_count = int(row["cols"] or 0)
        layout_info = f" · {rows_count}r×{cols_count}c" if rows_count and cols_count else ""

        saloons.append({
            "theater_id": row["theater_id"],
            "number": row["number"],
            "name": f"{row['theater_name']} - Saloon {row['number']}",
            "info": f"{row['capacity']} seats • {row['type']}{layout_info}",
            "status": "Active" if is_active else "Maintenance",
            "status_color": "emerald" if is_active else "amber"
        })

    return saloons


def fetch_upcoming_screenings():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            s.screening_id,
            m.title AS movie_title,
            t.name AS theater_name,
            s.saloon_number,
            s.start_time,
            s.base_price
        FROM screening s
        JOIN movie m ON s.movie_id = m.movie_id
        JOIN theater t ON s.theater_id = t.theater_id
        WHERE s.start_time >= NOW()
        ORDER BY s.start_time ASC
        LIMIT 10
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    screenings = []

    for row in rows:
        screenings.append({
            "id": row["screening_id"],
            "movie": row["movie_title"],
            "status": "Scheduled",
            "status_color": "sky",
            "saloon": f"{row['theater_name']} - Saloon {row['saloon_number']}",
            "time": row["start_time"].strftime("%Y-%m-%d %H:%M") if hasattr(row["start_time"], "strftime") else str(row["start_time"]),
            "price": f"${float(row['base_price']):.2f}"
        })

    return screenings

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

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    consumables = []

    for row in rows:
        stock = int(row["stock_quantity"])

        if stock <= 20:
            stock_class = "text-amber"
            wrapper_class = "border border-amber/30"
            stock_label = f"Stock: {stock} units ⚠️"
        else:
            stock_class = "text-slate-400"
            wrapper_class = ""
            stock_label = f"Stock: {stock} units"

        consumables.append({
            "id": row["consumable_id"],
            "name": row["name"],
            "unit_price": float(row["unit_price"]),
            "stock_quantity": stock,
            "price": f"${float(row['unit_price']):.2f}",
            "stock": stock_label,
            "stock_class": stock_class,
            "wrapper_class": wrapper_class
        })
    return consumables


def fetch_deals():
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
        ORDER BY valid_until DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    from datetime import date

    deals = []

    for row in rows:
        valid_until = row["valid_until"]
        is_active = valid_until >= date.today()

        valid_text = valid_until.strftime("%Y-%m-%d") if hasattr(valid_until, "strftime") else str(valid_until)

        deals.append({
            "id": row["deal_id"],
            "name": row["name"],
            "discount_percent": float(row["discount_percent"]),
            "valid_until": valid_text,
            "status": "Active" if is_active else "Inactive",
            "status_color": "emerald" if is_active else "slate-600",
            "desc": f"{float(row['discount_percent']):.0f}% discount",
            "valid": f"Valid until {valid_text}"
        })

    return deals

@admin_bp.route("/admin/deals/edit/<int:deal_id>", methods=["POST"], strict_slashes=False)
def edit_deal(deal_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    name = request.form.get("name", "").strip()
    discount_percent = request.form.get("discount_percent", "").strip()
    valid_until = request.form.get("valid_until", "").strip()

    if not name or not discount_percent or not valid_until:
        flash("Please fill all required deal fields.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    try:
        discount_percent = float(discount_percent)
    except ValueError:
        flash("Discount percent must be a valid number.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    if discount_percent < 0 or discount_percent > 100:
        flash("Discount percent must be between 0 and 100.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT deal_id
            FROM deal
            WHERE deal_id = %s
            """,
            (deal_id,)
        )

        existing_deal = cursor.fetchone()

        if not existing_deal:
            flash("Deal not found.", "error")
            return redirect(url_for("admin.dashboard", tab="business"))

        cursor.execute(
            """
            SELECT deal_id
            FROM deal
            WHERE LOWER(name) = LOWER(%s)
              AND deal_id != %s
            """,
            (name, deal_id)
        )

        duplicate_deal = cursor.fetchone()

        if duplicate_deal:
            flash("Another deal already uses this name.", "error")
            return redirect(url_for("admin.dashboard", tab="business"))

        cursor.execute(
            """
            UPDATE deal
            SET
                name = %s,
                discount_percent = %s,
                valid_until = %s
            WHERE deal_id = %s
            """,
            (
                name,
                discount_percent,
                valid_until,
                deal_id
            )
        )

        connection.commit()
        flash("Deal updated successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Deal could not be updated: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="business"))

def _period_sql(col, period):
    """Return a SQL AND-fragment for the given period, or '' for all-time.

    Safe to interpolate: period is validated against _VALID_PERIODS before this is called.
    """
    if period == "today":
        return f"AND DATE({col}) = CURDATE()"
    if period == "this_week":
        return f"AND {col} >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    if period == "this_month":
        return f"AND YEAR({col}) = YEAR(CURDATE()) AND MONTH({col}) = MONTH(CURDATE())"
    if period == "this_year":
        return f"AND YEAR({col}) = YEAR(CURDATE())"
    return ""

_PERIOD_LABELS = {
    "today":      "Today",
    "this_week":  "This week",
    "this_month": "This month",
    "this_year":  "This year",
    "all_time":   "All time",
}

def fetch_analytics_summary(revenue_period="this_month", occupancy_period="this_week", tickets_period="this_month"):
    connection = get_db_connection()

    if connection is None:
        return {
            "total_revenue": "$0.00",
            "tickets_sold": 0,
            "inventory_alerts": 0,
            "occupancy_rate": "0.0%",
            "revenue_label": "No data",
            "occupancy_label": "No data",
            "tickets_label": "No data",
        }

    cursor = connection.cursor(dictionary=True)

    try:
        rev_clause = _period_sql("b.created_at", revenue_period)
        cursor.execute(
            f"""
            SELECT COALESCE(SUM(b.total_amount), 0) AS total_revenue
            FROM booking b
            INNER JOIN payment p ON b.booking_id = p.booking_id
            WHERE p.status IN ('Paid', 'Completed')
            {rev_clause}
            """
        )
        revenue_row = cursor.fetchone()
        total_revenue = float(revenue_row["total_revenue"] or 0)

        # Tickets Sold — only count tickets from paid/completed bookings
        tkt_clause = _period_sql("b.created_at", tickets_period)
        cursor.execute(
            f"""
            SELECT COUNT(t.ticket_id) AS tickets_sold
            FROM ticket t
            JOIN booking b ON t.booking_id = b.booking_id
            INNER JOIN payment p ON b.booking_id = p.booking_id
            WHERE p.status IN ('Paid', 'Completed')
            {tkt_clause}
            """
        )
        tickets_row = cursor.fetchone()
        tickets_sold = int(tickets_row["tickets_sold"] or 0)

        # Inventory Alerts: stock <= 20 — no time filter (always all-time)
        cursor.execute(
            """
            SELECT COUNT(*) AS inventory_alerts
            FROM consumable
            WHERE stock_quantity <= 20
            """
        )
        inventory_row = cursor.fetchone()
        inventory_alerts = int(inventory_row["inventory_alerts"] or 0)

        # Occupancy Rate: filter both subqueries by screening start_time.
        # Two independent subqueries prevent the fan-trap where joining
        # tickets to screenings would multiply sal.capacity by the ticket count.
        occ_clause = _period_sql("sc.start_time", occupancy_period)
        cursor.execute(
            f"""
            SELECT
                (
                    SELECT COUNT(t.ticket_id)
                    FROM ticket t
                    JOIN screening sc ON t.screening_id = sc.screening_id
                    WHERE 1=1 {occ_clause}
                ) AS sold_seats,
                (
                    SELECT COALESCE(SUM(sal.capacity), 0)
                    FROM screening sc
                    JOIN saloon sal
                      ON sc.theater_id    = sal.theater_id
                     AND sc.saloon_number = sal.number
                    WHERE 1=1 {occ_clause}
                ) AS possible_capacity
            """
        )
        occupancy_row = cursor.fetchone()

        sold_seats = int(occupancy_row["sold_seats"] or 0)
        possible_capacity = int(occupancy_row["possible_capacity"] or 0)

        occupancy_rate = 0
        if possible_capacity > 0:
            occupancy_rate = (sold_seats / possible_capacity) * 100

        rev_label  = _PERIOD_LABELS.get(revenue_period, "All time") + " — paid bookings"
        occ_label  = _PERIOD_LABELS.get(occupancy_period, "All time") + " — tickets vs capacity"
        tkt_label  = _PERIOD_LABELS.get(tickets_period, "All time") + " — tickets issued"

        return {
            "total_revenue":    f"${total_revenue:,.2f}",
            "tickets_sold":     tickets_sold,
            "inventory_alerts": inventory_alerts,
            "occupancy_rate":   f"{occupancy_rate:.1f}%",
            "revenue_label":    rev_label,
            "occupancy_label":  occ_label,
            "tickets_label":    tkt_label,
        }

    finally:
        cursor.close()
        connection.close()

def fetch_revenue_by_theater():
    connection = get_db_connection()

    if connection is None:
        return {
            "labels": [],
            "values": []
        }

    cursor = connection.cursor(dictionary=True)

    try:
        # Subquery deduplicates on (theater_id, booking_id) so a booking with
        # N tickets is counted once, not N times.
        cursor.execute(
            """
            SELECT
                th.name AS theater_name,
                COALESCE(SUM(paid.total_amount), 0) AS revenue
            FROM theater th
            LEFT JOIN (
                SELECT DISTINCT sc.theater_id, b.booking_id, b.total_amount
                FROM ticket tk
                JOIN screening sc ON tk.screening_id = sc.screening_id
                JOIN booking   b  ON tk.booking_id   = b.booking_id
                JOIN payment   p  ON b.booking_id    = p.booking_id
                WHERE p.status IN ('Paid', 'Completed')
            ) paid ON th.theater_id = paid.theater_id
            GROUP BY th.theater_id, th.name
            ORDER BY revenue DESC
            """
        )

        rows = cursor.fetchall()

        labels = []
        values = []

        for row in rows:
            labels.append(row["theater_name"])
            values.append(float(row["revenue"] or 0))

        return {
            "labels": labels,
            "values": values
        }

    finally:
        cursor.close()
        connection.close()


@admin_bp.route("/admin/consumables/edit/<int:consumable_id>", methods=["POST"], strict_slashes=False)
def edit_consumable(consumable_id):
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    name = request.form.get("name", "").strip()
    unit_price = request.form.get("unit_price", "").strip()
    stock_quantity = request.form.get("stock_quantity", "").strip()

    if not name or not unit_price or not stock_quantity:
        flash("Please fill all required consumable fields.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    try:
        unit_price = float(unit_price)
        stock_quantity = int(stock_quantity)
    except ValueError:
        flash("Price and stock quantity must be valid numbers.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT consumable_id
            FROM consumable
            WHERE consumable_id = %s
            """,
            (consumable_id,)
        )

        existing_item = cursor.fetchone()

        if not existing_item:
            flash("Consumable not found.", "error")
            return redirect(url_for("admin.dashboard", tab="business"))

        cursor.execute(
            """
            SELECT consumable_id
            FROM consumable
            WHERE LOWER(name) = LOWER(%s)
              AND consumable_id != %s
            """,
            (name, consumable_id)
        )

        duplicate_item = cursor.fetchone()

        if duplicate_item:
            flash("Another consumable already uses this name.", "error")
            return redirect(url_for("admin.dashboard", tab="business"))

        cursor.execute(
            """
            UPDATE consumable
            SET
                name = %s,
                unit_price = %s,
                stock_quantity = %s
            WHERE consumable_id = %s
            """,
            (
                name,
                unit_price,
                stock_quantity,
                consumable_id
            )
        )

        connection.commit()
        flash("Consumable updated successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Consumable could not be updated: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="business"))

def get_vip_tier_info():
    return {
        "name": "VIP Member",
        "color": "amber",
        "border": "border-amber",
        "spend": "$500 Annual Spend",
        "discount": "15% off tickets & snacks",
        "discount_color": "emerald",
        "points": "2x Points on all purchases"
    }

@admin_bp.route("/admin/deals/add", methods=["POST"], strict_slashes=False)
def add_deal():
    if "admin_id" not in session:
        return redirect(url_for("admin.login"))

    name = request.form.get("name", "").strip()
    discount_percent = request.form.get("discount_percent", "").strip()
    valid_until = request.form.get("valid_until", "").strip()

    if not name or not discount_percent or not valid_until:
        flash("Please fill all required deal fields.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    try:
        discount_percent = float(discount_percent)
    except ValueError:
        flash("Discount percent must be a valid number.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    if discount_percent < 0 or discount_percent > 100:
        flash("Discount percent must be between 0 and 100.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("admin.dashboard", tab="business"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT deal_id
            FROM deal
            WHERE LOWER(name) = LOWER(%s)
            """,
            (name,)
        )

        existing_deal = cursor.fetchone()

        if existing_deal:
            flash("This deal already exists.", "error")
            return redirect(url_for("admin.dashboard", tab="business"))

        cursor.execute(
            """
            INSERT INTO deal
                (name, discount_percent, valid_until)
            VALUES
                (%s, %s, %s)
            """,
            (
                name,
                discount_percent,
                valid_until
            )
        )

        connection.commit()
        flash("Deal added successfully.", "success")

    except Exception as error:
        connection.rollback()
        flash(f"Deal could not be added: {error}", "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("admin.dashboard", tab="business"))

def fetch_vip_spenders():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            u.first_name,
            u.last_name,
            u.email,
            c.membership_tier,
            SUM(b.total_amount) AS total_spent,
            COUNT(DISTINCT b.booking_id) AS visits
        FROM customer c
        JOIN user u ON c.user_id = u.user_id
        JOIN booking b ON c.user_id = b.user_id
        JOIN payment p ON b.booking_id = p.booking_id
        LEFT JOIN employee e ON c.user_id = e.user_id
        WHERE p.status IN ('Paid', 'Completed')
          AND e.user_id IS NULL
        GROUP BY u.user_id, u.first_name, u.last_name, u.email, c.membership_tier
        ORDER BY total_spent DESC
        LIMIT 10
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    spenders = []
    colors = ["amber", "slate-400", "sky", "crimson"]

    for index, row in enumerate(rows):
        name = f"{row['first_name']} {row['last_name']}"
        initials = f"{row['first_name'][0]}{row['last_name'][0]}".upper()

        total_spent = float(row["total_spent"])
        visits = int(row["visits"])
        avg = total_spent / visits if visits > 0 else 0

        tier = row["membership_tier"] or "Standard"

        spenders.append({
            "initials": initials,
            "color": colors[index % len(colors)],
            "name": name,
            "email": row["email"],
            "tier": tier,
            "tier_color": "amber" if tier.lower() == "vip" else "slate-400",
            "spent": f"${total_spent:,.2f}",
            "visits": visits,
            "avg": f"${avg:,.2f}"
        })

    return spenders
