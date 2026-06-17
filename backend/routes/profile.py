from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from backend import db
from backend.models.food_profile import FoodProfile
from backend.models.review import Review
from backend.models.challenge import UserChallenge
from backend.services.dna_engine import update_food_dna

profile = Blueprint('profile', __name__)


@profile.route('/')
@login_required
def view_profile():
    food_profile = FoodProfile.query.filter_by(user_id=current_user.id).first()
    user_challenges = UserChallenge.query.filter_by(user_id=current_user.id).all()
    recent_reviews = Review.query.filter_by(user_id=current_user.id)\
                                 .order_by(Review.created_at.desc())\
                                 .limit(5).all()

    food_dna = food_profile.get_food_dna() if food_profile else {}
    completed_challenges = [c for c in user_challenges if c.completed]
    active_challenges = [c for c in user_challenges if not c.completed]

    return render_template('profile.html',
                           user=current_user,
                           food_profile=food_profile,
                           food_dna=food_dna,
                           completed_challenges=completed_challenges,
                           active_challenges=active_challenges,
                           recent_reviews=recent_reviews)


@profile.route('/update', methods=['POST'])
@login_required
def update_profile():
    food_profile = FoodProfile.query.filter_by(user_id=current_user.id).first()

    if not food_profile:
        flash('Profile not found.', 'error')
        return redirect(url_for('profile.view_profile'))

    # update basic preferences
    food_profile.spice_tolerance = int(request.form.get('spice_tolerance', food_profile.spice_tolerance))
    food_profile.diet_type = request.form.get('diet_type', food_profile.diet_type)
    food_profile.budget_min = int(request.form.get('budget_min', food_profile.budget_min))
    food_profile.budget_max = int(request.form.get('budget_max', food_profile.budget_max))

    # update vibes and cuisines
    vibes = request.form.getlist('vibes')
    cuisines = request.form.getlist('cuisines')

    if vibes:
        food_profile.set_vibes(vibes)
    if cuisines:
        food_profile.set_cuisines(cuisines)

    # update user city
    city = request.form.get('city')
    if city:
        current_user.city = city

    db.session.commit()
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('profile.view_profile'))


@profile.route('/dna')
@login_required
def get_dna():
    food_profile = FoodProfile.query.filter_by(user_id=current_user.id).first()
    if not food_profile:
        return jsonify({'error': 'Profile not found'}), 404

    return jsonify({
        'food_dna': food_profile.get_food_dna(),
        'spice_tolerance': food_profile.spice_tolerance,
        'diet_type': food_profile.diet_type,
        'budget_min': food_profile.budget_min,
        'budget_max': food_profile.budget_max,
        'vibes': food_profile.get_vibes(),
        'cuisines': food_profile.get_cuisines()
    })


@profile.route('/dna/refresh')
@login_required
def refresh_dna():
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    food_profile = FoodProfile.query.filter_by(user_id=current_user.id).first()

    if not food_profile:
        return jsonify({'error': 'Profile not found'}), 404

    updated_dna = update_food_dna(reviews, food_profile.get_food_dna())
    food_profile.set_food_dna(updated_dna)
    db.session.commit()

    return jsonify({
        'message': 'Food DNA updated',
        'food_dna': updated_dna
    })