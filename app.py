from flask import Flask

from config import SECRET_KEY
from db import init_db
from blueprints.auth import auth_bp
from blueprints.classify import classify_bp
from blueprints.results import results_bp
from blueprints.extension import extension_bp
from blueprints.extension_api import extension_api

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Ініціалізація БД
    init_db()

    # Реєстрація blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(classify_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(extension_bp)
    app.register_blueprint(extension_api)

    return app

if __name__ == '__main__':
    create_app().run(port=5000, debug=True, use_reloader=False)
