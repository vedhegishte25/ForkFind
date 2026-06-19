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
    from backend.routes.main import main

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(discover, url_prefix='/discover')
    app.register_blueprint(restaurants, url_prefix='/restaurants')
    app.register_blueprint(group, url_prefix='/group')
    app.register_blueprint(reviews, url_prefix='/reviews')
    app.register_blueprint(challenges, url_prefix='/challenges')
    app.register_blueprint(main)

# create tables and seed default data
    with app.app_context():
        db.create_all()
        seed_default_challenges()

    return app


def seed_default_challenges():
    from backend.models.challenge import Challenge

    default_challenges = [
        {
            'name': 'Thane Explorer',
            'description': 'Visit 10 unique restaurants across Thane.',
            'badge_name': 'Thane Explorer',
            'badge_icon': '🗺️',
            'target_count': 10,
            'challenge_type': 'unique_restaurants',
            'criteria': '{}'
        },
        {
            'name': 'Street Food Hunter',
            'description': 'Try 20 street food spots in your city.',
            'badge_name': 'Street Food Hunter',
            'badge_icon': '🍢',
            'target_count': 20,
            'challenge_type': 'street_food',
            'criteria': '{"cuisine": "street food"}'
        },
        {
            'name': 'Dessert Master',
            'description': 'Visit 15 dessert places and satisfy your sweet tooth.',
            'badge_name': 'Dessert Master',
            'badge_icon': '🍰',
            'target_count': 15,
            'challenge_type': 'desserts',
            'criteria': '{"cuisine": "desserts"}'
        },
        {
            'name': 'Cuisine Globetrotter',
            'description': 'Try 8 different cuisines from around the world.',
            'badge_name': 'Globetrotter',
            'badge_icon': '🌍',
            'target_count': 8,
            'challenge_type': 'cuisines',
            'criteria': '{}'
        },
        {
            'name': 'Hidden Gem Finder',
            'description': 'Discover and visit 5 hidden gem restaurants.',
            'badge_name': 'Gem Finder',
            'badge_icon': '💎',
            'target_count': 5,
            'challenge_type': 'hidden_gems',
            'criteria': '{"is_hidden_gem": true}'
        }
    ]

    for c in default_challenges:
        existing = Challenge.query.filter_by(name=c['name']).first()
        if not existing:
            challenge = Challenge(**c)
            db.session.add(challenge)

    db.session.commit()