from flask import Flask
from flask_login import LoginManager
from dev.config_db import Config_db
from dev.extensions import db
from domain.user import User

def create_app(config_class=Config_db):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.auth_handler'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Регистрация blueprint'ов
    from controller.authController import auth_bp
    app.register_blueprint(auth_bp)

    from controller.mainPageController import mainPage
    app.register_blueprint(mainPage)

    from controller.cartController import cart_bp
    app.register_blueprint(cart_bp)

    from controller.orderController import orders_bp
    app.register_blueprint(orders_bp)

    with app.app_context():
        # Убедитесь, что все модели импортированы до этой строки
        db.configure_mappers()  # Важно!
        db.create_all()

    return app