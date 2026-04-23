from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secret_key_for_flash_messages"

    @app.route("/")
    def home():
        return render_template("base.html")

    @app.route("/styleguide")
    def styleguide():
        return render_template("styleguide.html")

    @app.route("/components")
    def components():
        return render_template("components.html")

    return app
