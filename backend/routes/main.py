from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from backend.models.food_profile import FoodProfile
from backend.models.restaurant import Restaurant
from backend.models.review import Review
from backend.models.challenge import UserChallenge
from backend.services.context_engine import get_current_context, get_context_recommendation, get_festival_suggestion
from backend.services.dna_engine import get_dna_insights

main = Blueprint('main', __name__)


@main.route('/')
def splash():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('splash.html')


@main.route('/home')
@login_required
def home():
    # get food profile
    food_profile = FoodProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    food_dna = food_profile.get_food_dna() if food_profile else {}

    # get context
    context = get_current_context(current_user.city)
    recommendations = get_context_recommendation(context)
    festival_suggestion = get_festival_suggestion(context.get('festival'))

    # get hidden gems
    gems = Restaurant.query.filter_by(
        city=current_user.city,
        is_hidden_gem=True
    ).order_by(Restaurant.gem_score.desc()).limit(3).all()

    # get stats
    review_count = Review.query.filter_by(
        user_id=current_user.id
    ).count()

    user_challenges = UserChallenge.query.filter_by(
        user_id=current_user.id
    ).all()

    badge_count = len([uc for uc in user_challenges if uc.completed])
    challenge_count = len([uc for uc in user_challenges if not uc.completed])

    return render_template('home.html',
                           food_profile=food_profile,
                           food_dna=food_dna,
                           context=context,
                           recommendations=recommendations,
                           festival_suggestion=festival_suggestion,
                           gems=gems,
                           review_count=review_count,
                           badge_count=badge_count,
                           challenge_count=challenge_count)


@main.route('/404')
def not_found():
    return render_template('404.html'), 404