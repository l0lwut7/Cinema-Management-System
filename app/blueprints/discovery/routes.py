from __future__ import annotations

from copy import deepcopy

from flask import Blueprint, abort, redirect, render_template, request, url_for

discovery_bp = Blueprint("discovery", __name__)

NAV_ITEMS = [
    ("home", "Home", "discovery.home"),
    ("movies", "Movies", "discovery.movies"),
    ("coming_soon", "Coming Soon", "discovery.coming_soon"),
    ("theaters", "Theaters", "discovery.theaters"),
    ("deals", "Deals", "discovery.deals"),
]

MOVIES = [
    {
        "id": 1,
        "title": "Dune: Part Two",
        "duration": 166,
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200&q=80",
        "genres": "Sci-Fi, Adventure",
        "format": "IMAX",
        "synopsis": "Paul Atreides unites with the Fremen while seeking revenge and destiny.",
        "avg_rating": 4.8,
        "release_date": "March 1, 2024",
        "status": "Now Showing",
        "director": "Denis Villeneuve",
        "language": "English",
        "runtime_label": "2h 46min",
        "meta": "Epic sci-fi",
        "badge": "Featured",
        "showtimes": ["10:30 AM", "2:00 PM", "6:30 PM", "9:45 PM"],
        "theater_showtimes": {
            "CineMax Downtown": ["10:30 AM", "2:00 PM", "6:30 PM", "9:45 PM"],
            "CineMax Mall": ["11:00 AM", "3:30 PM", "7:00 PM"],
        },
        "cast": [
            {
                "name": "Timothee Chalamet",
                "role": "Paul Atreides",
                "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80",
            },
            {
                "name": "Zendaya",
                "role": "Chani",
                "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&q=80",
            },
            {
                "name": "Rebecca Ferguson",
                "role": "Lady Jessica",
                "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&q=80",
            },
        ],
    },
    {
        "id": 2,
        "title": "Oppenheimer",
        "duration": 180,
        "rating": 4.9,
        "image_url": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1200&q=80",
        "genres": "Drama, Biography",
        "format": "70mm IMAX",
        "synopsis": "The story of J. Robert Oppenheimer and the creation of the atomic bomb.",
        "avg_rating": 4.9,
        "release_date": "July 21, 2023",
        "status": "Now Showing",
        "director": "Christopher Nolan",
        "language": "English",
        "runtime_label": "3h 0min",
        "meta": "Award-winning drama",
        "badge": "Top Rated",
        "showtimes": ["1:15 PM", "4:45 PM", "8:10 PM"],
        "theater_showtimes": {
            "CineMax Downtown": ["1:15 PM", "4:45 PM", "8:10 PM"],
            "CineMax Mall": ["12:20 PM", "5:30 PM"],
        },
        "cast": [
            {
                "name": "Cillian Murphy",
                "role": "J. Robert Oppenheimer",
                "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80",
            },
            {
                "name": "Emily Blunt",
                "role": "Kitty Oppenheimer",
                "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&q=80",
            },
            {
                "name": "Matt Damon",
                "role": "Leslie Groves",
                "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&q=80",
            },
        ],
    },
    {
        "id": 3,
        "title": "Poor Things",
        "duration": 141,
        "rating": 4.6,
        "image_url": "https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=1200&q=80",
        "genres": "Comedy, Drama",
        "format": "Premium",
        "synopsis": "A bizarre and brilliant journey of rebirth, self-discovery, and freedom.",
        "avg_rating": 4.6,
        "release_date": "December 8, 2023",
        "status": "Now Showing",
        "director": "Yorgos Lanthimos",
        "language": "English",
        "runtime_label": "2h 21min",
        "meta": "Stylish dark comedy",
        "badge": "Popular",
        "showtimes": ["11:10 AM", "3:05 PM", "7:20 PM"],
        "theater_showtimes": {
            "CineMax Downtown": ["11:10 AM", "3:05 PM", "7:20 PM"],
            "CineMax IMAX": ["1:00 PM", "6:15 PM"],
        },
        "cast": [
            {
                "name": "Emma Stone",
                "role": "Bella Baxter",
                "image_url": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=300&q=80",
            },
            {
                "name": "Mark Ruffalo",
                "role": "Duncan Wedderburn",
                "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80",
            },
            {
                "name": "Willem Dafoe",
                "role": "Dr. Godwin Baxter",
                "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&q=80",
            },
        ],
    },
    {
        "id": 4,
        "title": "Godzilla x Kong",
        "duration": 115,
        "rating": 4.3,
        "image_url": "https://images.unsplash.com/photo-1535016120720-40c646be5580?w=1200&q=80",
        "genres": "Action, Sci-Fi",
        "format": "Dolby Atmos",
        "synopsis": "Titans clash again in a loud, fast, and larger-than-life showdown.",
        "avg_rating": 4.3,
        "release_date": "April 12, 2024",
        "status": "Now Showing",
        "director": "Adam Wingard",
        "language": "English",
        "runtime_label": "1h 55min",
        "meta": "Monster spectacle",
        "badge": "Blockbuster",
        "showtimes": ["12:40 PM", "5:10 PM", "8:40 PM"],
        "theater_showtimes": {
            "CineMax Mall": ["12:40 PM", "5:10 PM", "8:40 PM"],
            "CineMax IMAX": ["2:20 PM", "7:50 PM"],
        },
        "cast": [
            {
                "name": "Rebecca Hall",
                "role": "Ilene Andrews",
                "image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&q=80",
            },
            {
                "name": "Brian Tyree Henry",
                "role": "Bernie Hayes",
                "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&q=80",
            },
            {
                "name": "Dan Stevens",
                "role": "Trapper",
                "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&q=80",
            },
        ],
    },
]

COMING_SOON = [
    {
        "id": 5,
        "title": "Inside Out 2",
        "duration": 0,
        "rating": 0,
        "image_url": "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?w=1200&q=80",
        "genres": "Animation, Family",
        "format": "Dolby Atmos",
        "synopsis": "New emotions arrive just in time to make life far more complicated.",
        "avg_rating": 0,
        "release_date": "June 14, 2026",
        "status": "Coming Soon",
        "director": "Kelsey Mann",
        "language": "English",
        "runtime_label": "TBA",
        "meta": "Family favorite",
        "badge": "Coming Soon",
    },
    {
        "id": 6,
        "title": "Deadpool & Wolverine",
        "duration": 0,
        "rating": 0,
        "image_url": "https://images.unsplash.com/photo-1513106580091-1d82408b8cd6?w=1200&q=80",
        "genres": "Action, Comedy",
        "format": "IMAX",
        "synopsis": "The loudest duo of the summer finally shows up.",
        "avg_rating": 0,
        "release_date": "July 26, 2026",
        "status": "Coming Soon",
        "director": "Shawn Levy",
        "language": "English",
        "runtime_label": "TBA",
        "meta": "Summer event",
        "badge": "Anticipated",
    },
    {
        "id": 7,
        "title": "Joker: Folie a Deux",
        "duration": 0,
        "rating": 0,
        "image_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80",
        "genres": "Drama, Musical",
        "format": "Premium",
        "synopsis": "Arthur and Harley take the stage in a darker, stranger chapter.",
        "avg_rating": 0,
        "release_date": "October 4, 2026",
        "status": "Coming Soon",
        "director": "Todd Phillips",
        "language": "English",
        "runtime_label": "TBA",
        "meta": "Event release",
        "badge": "New",
    },
    {
        "id": 8,
        "title": "Avatar 3",
        "duration": 0,
        "rating": 0,
        "image_url": "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=1200&q=80",
        "genres": "Sci-Fi, Adventure",
        "format": "3D IMAX",
        "synopsis": "Return to Pandora with even bigger visuals and more world-building.",
        "avg_rating": 0,
        "release_date": "December 19, 2026",
        "status": "Coming Soon",
        "director": "James Cameron",
        "language": "English",
        "runtime_label": "TBA",
        "meta": "Visual event",
        "badge": "Soon",
    },
]

THEATERS = [
    {
        "id": 1,
        "name": "CineMax Downtown",
        "address": "123 Main Street, City Center",
        "status": "Open",
        "distance": "2.5 km",
        "screens": 8,
        "image_url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=900&q=80",
        "phone": "+90 232 000 00 00",
        "manager_name": "Ayse Demir",
    },
    {
        "id": 2,
        "name": "CineMax Mall",
        "address": "456 Shopping Ave, West Mall",
        "status": "Open",
        "distance": "5.8 km",
        "screens": 12,
        "image_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=900&q=80",
        "phone": "+90 232 111 11 11",
        "manager_name": "Mert Kaya",
    },
    {
        "id": 3,
        "name": "CineMax IMAX",
        "address": "789 Tech Park, Innovation District",
        "status": "Closing Soon",
        "distance": "8.2 km",
        "screens": 6,
        "image_url": "https://images.unsplash.com/photo-1510827740546-f1f1d4f8ae82?w=900&q=80",
        "phone": "+90 232 222 22 22",
        "manager_name": "Selin Acar",
    },
]

THEATER_SCREENS = {
    1: [
        {"name": "Screen 1", "type": "IMAX", "capacity": 350, "features": "Dolby Atmos, 4K Laser", "status": "Available"},
        {"name": "Screen 2", "type": "Premium", "capacity": 180, "features": "Recliner Seats, Dolby 7.1", "status": "Available"},
        {"name": "Screen 3", "type": "Standard", "capacity": 220, "features": "Digital 2K, Surround Sound", "status": "Maintenance"},
        {"name": "Screen 4", "type": "Standard", "capacity": 200, "features": "Digital 2K, 5.1 Audio", "status": "Available"},
    ],
    2: [
        {"name": "Screen 1", "type": "4DX", "capacity": 120, "features": "Motion Seats, Environmental Effects", "status": "Available"},
        {"name": "Screen 2", "type": "Premium", "capacity": 200, "features": "Recliner Seats, Dolby Atmos", "status": "Available"},
        {"name": "Screen 3", "type": "Standard", "capacity": 250, "features": "Digital 4K, 7.1 Audio", "status": "Available"},
        {"name": "Screen 4", "type": "Kids", "capacity": 100, "features": "Family Friendly, Low Volume", "status": "Available"},
    ],
    3: [
        {"name": "IMAX 1", "type": "IMAX", "capacity": 500, "features": "Dual 4K Laser, 12-Channel Audio", "status": "Available"},
        {"name": "IMAX 2", "type": "IMAX", "capacity": 400, "features": "Single 4K Laser, Dolby Atmos", "status": "Available"},
        {"name": "Screen 3", "type": "Premium", "capacity": 180, "features": "Recliner Seats, Dolby 7.1", "status": "Closed"},
    ],
}

REVIEWS = [
    {
        "author": "John D.",
        "rating": 5,
        "date": "2 days ago",
        "comment": "Absolutely stunning. The visuals are breathtaking and the pacing never lets up.",
        "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&q=80",
    },
    {
        "author": "Aylin S.",
        "rating": 4,
        "date": "1 week ago",
        "comment": "Big-screen energy done right. Great sound and a strong atmosphere.",
        "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&q=80",
    },
]

BOOKING_DEFAULTS = {
    "movie_id": 1,
    "theater_id": 1,
    "showtime": "7:30 PM",
    "step": 2,
}


def _normalize_movie(movie: dict) -> dict:
    movie = deepcopy(movie)
    movie.setdefault("detail_url", url_for("discovery.movie_detail", movie_id=movie["id"]))
    movie.setdefault("book_url", url_for("discovery.booking") + f"?movie_id={movie['id']}")
    return movie


def _base_context(active_page: str, title: str):
    return {
        "active_page": active_page,
        "page_title": title,
        "nav_items": NAV_ITEMS,
        "is_authenticated": False,
        "user_name": "Guest",
        "login_url": url_for("discovery.login"),
        "profile_url": url_for("discovery.profile"),
        "search_url": url_for("discovery.movies"),
        "deals_url": url_for("discovery.deals"),
    }


def _movie_detail_context(movie_id: int):
    movie = next((item for item in MOVIES if item["id"] == movie_id), None)
    if movie is None:
        abort(404)
    return movie


def _theater_detail_context(theater_id: int):
    theater = next((item for item in THEATERS if item["id"] == theater_id), None)
    if theater is None:
        abort(404)
    return theater


@discovery_bp.route("/")
def home():
    now_showing = [_normalize_movie(movie) for movie in MOVIES if movie["status"] == "Now Showing"]
    coming_soon = [_normalize_movie(movie) for movie in COMING_SOON]
    featured_movie = now_showing[0]
    context = _base_context("home", "CineMax - Home")
    context.update(
        {
            "featured_movie": featured_movie,
            "now_showing": now_showing,
            "coming_soon": coming_soon,
        }
    )
    return render_template("discovery/home.html", **context)


@discovery_bp.route("/movies")
def movies():
    query = request.args.get("q", "").strip().lower()
    all_movies = [_normalize_movie(movie) for movie in MOVIES]
    if query:
        all_movies = [movie for movie in all_movies if query in movie["title"].lower() or query in movie["genres"].lower()]

    context = _base_context("movies", "CineMax - Movies")
    context.update({"movies": all_movies, "query": request.args.get("q", "")})
    return render_template("discovery/movies.html", **context)


@discovery_bp.route("/coming-soon")
def coming_soon():
    context = _base_context("coming_soon", "CineMax - Coming Soon")
    context.update({"coming_soon": [_normalize_movie(movie) for movie in COMING_SOON]})
    return render_template("discovery/coming_soon.html", **context)


@discovery_bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id: int):
    movie = _movie_detail_context(movie_id)
    context = _base_context("movies", f"{movie['title']} - CineMax")
    context.update(
        {
            "movie": _normalize_movie(movie),
            "cast": movie.get("cast", []),
            "reviews": REVIEWS,
            "total_reviews": 128,
            "is_authenticated": False,
        }
    )
    return render_template("discovery/movie_detail.html", **context)


@discovery_bp.route("/theaters")
def theaters():
    selected_theater_id = request.args.get("theater_id", type=int) or 1
    selected_movie_id = request.args.get("movie_id", type=int) or 1
    selected_theater = _theater_detail_context(selected_theater_id)
    context = _base_context("theaters", "CineMax - Theaters")
    context.update(
        {
            "theaters": deepcopy(THEATERS),
            "selected_theater": selected_theater,
            "selected_movie": _normalize_movie(_movie_detail_context(selected_movie_id)),
            "selected_screens": THEATER_SCREENS[selected_theater_id],
            "movie_choices": [_normalize_movie(movie) for movie in MOVIES],
        }
    )
    return render_template("discovery/theaters.html", **context)


@discovery_bp.route("/theater/<int:theater_id>")
def theater_detail(theater_id: int):
    theater = _theater_detail_context(theater_id)
    context = _base_context("theaters", f"{theater['name']} - CineMax")
    context.update(
        {
            "theater": theater,
            "saloons": THEATER_SCREENS[theater_id],
            "movie_choices": [_normalize_movie(movie) for movie in MOVIES],
        }
    )
    return render_template("discovery/theater_detail.html", **context)


@discovery_bp.route("/booking")
@discovery_bp.route("/book/<int:movie_id>")
def booking(movie_id: int | None = None):
    selected_movie_id = movie_id or request.args.get("movie_id", type=int) or BOOKING_DEFAULTS["movie_id"]
    selected_theater_id = request.args.get("theater_id", type=int) or BOOKING_DEFAULTS["theater_id"]
    showtime = request.args.get("showtime", BOOKING_DEFAULTS["showtime"])

    movie = _normalize_movie(_movie_detail_context(selected_movie_id))
    theater = _theater_detail_context(selected_theater_id)
    screenings = THEATER_SCREENS[selected_theater_id]
    context = _base_context("movies", f"Booking - {movie['title']}")
    context.update(
        {
            "movie": movie,
            "theater": theater,
            "selected_showtime": showtime,
            "screens": screenings,
            "movie_choices": [_normalize_movie(movie_item) for movie_item in MOVIES],
            "theater_choices": deepcopy(THEATERS),
        }
    )
    return render_template("discovery/booking.html", **context)


@discovery_bp.route("/deals")
def deals():
    context = _base_context("deals", "CineMax - Deals")
    context.update(
        {
            "deals": [
                {
                    "title": "Weekend Combo",
                    "description": "Save on tickets, popcorn, and drinks for Friday to Sunday shows.",
                    "tag": "Popular",
                },
                {
                    "title": "Student Night",
                    "description": "Discounted tickets for verified students before 6 PM.",
                    "tag": "Campus",
                },
                {
                    "title": "Family Pack",
                    "description": "Bundle pricing for 4 tickets plus snacks.",
                    "tag": "Family",
                },
            ]
        }
    )
    return render_template("discovery/deals.html", **context)


@discovery_bp.route("/auth/login")
def login():
    context = _base_context("home", "Login - CineMax")
    context.update({"page_heading": "Login", "page_description": "Authentication flow can be plugged in here later."})
    return render_template("auth/login.html", **context)


@discovery_bp.route("/profile")
def profile():
    context = _base_context("home", "Profile - CineMax")
    context.update(
        {
            "is_authenticated": True,
            "user_name": "CineMax Member",
            "page_heading": "Profile",
            "page_description": "Profile page placeholder for the authenticated state.",
        }
    )
    return render_template("auth/login.html", **context)
