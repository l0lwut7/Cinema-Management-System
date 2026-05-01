from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/login", strict_slashes=False)
def login():
    return render_template("auth/login_register.html")

@auth_bp.route("/auth/register", strict_slashes=False)
def register():
    return render_template("auth/login_register.html")
