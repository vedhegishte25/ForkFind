from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend.models.food_profile import FoodProfile
from backend.services.ai_engine import get_mood_recommendations
from backend.services.context_engine import get_current_context, get_festival_suggestion
from backend.services.places_service import search_restaurants

discover = Blueprint('discover', __name__)

MOODS = [
    {"id": "comfort", "label": "Comfort Food", "emoji": "🍲", "description": "Warm, hearty, feels like home"},
    {"id": "date_night", "label": "Date Night", "emoji": "🕯️", "description": "Romantic, intimate, special"},
    {"id": "celebration", "label": "Celebration", "emoji": "🎉", "description": "Party vibes, big occasion"},
    {"id": "late_night", "label": "Late Night Cravings", "emoji": "🌙", "description": "Open late, satisfying"},
    {"id": "family", "label": "Family Dinner", "emoji": "👨‍👩‍👧", "description": "Kid friendly, spacious"},
    {"id": "solo_work", "label": "Solo Work Session", "emoji": "💻", "description": "Quiet, wifi, good coffee"},
    {"id": "rainy_day", "label": "Rainy Day Food", "emoji": "🌧️", "description": "Soup, chai, cozy corners"},
    {"id": "hangover", "label": "Hangover Cure", "emoji": "🥴", "description": "Heavy, greasy, restorative"},
    {"id": "healthy", "label": "Healthy Eating", "emoji": "🥗", "description": "Fresh, light, nutritious"},
    {"id": "cheat_meal", "label": "Cheat Meal Day", "emoji": "🍔", "description": "No regrets, full send"},
]


@discover.route('/')
@login_required
def index():
    context = get_current_context(current_user.city)
    return render_template('discover.html',
                           moods=MOODS,
                           context=context)


@discover.route('/mood', methods=['POST'])
@login_required
def mood_recommend():
    data = request.get_json()
    mood_id = data.get('mood_id')
    mood_label = data.get('mood_label')
    city = data.get('city', current_user.city)
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # get user food profile
    food_profile = FoodProfile.query.filter_by(user_id=current_user.id).first()

    # get current context
    context = get_current_context(city)

    # boost with festival cuisines if a festival is active
    festival_suggestion = get_festival_suggestion(context.get('festival'))


    # build user preferences dict
    user_prefs = {}
    if food_profile:
        user_prefs = {
            'spice_tolerance': food_profile.spice_tolerance,
            'diet_type': food_profile.diet_type,
            'budget_min': food_profile.budget_min,
            'budget_max': food_profile.budget_max,
            'preferred_vibes': food_profile.get_vibes(),
            'favourite_cuisines': food_profile.get_cuisines(),
            'food_dna': food_profile.get_food_dna()
        }

    # ask AI for recommendations
    ai_suggestions = get_mood_recommendations(
        mood=mood_label,
        user_prefs=user_prefs,
        context=context,
        city=city
    )
    # blend in festival cuisines if active
    if festival_suggestion:
        existing_cuisines = ai_suggestions.get('cuisines', [])
        for c in festival_suggestion['cuisines']:
            if c not in existing_cuisines:
                existing_cuisines.insert(0, c)
        ai_suggestions['cuisines'] = existing_cuisines[:3]
        ai_suggestions['message'] = f"{festival_suggestion['icon']} {festival_suggestion['message']}. " + ai_suggestions.get('message', '')

    # search real restaurants from Google Places
    restaurants = search_restaurants(
        query=ai_suggestions.get('search_query', mood_label),
        city=city,
        latitude=latitude,
        longitude=longitude,
        budget_max=user_prefs.get('budget_max', 800)
    )

    return jsonify({
        'mood': mood_label,
        'ai_message': ai_suggestions.get('message', ''),
        'cuisine_suggestions': ai_suggestions.get('cuisines', []),
        'vibe_suggestions': ai_suggestions.get('vibes', []),
        'restaurants': restaurants,
        'context': context
    })