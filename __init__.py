from flask import Flask
from flask_bootstrap import Bootstrap5

bootstrap = Bootstrap5()

def create_app():
    app = Flask(__name__, template_folder="templates")

    bootstrap.init_app(app)

    from .main import bp
    app.register_blueprint(bp)

    return app
