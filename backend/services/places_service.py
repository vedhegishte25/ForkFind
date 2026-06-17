import requests
from config import Config

PLACES_API_KEY = Config.GOOGLE_PLACES_API_KEY
PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"


def search_restaurants(query, city, latitude=None, longitude=None, budget_max=None):
    try:
        # build search query
        search_query = f"{query} restaurant in {city}"

        params = {
            'query': search_query,
            'key': PLACES_API_KEY,
            'type': 'restaurant',
            'language': 'en'
        }

        # use location bias if coordinates provided
        if latitude and longitude:
            params['location'] = f"{latitude},{longitude}"
            params['radius'] = 5000

        response = requests.get(
            f"{PLACES_BASE_URL}/textsearch/json",
            params=params
        )

        data = response.json()

        if data.get('status') != 'OK':
            return []

        restaurants = []
        for place in data.get('results', [])[:10]:
            restaurant = {
                'place_id': place.get('place_id'),
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'rating': place.get('rating', 0),
                'total_ratings': place.get('user_ratings_total', 0),
                'price_level': place.get('price_level', 2),
                'photo_url': get_photo_url(
                    place.get('photos', [{}])[0].get('photo_reference')
                ) if place.get('photos') else None,
                'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
                'longitude': place.get('geometry', {}).get('location', {}).get('lng'),
                'open_now': place.get('opening_hours', {}).get('open_now', None),
                'types': place.get('types', [])
            }
            restaurants.append(restaurant)

        return restaurants

    except Exception as e:
        print(f"Places search error: {e}")
        return []


def get_restaurant_details(place_id):
    try:
        params = {
            'place_id': place_id,
            'key': PLACES_API_KEY,
            'fields': (
                'name,formatted_address,geometry,rating,'
                'user_ratings_total,price_level,photos,'
                'opening_hours,website,formatted_phone_number,'
                'reviews,types,url'
            )
        }

        response = requests.get(
            f"{PLACES_BASE_URL}/details/json",
            params=params
        )

        data = response.json()

        if data.get('status') != 'OK':
            return None

        place = data.get('result', {})

        # extract cuisine type from types
        cuisine_type = extract_cuisine(place.get('types', []))

        # get photo url
        photo_url = None
        if place.get('photos'):
            photo_url = get_photo_url(place['photos'][0].get('photo_reference'))

        # extract city from address
        address = place.get('formatted_address', '')
        city = extract_city(address)

        # get review texts for vibe detection
        reviews = place.get('reviews', [])
        reviews_text = ' '.join([r.get('text', '') for r in reviews[:3]])

        return {
            'name': place.get('name'),
            'address': address,
            'city': city,
            'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
            'longitude': place.get('geometry', {}).get('location', {}).get('lng'),
            'rating': place.get('rating', 0),
            'total_reviews': place.get('user_ratings_total', 0),
            'price_level': place.get('price_level', 2),
            'photo_url': photo_url,
            'maps_url': place.get('url'),
            'website': place.get('website'),
            'phone': place.get('formatted_phone_number'),
            'cuisine_type': cuisine_type,
            'opening_hours': place.get('opening_hours', {}).get('weekday_text', []),
            'reviews_text': reviews_text,
            'vibes': []
        }

    except Exception as e:
        print(f"Places details error: {e}")
        return None


def get_photo_url(photo_reference, max_width=800):
    if not photo_reference:
        return None
    return (
        f"{PLACES_BASE_URL}/photo"
        f"?maxwidth={max_width}"
        f"&photo_reference={photo_reference}"
        f"&key={PLACES_API_KEY}"
    )


def extract_cuisine(types):
    cuisine_map = {
        'indian_restaurant': 'Indian',
        'chinese_restaurant': 'Chinese',
        'italian_restaurant': 'Italian',
        'japanese_restaurant': 'Japanese',
        'mexican_restaurant': 'Mexican',
        'thai_restaurant': 'Thai',
        'mediterranean_restaurant': 'Mediterranean',
        'american_restaurant': 'American',
        'bakery': 'Bakery',
        'cafe': 'Cafe',
        'bar': 'Bar',
        'fast_food_restaurant': 'Fast Food',
        'pizza_restaurant': 'Pizza',
        'seafood_restaurant': 'Seafood',
        'steak_house': 'Steakhouse',
        'vegetarian_restaurant': 'Vegetarian',
    }

    for t in types:
        if t in cuisine_map:
            return cuisine_map[t]

    return 'Restaurant'


def extract_city(address):
    if not address:
        return ''
    parts = address.split(',')
    if len(parts) >= 2:
        return parts[-3].strip() if len(parts) >= 3 else parts[-2].strip()
    return ''