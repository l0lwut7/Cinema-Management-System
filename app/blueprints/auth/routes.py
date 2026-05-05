from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import get_db_connection


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone_number = request.form.get("phone_number")
    email = request.form.get("email")
    password = request.form.get("password")
    birth_date = request.form.get("birth_date")

    if not first_name or not last_name or not email or not password:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("auth.register"))

    password_hash = generate_password_hash(password)

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("auth.register"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT user_id
            FROM user
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            flash("This email is already registered.", "error")
            return redirect(url_for("auth.register"))

        cursor.execute(
            """
            INSERT INTO user
            (first_name, last_name, phone_number, email, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (first_name, last_name, phone_number, email, password_hash)
        )

        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO customer
            (user_id, birth_date, loyalty_points, membership_tier)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, birth_date, 0, "Standard")
        )

        connection.commit()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    except Exception as e:
        connection.rollback()
        flash(str(e), "error")
        return redirect(url_for("auth.register"))

    finally:
        cursor.close()
        connection.close()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required.", "error")
        return redirect(url_for("auth.login"))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("auth.login"))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                user_id,
                first_name,
                last_name,
                email,
                password_hash
            FROM user
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user is None:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))

        session["user_id"] = user["user_id"]
        session["user_name"] = user["first_name"]

        next_url = request.args.get("next")

        flash("Login successful.", "success")

        if next_url:
            return redirect(next_url)

        return redirect(url_for("discovery.home"))

    finally:
        cursor.close()
        connection.close()


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("discovery.home"))