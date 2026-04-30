from flask import Flask
from flask_bootstrap import Bootstrap5 # type: ignore


def create_app():
    app = Flask(__name__, template_folder="templates")

    from .main import bp
    app.register_blueprint(bp)
    
    return app


def setup_bootstrap(app: Flask) -> None:
    Bootstrap5(app)
    return


app = create_app()
setup_bootstrap(app)
