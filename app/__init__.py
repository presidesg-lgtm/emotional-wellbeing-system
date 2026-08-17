from flask import Flask, render_template

from config import Config
from app.routes.analysis import analysis_blueprint
from app.routes.auth import auth_blueprint


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Using an application factory keeps the project modular and makes
    testing and configuration easier as the system grows.
    """

    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(analysis_blueprint)
    app.register_blueprint(auth_blueprint)

    @app.get("/")
    def index():
        return render_template("index.html")

    return app