from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard", strict_slashes=False)
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template("dashboard/dashboard.html", user_name=session.get('user_name', 'John Doe'))
