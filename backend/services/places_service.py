from backend.services.mock_data import (
    generate_mock_restaurants,
    generate_mock_restaurant_detail,
)

# ── Mock Places Service — no API calls, zero cost ──
# Same function signatures as the real version.
# Swap this file out later when ready to use real Google Places API.


def search_restaurants(query, city, latitude=None, longitude=None, budget_max=None):
    """
    Mock version — generates realistic fake restaurants
    instead of calling Google Places API.
    """

    # try to detect mood_id from query for biased results
    mood_id = None
    mood_keywords = {
        'comfort': 'comfort',
        'date': 'date_night',
        'celebrat': 'celebration',
        'late night': 'late_night',
        'family': 'family',
        'work': 'solo_work',
        'rain': 'rainy_day',
        'hangover': 'hangover',
        'healthy': 'healthy',
        'cheat': 'cheat_meal',
    }

    query_lower = query.lower()
    for keyword, mood in mood_keywords.items():
        if keyword in query_lower:
            mood_id = mood
            break

    restaurants = generate_mock_restaurants(
        mood_id=mood_id,
        city=city,
        count=9,
        budget_max=budget_max or 800
    )

    return restaurants


def get_restaurant_details(place_id):
    """
    Mock version — generates a single fake restaurant detail
    instead of calling Google Places API.
    """

    details = generate_mock_restaurant_detail(place_id)
    return details


def get_photo_url(photo_reference, max_width=800):
    """
    Mock version — not used since mock data already
    includes full photo URLs from Unsplash.
    """
    return photo_reference


def extract_cuisine(types):
    """
    Mock version — kept for compatibility, not used
    since mock data already includes cuisine_type directly.
    """
    return 'Restaurant'


def extract_city(address):
    """
    Mock version — kept for compatibility.
    """
    if not address:
        return ''
    parts = address.split(',')
    return parts[-2].strip() if len(parts) >= 2 else ''