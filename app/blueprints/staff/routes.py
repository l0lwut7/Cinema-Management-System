from flask import Blueprint, render_template, session, redirect, url_for, request, flash

from .data import TICKETS, SNACKS, DRINKS, COMBOS, STAFF

staff_bp = Blueprint("staff", __name__)


@staff_bp.route("/staff/login", methods=["GET", "POST"], strict_slashes=False)
def login():
    if request.method == "POST":
        # Mock staff authentication
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == "admin" and password == "admin":
            session['staff_id'] = 1
            return redirect(url_for('staff.terminal'))
        else:
            flash("Invalid credentials", "error")
            
    return render_template("staff/login.html")

@staff_bp.route("/staff/logout", strict_slashes=False)
def logout():
    session.pop('staff_id', None)
    return redirect(url_for('staff.login'))

@staff_bp.route("/staff/terminal", strict_slashes=False)
def terminal():
    if 'staff_id' not in session:
        return redirect(url_for('staff.login'))
    return render_template(
        "staff/terminal.html",
        tickets=TICKETS,
        snacks=SNACKS,
        drinks=DRINKS,
        combos=COMBOS,
        staff=STAFF,
    )
