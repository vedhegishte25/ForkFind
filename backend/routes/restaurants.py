from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend import db
from backend.models.restaurant import Restaurant
from backend.models.review import Review
from backend.services.places_service import get_restaurant_details
from backend.services.gem_scorer import calculate_gem_score

restaurants = Blueprint('restaurants', __name__)


@restaurants.route('/')
@login_required
def index():
    city = request.args.get('city', current_user.city)
    cuisine = request.args.get('cuisine', '')
    vibe = request.args.get('vibe', '')

    query = Restaurant.query.filter_by(city=city)

    if cuisine:
        query = query.filter(Restaurant.cuisine_type.ilike(f'%{cuisine}%'))

    results = query.order_by(Restaurant.average_rating.desc()).limit(20).all()

    return jsonify([r.to_dict() for r in results])


@restaurants.route('/<string:place_id>')
@login_required
def detail(place_id):
    # check cache first
    restaurant = Restaurant.query.filter_by(place_id=place_id).first()

    if not restaurant:
        # fetch from Google Places
        details = get_restaurant_details(place_id)
        if not details:
            return jsonify({'error': 'Restaurant not found'}), 404

        restaurant = Restaurant(
            place_id=place_id,
            name=details.get('name'),
            address=details.get('address'),
            city=details.get('city'),
            latitude=details.get('latitude'),
            longitude=details.get('longitude'),
            cuisine_type=details.get('cuisine_type'),
            price_level=details.get('price_level'),
            average_rating=details.get('rating'),
            total_reviews=details.get('total_reviews'),
            photo_url=details.get('photo_url'),
            google_maps_url=details.get('maps_url'),
        )
        restaurant.set_vibes(details.get('vibes', []))
        restaurant.gem_score = calculate_gem_score(details)
        restaurant.is_hidden_gem = restaurant.gem_score >= 7.0

        db.session.add(restaurant)
        db.session.commit()

    # get reviews for this restaurant
    reviews = Review.query.filter_by(restaurant_id=restaurant.id)\
                          .order_by(Review.created_at.desc())\
                          .limit(10).all()

    return render_template('restaurant_detail.html',
                           restaurant=restaurant,
                           reviews=[r.to_dict() for r in reviews])


@restaurants.route('/hidden-gems')
@login_required
def hidden_gems():
    city = request.args.get('city', current_user.city)

    gems = Restaurant.query.filter_by(city=city, is_hidden_gem=True)\
                           .order_by(Restaurant.gem_score.desc())\
                           .limit(15).all()

    return render_template('hidden_gems.html',
                           gems=[g.to_dict() for g in gems],
                           city=city)


@restaurants.route('/vibe/<string:vibe_tag>')
@login_required
def by_vibe(vibe_tag):
    city = request.args.get('city', current_user.city)

    all_restaurants = Restaurant.query.filter_by(city=city).all()
    filtered = [r for r in all_restaurants if vibe_tag in r.get_vibes()]

    return jsonify([r.to_dict() for r in filtered])