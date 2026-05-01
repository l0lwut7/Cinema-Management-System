from flask import Blueprint, render_template

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/booking")
def booking():
    return render_template("booking/booking.html")
