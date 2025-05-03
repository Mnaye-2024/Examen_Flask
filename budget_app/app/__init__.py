import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
from datetime import datetime
from babel.numbers import format_currency

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///../instance/budget.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @app.template_filter('currency')
    def currency_filter(value):
        """Filtre Jinja pour formater un nombre en devise XOF."""
        if value is None:
            return ""
        return format_currency(value, 'XOF', locale='fr_FR')

    @app.context_processor
    def inject_now():
        """Rend la date/heure actuelle disponible pour tous les templates."""
        return {'now': datetime.utcnow()}


    from .routes import main_bp
    app.register_blueprint(main_bp)

    from . import models

    return app