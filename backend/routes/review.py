from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from backend import db
from backend.models.review import Review
from backend.models.restaurant import Restaurant
from backend.services.ai_engine import analyze_review_sentiment
from backend.services.dna_engine import update_food_dna
from backend.models.food_profile import FoodProfile

reviews = Blueprint('reviews', __name__)


@reviews.route('/<int:restaurant_id>', methods=['GET'])
@login_required
def get_reviews(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    all_reviews = Review.query.filter_by(restaurant_id=restaurant_id)\
                              .order_by(Review.created_at.desc())\
                              .all()

    return jsonify({
        'restaurant': restaurant.to_dict(),
        'reviews': [r.to_dict() for r in all_reviews],
        'total': len(all_reviews),
        'average_rating': round(
            sum(r.rating for r in all_reviews) / len(all_reviews), 1
        ) if all_reviews else 0
    })


@reviews.route('/submit', methods=['POST'])
@login_required
def submit_review():
    data = request.get_json()

    restaurant_id = data.get('restaurant_id')
    rating = data.get('rating')
    written_review = data.get('written_review', '')
    mood_tag = data.get('mood_tag', '')
    occasion_tag = data.get('occasion_tag', '')
    photo_url = data.get('photo_url', '')

    if not restaurant_id or not rating:
        return jsonify({'error': 'Restaurant and rating are required'}), 400

    # check if user already reviewed this restaurant
    existing = Review.query.filter_by(
        user_id=current_user.id,
        restaurant_id=restaurant_id
    ).first()

    if existing:
        return jsonify({'error': 'You have already reviewed this restaurant'}), 400

    # analyze sentiment with AI
    sentiment = 'positive'
    if written_review:
        sentiment = analyze_review_sentiment(written_review)

    new_review = Review(
        user_id=current_user.id,
        restaurant_id=restaurant_id,
        rating=rating,
        written_review=written_review,
        mood_tag=mood_tag,
        occasion_tag=occasion_tag,
        photo_url=photo_url,
        sentiment=sentiment,
        liked=rating >= 4
    )

    db.session.add(new_review)

    # update restaurant average rating
    restaurant = Restaurant.query.get(restaurant_id)
    if restaurant:
        all_reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
        total_ratings = sum(r.rating for r in all_reviews) + rating
        restaurant.average_rating = round(total_ratings / (len(all_reviews) + 1), 1)
        restaurant.total_reviews = len(all_reviews) + 1

    # update user food DNA based on this visit
    food_profile = FoodProfile.query.filter_by(user_id=current_user.id).first()
    if food_profile and restaurant:
        current_dna = food_profile.get_food_dna()
        all_user_reviews = Review.query.filter_by(user_id=current_user.id).all()
        updated_dna = update_food_dna(all_user_reviews, current_dna, restaurant)
        food_profile.set_food_dna(updated_dna)

    db.session.commit()

    return jsonify({
        'message': 'Review submitted successfully',
        'sentiment': sentiment,
        'review': new_review.to_dict()
    })


@reviews.route('/delete/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(review)
    db.session.commit()

    return jsonify({'message': 'Review deleted successfully'})


@reviews.route('/my-reviews')
@login_required
def my_reviews():
    all_reviews = Review.query.filter_by(user_id=current_user.id)\
                              .order_by(Review.created_at.desc())\
                              .all()

    return jsonify({
        'reviews': [r.to_dict() for r in all_reviews],
        'total': len(all_reviews)
    })