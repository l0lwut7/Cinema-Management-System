from flask import Blueprint, render_template, request, session, redirect, url_for

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/login", methods=["GET", "POST"], strict_slashes=False)
def login():
    if request.method == "POST":
        # Mock session login
        session['user_id'] = 1
        session['user_name'] = "John Doe"
        return redirect(url_for('dashboard.dashboard'))
    return render_template("auth/login_register.html")

@auth_bp.route("/auth/register", methods=["GET", "POST"], strict_slashes=False)
def register():
    if request.method == "POST":
        # Mock session registration
        session['user_id'] = 1
        session['user_name'] = request.form.get('first_name', 'John') + " " + request.form.get('last_name', 'Doe')
        return redirect(url_for('dashboard.dashboard'))
    return render_template("auth/login_register.html")

@auth_bp.route("/auth/logout", strict_slashes=False)
def logout():
    session.clear()
    return redirect(url_for('discovery.home'))
