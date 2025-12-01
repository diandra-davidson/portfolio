from flask import Flask
from flask_bootstrap import Bootstrap5


def create_app():
    app = Flask(__name__)
    return app


def setup_bootstrap(app: Flask) -> None:
    Bootstrap5(app)
    return


app = create_app()
setup_bootstrap(app)
