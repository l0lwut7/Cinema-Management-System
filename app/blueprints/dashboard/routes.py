from flask import Blueprint, render_template, session, redirect, url_for

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


@dashboard_bp.route("/dashboard", strict_slashes=False)
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    favorite_movies = get_user_favorite_movies(session['user_id'])
    return render_template(
        "dashboard/dashboard.html",
        user_name=session.get('user_name', 'John Doe'),
        favorite_movies=favorite_movies
    )
