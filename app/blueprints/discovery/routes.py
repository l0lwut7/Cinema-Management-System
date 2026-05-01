from flask import Blueprint, abort, redirect, render_template, request, url_for

from .data import COMING_SOON, DEALS, MOVIES, NAV_ITEMS, REVIEWS, THEATER_SCREENS, THEATERS

from app.db import get_db_connection


discovery_bp = Blueprint("discovery", __name__)

def fetch_now_showing_movies():
    connection = get_db_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT DISTINCT
            m.movie_id AS id,
            m.title,
            m.director,
            m.duration_mins AS duration,
            m.rating_age,
            m.release_date,
            m.summary AS synopsis
        FROM movie m
        JOIN movie_run mr ON m.movie_id = mr.movie_id
        WHERE CURDATE() BETWEEN mr.start_date AND mr.end_date
        ORDER BY m.release_date DESC
    """

    cursor.execute(query)
    movies = cursor.fetchall()

    cursor.close()
    connection.close()

    for movie in movies:
        movie["rating"] = 0
        movie["avg_rating"] = 0
        movie["status"] = "Now Showing"
        movie["genres"] = ""
        movie["format"] = ""
        movie["runtime_label"] = str(movie["duration"]) + " min"
        movie["meta"] = movie["director"]
        movie["badge"] = "Now Showing"
        movie["image_url"] = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80"
        movie["detail_url"] = url_for("discovery.movie_detail", movie_id=movie["id"])

    return movies


def fetch_coming_soon_movies():
    connection = get_db_connection()

    if connection is None:
        return []

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
        WHERE release_date > CURDATE()
        ORDER BY release_date ASC
    """

    cursor.execute(query)
    movies = cursor.fetchall()

    cursor.close()
    connection.close()

    for movie in movies:
        movie["rating"] = 0
        movie["avg_rating"] = 0
        movie["status"] = "Coming Soon"
        movie["genres"] = ""
        movie["format"] = ""
        movie["runtime_label"] = "TBA" if movie["duration"] is None else str(movie["duration"]) + " min"
        movie["meta"] = movie["director"]
        movie["badge"] = "Coming Soon"
        movie["image_url"] = "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?w=1200&q=80"
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

    movie["rating"] = 0
    movie["avg_rating"] = 0
    movie["runtime_label"] = str(movie["duration"]) + " min"
    movie["meta"] = movie["director"]
    movie["badge"] = "Movie"
    movie["image_url"] = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80"
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


def get_theater(theater_id):
    for theater in THEATERS:
        if theater["id"] == theater_id:
            return theater
    abort(404)


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
    context["is_authenticated"] = False
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
    featured_movie = now_showing[0]

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

    context = get_base_context("movies", movie["title"] + " - CineMax")
    context["movie"] = movie
    context["cast"] = cast
    context["reviews"] = reviews
    context["total_reviews"] = len(reviews)
    context["is_authenticated"] = False

    return render_template("discovery/movie_detail.html", **context)

@discovery_bp.route("/theaters")
def theaters():
    selected_theater_id = get_request_int("theater_id", 1)
    selected_movie_id = get_request_int("movie_id", 1)

    selected_theater = get_theater(selected_theater_id)
    selected_movie = build_movie(get_movie(selected_movie_id))

    context = get_base_context("theaters", "CineMax - Theaters")
    context["theaters"] = THEATERS.copy()
    context["selected_theater"] = selected_theater
    context["selected_movie"] = selected_movie
    context["selected_screens"] = THEATER_SCREENS.get(selected_theater_id, [])
    context["movie_choices"] = get_now_showing_movies()
    return render_template("discovery/theaters.html", **context)


@discovery_bp.route("/theater/<int:theater_id>")
def theater_detail(theater_id):
    theater = get_theater(theater_id)

    context = get_base_context("theaters", theater["name"] + " - CineMax")
    context["theater"] = theater
    context["saloons"] = THEATER_SCREENS.get(theater_id, [])
    context["movie_choices"] = get_now_showing_movies()
    return render_template("discovery/theater_detail.html", **context)


@discovery_bp.route("/deals")
def deals():
    context = get_base_context("deals", "CineMax - Deals")
    context["deals"] = DEALS
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