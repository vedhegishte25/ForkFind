from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config.from_object(config[config_name])

    # initialise extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # register blueprints
    from backend.routes.auth import auth
    from backend.routes.profile import profile
    from backend.routes.discover import discover
    from backend.routes.restaurants import restaurants
    from backend.routes.group import group
    from backend.routes.reviews import reviews
    from backend.routes.challenges import challenges

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(discover, url_prefix='/discover')
    app.register_blueprint(restaurants, url_prefix='/restaurants')
    app.register_blueprint(group, url_prefix='/group')
    app.register_blueprint(reviews, url_prefix='/reviews')
    app.register_blueprint(challenges, url_prefix='/challenges')

    # create tables
    with app.app_context():
        db.create_all()

    return app