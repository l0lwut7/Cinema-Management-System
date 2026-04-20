from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Geçici örnek veriler
now_showing_movies = [
    {
        "id": 1,
        "title": "Dune: Part Two",
        "genre": "Sci-Fi",
        "format": "IMAX 70mm",
        "status": "Releasing Today",
        "badge": "Selling Fast",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuBzAkEgFBMVPDPvyEj8zeo9oG_Xk0gr7OD7iFDP7Iw6MdcxDo_u7xFqrFasu0bfSfaMgliMUcFxf5z_qFqiW2jXcWHyughEw73XuQSTen47hXE6-SR8T0poImZ-2a6bPLygoGgN1KllH7K2e_tSZCAjuT1CEJ9fc0-34btQYp5t1_UmxNvpErZ0KTjF9lULIhmy7CmvyB_V5DLzWxEgHgwWkhVJZF8NrxdaBM1SgGBtotrbmlSJZP-vU9_IrX7Pamt57tukYh8GUiQ",
        "banner_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAEgxTDZ8EVQOhqZsHyzqHHBuvG6sjsTM1A-fuPQxIpbSUj3RmZdgwimj88Y38CCISFeXGc_E5Hv5PXwQRScs-feBPsum09mSdx6C5soSVf5LOV7a8l7KK72CSbztxyL9YPieG-kw5G23WKBWPgVfP7ReNimNyRgeHsXabKrT_-h1kQexxCstvK4xLE0zlJCTsx2x6jyRhykmwLOTQG-0dq_RabhBeYHXq2GmRMkeWA-dLG-eoIU6Z7QeGwpwcyKfmiDCvGi-jz8HE",
        "poster_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAC_wEI8pmnO9vMcHsDLxxcY7BZwLnu8YOOloJK4xDinUG3OxMPu7GoCBMTkw1zl0fF4AGuyYwVAJRyE5wOdACXVbZKl6yzUaKTvuxjajhn4IGZD-IeT5xaADaoouXXc-RuifewtGIu99l7GY--1NO1El5Y6aVxM0FqTU0qmCyAkKLJVJbFG0I-qCExdgUZR9bM6l7RYxVFt-J6wxh_WHJKfSRFMj2jgf7zlOW-HhF3XPDLWrW41A_t282MD4h4O-t_GPl4euTbxNA",
        "sold_out": False,
        "director": "Denis Villeneuve",
        "year": 2024,
        "duration": "166 min",
        "genres": ["Sci-Fi", "Adventure"],
        "description": "Paul Atreides unites with Chani and the Fremen while on a warpath of revenge against the conspirators who destroyed his family. Facing a choice between the love of his life and the fate of the known universe, he endeavors to prevent a terrible future only he can foresee.",
        "rating": 9.2,
        "review_count": 142,
        "reviews": [
            {
                "quote": "A monumental achievement in sci-fi cinema. Visually staggering.",
                "source": "The Cinematic Post"
            },
            {
                "quote": "Villeneuve crafts a sequel that surpasses the original in scale and emotional depth.",
                "source": "Frame & Lens"
            }
        ],
        "cast": [
            {"name": "Timothée Chalamet", "role": "Paul Atreides"},
            {"name": "Zendaya", "role": "Chani"},
            {"name": "Rebecca Ferguson", "role": "Lady Jessica"},
            {"name": "Javier Bardem", "role": "Stilgar"}
        ]
    },
    {
        "id": 2,
        "title": "The Archivist",
        "genre": "Drama",
        "format": "Standard",
        "status": "Limited Run",
        "badge": "",
        "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuCrpA5L7kDZTk9Wywz0N2xnqND3Z0f7O322oQXXyvLz2Jq9bxCFfBbTSw3hM5KgUB7bMamEPpnm0CawW1LOm9l3xyI5CuV5aycqV8ScMZzzFFepZbXy-I0mDXAikv5gWhOUGWelvcVir6lbix-dhu44gcuZ2lHUE1AyTYA3P9Lv97avJT_Eo6OnUpbQM-41d6vam__mTHfysNmc8cUHSitlES34W5YTootjxVPB_g4JyUv2HMwt03nkCR2J59tiL_EGexwgJi0ulg0",
        "banner_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAEgxTDZ8EVQOhqZsHyzqHHBuvG6sjsTM1A-fuPQxIpbSUj3RmZdgwimj88Y38CCISFeXGc_E5Hv5PXwQRScs-feBPsum09mSdx6C5soSVf5LOV7a8l7KK72CSbztxyL9YPieG-kw5G23WKBWPgVfP7ReNimNyRgeHsXabKrT_-h1kQexxCstvK4xLE0zlJCTsx2x6jyRhykmwLOTQG-0dq_RabhBeYHXq2GmRMkeWA-dLG-eoIU6Z7QeGwpwcyKfmiDCvGi-jz8HE",
        "poster_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAC_wEI8pmnO9vMcHsDLxxcY7BZwLnu8YOOloJK4xDinUG3OxMPu7GoCBMTkw1zl0fF4AGuyYwVAJRyE5wOdACXVbZKl6yzUaKTvuxjajhn4IGZD-IeT5xaADaoouXXc-RuifewtGIu99l7GY--1NO1El5Y6aVxM0FqTU0qmCyAkKLJVJbFG0I-qCExdgUZR9bM6l7RYxVFt-J6wxh_WHJKfSRFMj2jgf7zlOW-HhF3XPDLWrW41A_t282MD4h4O-t_GPl4euTbxNA",
        "sold_out": False,
        "director": "Mira Solberg",
        "year": 2024,
        "duration": "118 min",
        "genres": ["Drama"],
        "description": "A quiet archivist discovers a forgotten reel that alters the story of a city's past.",
        "rating": 8.4,
        "review_count": 57,
        "reviews": [
            {
                "quote": "Subtle, restrained, and emotionally precise.",
                "source": "Archive Weekly"
            }
        ],
        "cast": [
            {"name": "Alicia Voss", "role": "Elena Hart"},
            {"name": "Daniel Rowe", "role": "Martin Vale"}
        ]
    }
]

coming_soon_movies = [
    {
        "id": 101,
        "title": "The Architect",
        "genre": "Documentary",
        "format": "Standard",
        "status": "Coming Soon",
        "badge": "Oct 15",
        "image_url": "https://via.placeholder.com/400x600?text=Architect",
        "banner_url": "https://via.placeholder.com/1200x600?text=Architect+Banner",
        "poster_url": "https://via.placeholder.com/400x600?text=Architect",
        "sold_out": False,
        "director": "Liam Carter",
        "year": 2026,
        "duration": "102 min",
        "genres": ["Documentary"],
        "description": "An exploration into the minds of modern architects shaping the skylines of tomorrow.",
        "rating": 0,
        "review_count": 0,
        "reviews": [],
        "cast": [
            {"name": "Various Experts", "role": "Self"}
        ]
    },
    {
        "id": 102,
        "title": "Ocean's Depth",
        "genre": "Adventure",
        "format": "IMAX",
        "status": "Coming Soon",
        "badge": "Oct 22",
        "image_url": "https://via.placeholder.com/400x600?text=Ocean",
        "banner_url": "https://via.placeholder.com/1200x600?text=Ocean+Banner",
        "poster_url": "https://via.placeholder.com/400x600?text=Ocean",
        "sold_out": False,
        "director": "Sophie Lin",
        "year": 2026,
        "duration": "128 min",
        "genres": ["Adventure", "Nature"],
        "description": "Dive into the unexplored depths of the world's oceans and uncover hidden ecosystems.",
        "rating": 0,
        "review_count": 0,
        "reviews": [],
        "cast": [
            {"name": "Narrator", "role": "Voice"}
        ]
    },
    {
        "id": 103,
        "title": "Quantum Leap",
        "genre": "Sci-Fi",
        "format": "Dolby Atmos",
        "status": "Coming Soon",
        "badge": "Nov 05",
        "image_url": "https://via.placeholder.com/400x600?text=Quantum",
        "banner_url": "https://via.placeholder.com/1200x600?text=Quantum+Banner",
        "poster_url": "https://via.placeholder.com/400x600?text=Quantum",
        "sold_out": False,
        "director": "Ethan Cole",
        "year": 2026,
        "duration": "140 min",
        "genres": ["Sci-Fi"],
        "description": "A physicist discovers a way to travel between timelines—but every jump changes reality.",
        "rating": 0,
        "review_count": 0,
        "reviews": [],
        "cast": [
            {"name": "Unknown", "role": "TBA"}
        ]
    }
]

deals = [
    {
        "id": 1,
        "title": "Join The Director's Club",
        "type": "Membership",
        "description": "Unlimited screenings, priority booking, and exclusive invites."
    },
    {
        "id": 2,
        "title": "Half-Price Matinees",
        "type": "Student Pass",
        "description": "50% off all screenings before 5 PM on weekdays."
    }
]

deals = [
    {
        "id": 1,
        "title": "The Auteur Collection Pass",
        "category": "Premium",
        "description": "Gain unlimited access to independent and international cinema screenings for the entire season. Includes priority seating and complimentary gallery lounge access.",
        "price": 149,
        "old_price": 299,
        "badge": "Ends in 3 days",
        "button_text": "Claim Offer",
        "highlighted": True,
        "icon": "local_activity"
    },
    {
        "id": 2,
        "title": "Matinee Magic",
        "category": "Weekday Offer",
        "description": "Enjoy 40% off all screenings before 4 PM, Tuesday through Thursday. Perfect for a quiet cinematic escape.",
        "price": None,
        "old_price": None,
        "badge": "Valid till Dec 31",
        "button_text": "View Details",
        "highlighted": False,
        "icon": "schedule"
    },
    {
        "id": 3,
        "title": "Cinephile Duo",
        "category": "Companion Deal",
        "description": "Bring a companion. Buy one general admission ticket and get the second at half price. Applies to all standard screenings.",
        "price": None,
        "old_price": None,
        "badge": "Ongoing",
        "button_text": "View Details",
        "highlighted": False,
        "icon": "group"
    },
    {
        "id": 4,
        "title": "Curated Concessions",
        "category": "Members Only",
        "description": "Complimentary artisanal popcorn pairing or a glass of select wine with any evening premiere ticket purchase.",
        "price": None,
        "old_price": None,
        "badge": "Members Only",
        "button_text": "View Details",
        "highlighted": False,
        "icon": "restaurant"
    }
]

@app.route("/")
def home():
    return render_template(
        "home.html",
        now_showing_movies=now_showing_movies,
        coming_soon_movies=coming_soon_movies,
        deals=deals
    )

@app.route("/nowshowing")
def now_showing():
    return render_template("nowshowing.html", movies=now_showing_movies)

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    all_movies = now_showing_movies + coming_soon_movies
    movie = next((movie for movie in all_movies if movie["id"] == movie_id), None)

    if not movie:
        return "Movie not found", 404

    return render_template("moviedetail.html", movie=movie)

@app.route("/comingsoon")
def coming_soon():
    return render_template("comingsoon.html", movies=coming_soon_movies)

@app.route("/deals")
def deals_page():
    return render_template("deals.html", deals=deals)


@app.route("/subscription")
def subscription_page():
    return render_template("subscription.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Şimdilik sahte kontrol
        if email == "admin@example.com" and password == "1234":
            return redirect(url_for("home"))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Şimdilik sadece ekrana/loga düşünebilirsin
        print("New user:", full_name, email)

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/booking/<int:movie_id>")
def booking(movie_id):
    all_movies = now_showing_movies + coming_soon_movies
    movie = next((movie for movie in all_movies if movie["id"] == movie_id), None)

    if not movie:
        return "Movie not found", 404

    return render_template("booking.html", movie=movie)


if __name__ == "__main__":
    app.run(debug=True)