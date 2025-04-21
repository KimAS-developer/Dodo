from flask import Flask

from dev.extensions import db
from dev.config_db import Config_db

def create_app(config_class=Config_db):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)

    db.init_app(app)

    from controller.authController import user  # обязательно после db.init_app
    app.register_blueprint(user)

    from controller.mainPageController import mainPage
    app.register_blueprint(mainPage)

    with app.app_context():
        db.create_all()

    return app
