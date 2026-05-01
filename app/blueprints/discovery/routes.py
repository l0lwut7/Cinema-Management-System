from flask import Blueprint, abort, redirect, render_template, request, url_for

from .data import COMING_SOON, DEALS, MOVIES, NAV_ITEMS, REVIEWS, THEATER_SCREENS, THEATERS


discovery_bp = Blueprint("discovery", __name__)


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
    for movie in MOVIES:
        if movie["id"] == movie_id:
            return movie
    abort(404)


def get_theater(theater_id):
    for theater in THEATERS:
        if theater["id"] == theater_id:
            return theater
    abort(404)


def get_now_showing_movies():
    movies = []
    for movie in MOVIES:
        if movie["status"] == "Now Showing":
            movies.append(build_movie(movie))
    return movies


def get_coming_soon_movies():
    return build_movies(COMING_SOON)


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
    movie_data = get_movie(movie_id)
    movie = build_movie(movie_data)

    context = get_base_context("movies", movie["title"] + " - CineMax")
    context["movie"] = movie
    context["cast"] = movie_data.get("cast", [])
    context["reviews"] = REVIEWS
    context["total_reviews"] = 128
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

