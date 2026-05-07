from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for, session, flash
from .data import COMING_SOON, MOVIES, NAV_ITEMS, REVIEWS
from app.db import get_db_connection


discovery_bp = Blueprint("discovery", __name__)

def fetch_deals():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            deal_id AS id,
            name AS title,
            discount_percent,
            valid_until
        FROM deal
        WHERE valid_until IS NULL
           OR valid_until >= CURDATE()
        ORDER BY
            valid_until ASC,
            discount_percent DESC
        """
    )

    deals = cursor.fetchall()

    cursor.close()
    connection.close()

    for deal in deals:
        deal["discount_percent"] = float(deal["discount_percent"] or 0)

        if deal["valid_until"]:
            deal["valid_until_display"] = deal["valid_until"].strftime("%b %d, %Y")
        else:
            deal["valid_until_display"] = "No expiry"

        deal["tag"] = str(int(deal["discount_percent"])) + "% OFF"

        if deal["discount_percent"] > 0:
            deal["description"] = (
                "Save " + str(int(deal["discount_percent"])) +
                "% on eligible bookings. Valid until " +
                deal["valid_until_display"] + "."
            )
        else:
            deal["description"] = "Special cinema promotion. Valid until " + deal["valid_until_display"] + "."

    return deals

def fetch_theaters():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            t.theater_id AS id,
            t.name,
            t.address,
            COUNT(sa.number) AS screens
        FROM theater t
        LEFT JOIN saloon sa
            ON t.theater_id = sa.theater_id
        GROUP BY
            t.theater_id,
            t.name,
            t.address
        ORDER BY t.name ASC
        """
    )

    theaters = cursor.fetchall()

    cursor.close()
    connection.close()

    for theater in theaters:
        theater["status"] = "Open"
        theater["distance"] = "—"
        theater["phone"] = ""
        theater["manager_name"] = ""
        theater["image_url"] = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=900&q=80"

    return theaters


def fetch_theater_by_id(theater_id):
    connection = get_db_connection()

    if connection is None:
        abort(500)

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            t.theater_id AS id,
            t.name,
            t.address,
            COUNT(sa.number) AS screens
        FROM theater t
        LEFT JOIN saloon sa
            ON t.theater_id = sa.theater_id
        WHERE t.theater_id = %s
        GROUP BY
            t.theater_id,
            t.name,
            t.address
        """,
        (theater_id,)
    )

    theater = cursor.fetchone()

    cursor.close()
    connection.close()

    if theater is None:
        abort(404)

    theater["status"] = "Open"
    theater["distance"] = "—"
    theater["phone"] = ""
    theater["manager_name"] = ""
    theater["image_url"] = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=900&q=80"

    return theater


def fetch_saloons_for_theater(theater_id):
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            number,
            type,
            capacity
        FROM saloon
        WHERE theater_id = %s
        ORDER BY number ASC
        """,
        (theater_id,)
    )

    saloons = cursor.fetchall()

    cursor.close()
    connection.close()

    screens = []

    for saloon in saloons:
        saloon_type = saloon.get("type") or "Standard"

        screens.append({
            "name": "Saloon " + str(saloon["number"]),
            "type": saloon_type,
            "capacity": saloon["capacity"],
            "features": get_saloon_features(saloon_type),
            "status": "Available"
        })

    return screens


def get_saloon_features(saloon_type):
    if not saloon_type:
        return "Digital Projection, Surround Sound"

    saloon_type_lower = saloon_type.lower()

    if "imax" in saloon_type_lower:
        return "IMAX Screen, Premium Sound"
    if "premium" in saloon_type_lower:
        return "Premium Seats, Enhanced Audio"
    if "4dx" in saloon_type_lower:
        return "Motion Seats, Environmental Effects"
    if "kids" in saloon_type_lower:
        return "Family Friendly, Low Volume"

    return "Digital Projection, Surround Sound"

def fetch_now_showing_movies():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            m.movie_id AS id,
            m.title,
            m.director,
            m.duration_mins AS duration,
            m.rating_age,
            m.release_date,
            m.summary AS synopsis,
            m.poster_url,
            COALESCE(ROUND(AVG(r.rating), 1), 0) AS avg_rating
        FROM movie m
        LEFT JOIN review r ON r.movie_id = m.movie_id
        WHERE m.visibility_status = 'now_showing'
        GROUP BY m.movie_id, m.title, m.director, m.duration_mins, m.rating_age, m.release_date, m.summary, m.poster_url
        ORDER BY m.release_date DESC
    """

    cursor.execute(query)
    movies = cursor.fetchall()

    cursor.close()
    connection.close()

    _fallback = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80"
    for movie in movies:
        movie["avg_rating"] = float(movie["avg_rating"] or 0)
        movie["rating"] = movie["avg_rating"]
        movie["status"] = "Now Showing"
        movie["genres"] = ""
        movie["format"] = ""
        movie["runtime_label"] = str(movie["duration"]) + " min"
        movie["meta"] = movie["director"]
        movie["badge"] = "Now Showing"
        movie["image_url"] = movie.get("poster_url") or _fallback
        movie["is_favorited"] = False
        movie["detail_url"] = url_for("discovery.movie_detail", movie_id=movie["id"])

    return movies


def fetch_coming_soon_movies():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            m.movie_id AS id,
            m.title,
            m.director,
            m.duration_mins AS duration,
            m.rating_age,
            m.release_date,
            m.summary AS synopsis,
            m.poster_url,
            COALESCE(ROUND(AVG(r.rating), 1), 0) AS avg_rating
        FROM movie m
        LEFT JOIN review r ON r.movie_id = m.movie_id
        WHERE m.visibility_status = 'coming_soon'
        GROUP BY m.movie_id, m.title, m.director, m.duration_mins, m.rating_age, m.release_date, m.summary, m.poster_url
        ORDER BY m.release_date ASC
    """

    cursor.execute(query)
    movies = cursor.fetchall()

    cursor.close()
    connection.close()

    _fallback = "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?w=1200&q=80"
    for movie in movies:
        movie["avg_rating"] = float(movie["avg_rating"] or 0)
        movie["rating"] = movie["avg_rating"]
        movie["status"] = "Coming Soon"
        movie["genres"] = ""
        movie["format"] = ""
        movie["runtime_label"] = "TBA" if movie["duration"] is None else str(movie["duration"]) + " min"
        movie["meta"] = movie["director"]
        movie["badge"] = "Coming Soon"
        movie["image_url"] = movie.get("poster_url") or _fallback
        movie["is_favorited"] = False
        movie["detail_url"] = url_for("discovery.movie_detail", movie_id=movie["id"])

    return movies


def fetch_movie_by_id(movie_id):
    connection = get_db_connection()

    if connection is None:
        abort(500)

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            m.movie_id AS id,
            m.title,
            m.director,
            m.duration_mins AS duration,
            m.rating_age,
            m.release_date,
            m.summary AS synopsis,
            m.poster_url,
            m.visibility_status,
            GROUP_CONCAT(DISTINCT g.name SEPARATOR ', ') AS genres,
            GROUP_CONCAT(DISTINCT f.name SEPARATOR ', ') AS format
        FROM movie m
        LEFT JOIN movie_genre mg ON m.movie_id = mg.movie_id
        LEFT JOIN genre g ON mg.genre_id = g.genre_id
        LEFT JOIN movie_format mf ON m.movie_id = mf.movie_id
        LEFT JOIN format f ON mf.format_id = f.format_id
        WHERE m.movie_id = %s
        GROUP BY m.movie_id
    """

    cursor.execute(query, (movie_id,))
    movie = cursor.fetchone()

    cursor.close()
    connection.close()

    if movie is None:
        abort(404)

    vs = movie.get("visibility_status", "catalog_only")
    if vs == "now_showing":
        movie["status"] = "Now Showing"
    elif vs == "coming_soon":
        movie["status"] = "Coming Soon"
    else:
        movie["status"] = "Catalog Only"

    movie["rating"] = 0
    movie["avg_rating"] = 0
    movie["runtime_label"] = str(movie["duration"]) + " min"
    movie["meta"] = movie["director"]
    movie["badge"] = movie["status"]
    movie["image_url"] = movie.get("poster_url") or "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80"
    movie["is_favorited"] = False
    movie["detail_url"] = url_for("discovery.movie_detail", movie_id=movie["id"])

    return movie


def build_movie(movie):
    item = movie.copy()
    item["detail_url"] = url_for("discovery.movie_detail", movie_id=item["id"])
    return item


def build_movies(items):
    movies = []
    for item in items:
        movies.append(build_movie(item))
    return movies


def get_movie(movie_id):
  return fetch_movie_by_id(movie_id)


def is_movie_favorited(user_id, movie_id):
    connection = get_db_connection()
    if connection is None:
        return False

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT 1 FROM CUSTOMER_FAVORITE_MOVIE WHERE user_id = %s AND movie_id = %s LIMIT 1",
        (user_id, movie_id)
    )
    exists = cursor.fetchone() is not None
    cursor.close()
    connection.close()
    return exists


def get_theater(theater_id):
    return fetch_theater_by_id(theater_id)

def get_now_showing_movies():
    return fetch_now_showing_movies()


def get_coming_soon_movies():
    return fetch_coming_soon_movies()


def get_request_int(name, default_value):
    value = request.args.get(name, type=int)
    if value is None:
        return default_value
    return value


def get_base_context(active_page, title):
    context = {}
    context["active_page"] = active_page
    context["page_title"] = title
    context["nav_items"] = NAV_ITEMS
    context["is_authenticated"] = 'user_id' in session
    context["user_name"] = "Guest"
    context["login_url"] = url_for("auth.login")
    context["profile_url"] = url_for("discovery.profile")
    context["search_url"] = url_for("discovery.now_showing")
    context["deals_url"] = url_for("discovery.deals")
    return context


@discovery_bp.route("/")
def home():
    now_showing = get_now_showing_movies()
    coming_soon = get_coming_soon_movies()

    # Use first now-showing movie as hero; fall back to first coming-soon movie.
    # If both lists are empty the template gets None and renders without a hero.
    all_movies = now_showing + coming_soon
    featured_movie = all_movies[0] if all_movies else None

    context = get_base_context("home", "CineMax - Home")
    context["featured_movie"] = featured_movie
    context["now_showing"] = now_showing
    context["coming_soon"] = coming_soon
    return render_template("discovery/home.html", **context)


@discovery_bp.route("/now-showing")
def now_showing():
    context = get_base_context("now_showing", "CineMax - Now Showing")
    context["movies"] = get_now_showing_movies()
    return render_template("discovery/now_showing.html", **context)


@discovery_bp.route("/movies")
def movies():
    return redirect(url_for("discovery.now_showing"))


@discovery_bp.route("/coming-soon")
def coming_soon():
    context = get_base_context("coming_soon", "CineMax - Coming Soon")
    context["coming_soon"] = get_coming_soon_movies()
    return render_template("discovery/coming_soon.html", **context)


@discovery_bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = get_movie(movie_id)
    cast = fetch_movie_cast(movie_id)
    reviews = fetch_movie_reviews(movie_id)
    rating_summary = fetch_movie_rating_summary(movie_id)

    movie["avg_rating"] = rating_summary["avg_rating"]

    if session.get("user_id"):
        movie["is_favorited"] = is_movie_favorited(session["user_id"], movie_id)
    else:
        movie["is_favorited"] = False

    context = get_base_context("movies", movie["title"] + " - CineMax")
    context["movie"] = movie
    context["cast"] = cast
    context["reviews"] = reviews
    context["total_reviews"] = rating_summary["total_reviews"]
    context["rating_distribution"] = rating_summary["distribution"]

    return render_template("discovery/movie_detail.html", **context)


@discovery_bp.route("/api/favorites/toggle/<int:movie_id>", methods=["POST"])
def toggle_favorite(movie_id):
    if "user_id" not in session:
        return jsonify(error="Authentication required"), 401

    user_id = session["user_id"]
    connection = get_db_connection()
    if connection is None:
        return jsonify(error="Database connection failed"), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT 1 FROM CUSTOMER_FAVORITE_MOVIE WHERE user_id = %s AND movie_id = %s LIMIT 1",
            (user_id, movie_id)
        )
        favorite_exists = cursor.fetchone() is not None

        if favorite_exists:
            cursor.execute(
                "DELETE FROM CUSTOMER_FAVORITE_MOVIE WHERE user_id = %s AND movie_id = %s",
                (user_id, movie_id)
            )
            is_favorited = False
        else:
            cursor.execute(
                "INSERT INTO CUSTOMER_FAVORITE_MOVIE (user_id, movie_id) VALUES (%s, %s)",
                (user_id, movie_id)
            )
            is_favorited = True

        connection.commit()
        return jsonify(is_favorited=is_favorited)
    except Exception:
        connection.rollback()
        return jsonify(error="Failed to update favorite"), 500
    finally:
        cursor.close()
        connection.close()


@discovery_bp.route("/theaters")
def theaters():
    theaters_list = fetch_theaters()

    if not theaters_list:
        context = get_base_context("theaters", "CineMax - Theaters")
        context["theaters"] = []
        context["selected_theater"] = None
        context["selected_movie"] = None
        context["selected_screens"] = []
        context["movie_choices"] = get_now_showing_movies()
        return render_template("discovery/theaters.html", **context)

    selected_theater_id = request.args.get("theater_id", type=int)

    if selected_theater_id is None:
        selected_theater_id = theaters_list[0]["id"]

    selected_movie_id = get_request_int("movie_id", 1)

    selected_theater = fetch_theater_by_id(selected_theater_id)
    selected_movie = build_movie(get_movie(selected_movie_id))
    selected_screens = fetch_saloons_for_theater(selected_theater_id)

    context = get_base_context("theaters", "CineMax - Theaters")
    context["theaters"] = theaters_list
    context["selected_theater"] = selected_theater
    context["selected_movie"] = selected_movie
    context["selected_screens"] = selected_screens
    context["movie_choices"] = get_now_showing_movies()

    return render_template("discovery/theaters.html", **context)

@discovery_bp.route("/theater/<int:theater_id>")
def theater_detail(theater_id):
    theater = fetch_theater_by_id(theater_id)
    saloons = fetch_saloons_for_theater(theater_id)

    context = get_base_context("theaters", theater["name"] + " - CineMax")
    context["theater"] = theater
    context["saloons"] = saloons
    context["movie_choices"] = get_now_showing_movies()

    return render_template("discovery/theater_detail.html", **context)

@discovery_bp.route("/deals")
def deals():
    context = get_base_context("deals", "CineMax - Deals")
    context["deals"] = fetch_deals()
    return render_template("discovery/deals.html", **context)

@discovery_bp.route("/profile")
def profile():
    context = get_base_context("home", "Profile - CineMax")
    context["page_heading"] = "Profile"
    context["page_description"] = "Profile details can be added here later."
    return render_template("auth/login.html", **context)

def fetch_movie_cast(movie_id):
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT cast_name AS name
        FROM movie_cast
        WHERE movie_id = %s
    """

    cursor.execute(query, (movie_id,))
    cast = cursor.fetchall()

    cursor.close()
    connection.close()

    return cast

def fetch_movie_reviews(movie_id):
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            r.review_id,
            r.rating,
            r.comment,
            CONCAT(u.first_name, ' ', u.last_name) AS author
        FROM review r
        JOIN user u ON r.user_id = u.user_id
        WHERE r.movie_id = %s
        ORDER BY r.review_id DESC
    """

    cursor.execute(query, (movie_id,))
    reviews = cursor.fetchall()

    cursor.close()
    connection.close()

    return reviews

@discovery_bp.route("/movie/<int:movie_id>/review", methods=["POST"])
def submit_review(movie_id):
    if "user_id" not in session:
        flash("Please log in to submit a review.", "error")
        return redirect(url_for("auth.login", next=url_for("discovery.movie_detail", movie_id=movie_id)))

    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()

    if rating is None or rating < 1 or rating > 5:
        flash("Please select a rating between 1 and 5.", "error")
        return redirect(url_for("discovery.movie_detail", movie_id=movie_id))

    if not comment:
        flash("Please write a comment.", "error")
        return redirect(url_for("discovery.movie_detail", movie_id=movie_id))

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed.", "error")
        return redirect(url_for("discovery.movie_detail", movie_id=movie_id))

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT review_id
            FROM review
            WHERE user_id = %s AND movie_id = %s
            """,
            (session["user_id"], movie_id)
        )

        existing_review = cursor.fetchone()

        if existing_review:
            cursor.execute(
                """
                UPDATE review
                SET rating = %s,
                    comment = %s
                WHERE user_id = %s AND movie_id = %s
                """,
                (rating, comment, session["user_id"], movie_id)
            )
        else:
            cursor.execute(
                """
                INSERT INTO review
                    (user_id, movie_id, rating, comment)
                VALUES
                    (%s, %s, %s, %s)
                """,
                (session["user_id"], movie_id, rating, comment)
            )

        connection.commit()
        flash("Review submitted successfully.", "success")

    except Exception as e:
        connection.rollback()
        flash(str(e), "error")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("discovery.movie_detail", movie_id=movie_id))

def fetch_movie_rating_summary(movie_id):
    empty_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    if get_db_connection() is None:
        return {
            "avg_rating": 0,
            "total_reviews": 0,
            "distribution": empty_distribution,
        }

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COALESCE(AVG(rating), 0) AS avg_rating,
            COUNT(review_id) AS total_reviews
        FROM review
        WHERE movie_id = %s
        """,
        (movie_id,)
    )
    summary = cursor.fetchone()

    cursor.execute(
        """
        SELECT rating, COUNT(*) AS count
        FROM review
        WHERE movie_id = %s
        GROUP BY rating
        """,
        (movie_id,)
    )
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    total_reviews = int(summary["total_reviews"] or 0)

    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for row in rows:
        star = int(row["rating"])
        if star in distribution and total_reviews > 0:
            distribution[star] = round((row["count"] / total_reviews) * 100)

    return {
        "avg_rating": round(float(summary["avg_rating"] or 0), 1),
        "total_reviews": total_reviews,
        "distribution": distribution,
    }