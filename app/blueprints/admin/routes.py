from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from .data import VIP_SPENDERS, EMPLOYEES, MOVIES, UPCOMING_SCREENINGS, SALOONS, CONSUMABLES, DEALS, VIP_TIER, GENRES, FORMATS

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/login", methods=["GET", "POST"], strict_slashes=False)
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Mock admin auth
        if username == "admin" and password == "admin":
            session['admin_id'] = 1
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Invalid credentials", "error")
            
    return render_template("admin/login.html")

@admin_bp.route("/admin/logout", strict_slashes=False)
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin.login'))

@admin_bp.route("/admin/dashboard", strict_slashes=False)
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
        
    return render_template(
        "admin/dashboard.html",
        vip_spenders=VIP_SPENDERS,
        employees=EMPLOYEES,
        movies=MOVIES,
        upcoming_screenings=UPCOMING_SCREENINGS,
        saloons=SALOONS,
        consumables=CONSUMABLES,
        deals=DEALS,
        vip_tier=VIP_TIER,
        genres=GENRES,
        formats=FORMATS
    )
