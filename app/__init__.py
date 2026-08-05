from flask import Flask


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Using an application factory keeps the project modular and makes
    testing and configuration easier as the system grows.
    """
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return "Emotional Wellbeing Analysis System is running."

    return app