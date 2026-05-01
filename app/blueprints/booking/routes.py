from flask import Blueprint, render_template, request

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/booking")
def booking():
    movie_id = request.args.get('movie_id')
    if movie_id and movie_id.isdigit():
        movie_id = int(movie_id)
            
    # Here you would typically fetch movie details using the movie_id
    # For demonstration, we'll just pass the movie_id to the template
    return render_template("booking/booking.html", movie_id=movie_id)
