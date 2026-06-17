from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend import db
from backend.models.challenge import Challenge, UserChallenge
from backend.models.restaurant import Restaurant
from datetime import datetime

challenges = Blueprint('challenges', __name__)


@challenges.route('/')
@login_required
def index():
    # get all active challenges
    all_challenges = Challenge.query.filter_by(is_active=True).all()

    # get user's enrolled challenges
    user_challenges = UserChallenge.query.filter_by(
        user_id=current_user.id
    ).all()

    enrolled_ids = [uc.challenge_id for uc in user_challenges]

    # separate enrolled and available
    enrolled = [uc for uc in user_challenges]
    available = [c for c in all_challenges if c.id not in enrolled_ids]

    completed_count = len([uc for uc in user_challenges if uc.completed])
    total_badges = completed_count

    return render_template('challenges.html',
                           enrolled=enrolled,
                           available=available,
                           completed_count=completed_count,
                           total_badges=total_badges)


@challenges.route('/enroll/<int:challenge_id>', methods=['POST'])
@login_required
def enroll(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)

    # check if already enrolled
    existing = UserChallenge.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge_id
    ).first()

    if existing:
        return jsonify({'error': 'Already enrolled in this challenge'}), 400

    user_challenge = UserChallenge(
        user_id=current_user.id,
        challenge_id=challenge_id
    )

    db.session.add(user_challenge)
    db.session.commit()

    return jsonify({
        'message': f'Enrolled in {challenge.name}',
        'challenge': {
            'id': challenge.id,
            'name': challenge.name,
            'badge_name': challenge.badge_name,
            'target_count': challenge.target_count
        }
    })


@challenges.route('/checkin', methods=['POST'])
@login_required
def checkin():
    data = request.get_json()
    challenge_id = data.get('challenge_id')
    restaurant_id = data.get('restaurant_id')

    if not challenge_id or not restaurant_id:
        return jsonify({'error': 'Challenge and restaurant are required'}), 400

    user_challenge = UserChallenge.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge_id
    ).first()

    if not user_challenge:
        return jsonify({'error': 'Not enrolled in this challenge'}), 400

    if user_challenge.completed:
        return jsonify({'error': 'Challenge already completed'}), 400

    restaurant = Restaurant.query.get_or_404(restaurant_id)

    # add checkin
    user_challenge.add_checkin(restaurant_id)

    # check if challenge is now complete
    if user_challenge.current_count >= user_challenge.challenge.target_count:
        user_challenge.completed = True
        user_challenge.completed_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': f'🎉 Challenge complete! You earned the {user_challenge.challenge.badge_name} badge!',
            'completed': True,
            'badge': user_challenge.challenge.badge_name,
            'progress': user_challenge.to_dict()
        })

    db.session.commit()

    return jsonify({
        'message': f'Checked in at {restaurant.name}',
        'completed': False,
        'progress': user_challenge.to_dict()
    })


@challenges.route('/progress')
@login_required
def progress():
    user_challenges = UserChallenge.query.filter_by(
        user_id=current_user.id
    ).all()

    return jsonify({
        'challenges': [uc.to_dict() for uc in user_challenges],
        'total_enrolled': len(user_challenges),
        'total_completed': len([uc for uc in user_challenges if uc.completed])
    })


@challenges.route('/seed', methods=['POST'])
def seed_challenges():
    # seed default challenges into database
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
    return jsonify({'message': 'Challenges seeded successfully'})