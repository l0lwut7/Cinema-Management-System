from flask import Blueprint, render_template, session, redirect, url_for
from .data import TICKETS, SNACKS, DRINKS, COMBOS, STAFF

staff_bp = Blueprint("staff", __name__)


@staff_bp.route("/staff/terminal", strict_slashes=False)
def terminal():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template(
        "staff/terminal.html",
        tickets=TICKETS,
        snacks=SNACKS,
        drinks=DRINKS,
        combos=COMBOS,
        staff=STAFF,
    )
