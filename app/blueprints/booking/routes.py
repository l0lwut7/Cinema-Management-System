from flask import Blueprint, render_template

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/booking")
def booking():
    return render_template("booking/booking.html")

@booking_bp.route("/booking/<int:movie_id>")
def booking_movie(movie_id):
    # Here you would typically fetch movie details using the movie_id
    # For demonstration, we'll just pass the movie_id to the template
    return render_template("booking/booking.html", movie_id=movie_id)
