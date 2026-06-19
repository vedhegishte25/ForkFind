import random

# ── Mock restaurant database — Thane based, realistic but fake ──

CUISINES = [
    'Indian', 'Chinese', 'Italian', 'Continental', 'Japanese',
    'Thai', 'Street Food', 'Fast Food', 'Seafood', 'Desserts',
    'Cafe', 'Mexican', 'Mughlai', 'South Indian'
]

VIBE_POOL = [
    'cozy', 'rooftop', 'romantic', 'family-friendly', 'casual',
    'late-night', 'work-friendly', 'instagrammable', 'luxury',
    'pet-friendly', 'street-side', 'fine-dining', 'brunch-spot',
    'loud', 'quiet'
]

NAME_PREFIXES = [
    'The', 'Spice', 'Royal', 'Urban', 'Green', 'Cafe', 'Bombay',
    'Tandoor', 'Bay', 'Garden', 'Old Town', 'Curry', 'Fresh',
    'Hidden', 'Coastal', 'Wood Fired', 'Roof Top', 'Local'
]

NAME_SUFFIXES = [
    'Kitchen', 'House', 'Bistro', 'Junction', 'Corner', 'Diner',
    'Cafe', 'Grill', 'Tavern', 'Eatery', 'Hub', 'Plate',
    'Table', 'Bowl', 'Spoon', 'Garden', 'Terrace', 'Express'
]

PHOTO_POOL = [
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600',
    'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600',
    'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600',
    'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600',
    'https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=600',
    'https://images.unsplash.com/photo-1517022812141-23620dba5c23?w=600',
    'https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=600',
    'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=600',
    'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=600',
    'https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=600',
]

AREAS_THANE = [
    'Ghodbunder Road', 'Vartak Nagar', 'Naupada', 'Panchpakhadi',
    'Vasant Vihar', 'Hiranandani Estate', 'Kasarvadavali', 'Manpada',
    'Brahmand', 'Pokhran Road', 'Wagle Estate', 'Kapurbawdi'
]

MOOD_TO_CUISINE = {
    'comfort': ['Indian', 'Mughlai', 'South Indian'],
    'date_night': ['Italian', 'Continental', 'Japanese'],
    'celebration': ['Continental', 'Mughlai', 'Italian'],
    'late_night': ['Street Food', 'Fast Food', 'Chinese'],
    'family': ['Indian', 'Chinese', 'Continental'],
    'solo_work': ['Cafe', 'Continental'],
    'rainy_day': ['Indian', 'Cafe', 'South Indian'],
    'hangover': ['Fast Food', 'Indian', 'Street Food'],
    'healthy': ['Continental', 'Cafe', 'South Indian'],
    'cheat_meal': ['Fast Food', 'Italian', 'Street Food'],
}

MOOD_TO_VIBE = {
    'comfort': ['cozy', 'casual', 'family-friendly'],
    'date_night': ['romantic', 'rooftop', 'fine-dining'],
    'celebration': ['loud', 'instagrammable', 'luxury'],
    'late_night': ['late-night', 'casual', 'street-side'],
    'family': ['family-friendly', 'casual', 'quiet'],
    'solo_work': ['work-friendly', 'quiet', 'cafe'],
    'rainy_day': ['cozy', 'quiet', 'casual'],
    'hangover': ['casual', 'late-night', 'street-side'],
    'healthy': ['quiet', 'instagrammable', 'casual'],
    'cheat_meal': ['loud', 'casual', 'instagrammable'],
}


def generate_mock_restaurants(mood_id=None, city='Thane', count=9, budget_max=800):
    """
    Generates a list of realistic fake restaurants.
    If mood_id is given, biases cuisine and vibe selection to match the mood.
    """
    restaurants = []

    cuisines_pool = MOOD_TO_CUISINE.get(mood_id, CUISINES)
    vibes_pool = MOOD_TO_VIBE.get(mood_id, VIBE_POOL)

    for i in range(count):
        name = f"{random.choice(NAME_PREFIXES)} {random.choice(NAME_SUFFIXES)}"
        cuisine = random.choice(cuisines_pool)
        area = random.choice(AREAS_THANE)
        rating = round(random.uniform(3.6, 4.9), 1)
        total_reviews = random.randint(15, 850)
        price_level = random.randint(1, 4)

        # bias price to budget
        if budget_max and budget_max <= 400:
            price_level = random.choice([1, 1, 2])
        elif budget_max and budget_max <= 800:
            price_level = random.choice([2, 2, 3])
        else:
            price_level = random.choice([3, 4])

        vibes = random.sample(vibes_pool, k=min(3, len(vibes_pool)))

        place_id = f"mock_{city.lower()}_{i}_{random.randint(1000,9999)}"

        restaurant = {
            'place_id': place_id,
            'name': name,
            'address': f"{area}, {city}, Maharashtra",
            'rating': rating,
            'total_ratings': total_reviews,
            'price_level': price_level,
            'photo_url': random.choice(PHOTO_POOL),
            'latitude': 19.2183 + random.uniform(-0.05, 0.05),
            'longitude': 72.9781 + random.uniform(-0.05, 0.05),
            'open_now': random.choice([True, True, True, False]),
            'types': [cuisine.lower().replace(' ', '_') + '_restaurant'],
            'cuisine_type': cuisine,
            'vibe_tags': vibes,
        }
        restaurants.append(restaurant)

    return restaurants


def generate_mock_restaurant_detail(place_id, city='Thane'):
    """
    Generates a single detailed mock restaurant for the detail page.
    """
    name = f"{random.choice(NAME_PREFIXES)} {random.choice(NAME_SUFFIXES)}"
    cuisine = random.choice(CUISINES)
    area = random.choice(AREAS_THANE)
    rating = round(random.uniform(3.8, 4.9), 1)
    total_reviews = random.randint(40, 600)

    return {
        'name': name,
        'address': f"{area}, {city}, Maharashtra",
        'city': city,
        'latitude': 19.2183 + random.uniform(-0.05, 0.05),
        'longitude': 72.9781 + random.uniform(-0.05, 0.05),
        'rating': rating,
        'total_reviews': total_reviews,
        'price_level': random.randint(1, 4),
        'photo_url': random.choice(PHOTO_POOL),
        'maps_url': f"https://maps.google.com/?q={name.replace(' ', '+')}+{city}",
        'website': None,
        'phone': f"+91 98{random.randint(10000000,99999999)}",
        'cuisine_type': cuisine,
        'opening_hours': [
            'Monday: 11:00 AM – 11:00 PM',
            'Tuesday: 11:00 AM – 11:00 PM',
            'Wednesday: 11:00 AM – 11:00 PM',
            'Thursday: 11:00 AM – 11:00 PM',
            'Friday: 11:00 AM – 12:00 AM',
            'Saturday: 11:00 AM – 12:00 AM',
            'Sunday: 11:00 AM – 11:00 PM',
        ],
        'reviews_text': 'Great food and friendly service. Highly recommended for groups.',
        'vibes': random.sample(VIBE_POOL, k=3)
    }


def generate_mock_hidden_gems(city='Thane', count=12):
    """
    Generates mock restaurants pre-classified as hidden gems.
    """
    gems = []
    gem_types = ['undiscovered', 'local_favourite', 'rare_find',
                 'rising_star', 'neighbourhood_gem']
    gem_badges = {
        'undiscovered': '🔍 Undiscovered',
        'local_favourite': '❤️ Local Favourite',
        'rare_find': '💎 Rare Find',
        'rising_star': '⭐ Rising Star',
        'neighbourhood_gem': '🏘️ Neighbourhood Gem'
    }

    for i in range(count):
        name = f"{random.choice(NAME_PREFIXES)} {random.choice(NAME_SUFFIXES)}"
        cuisine = random.choice(CUISINES)
        area = random.choice(AREAS_THANE)
        rating = round(random.uniform(4.1, 4.9), 1)
        total_reviews = random.randint(8, 280)
        gem_type = random.choice(gem_types)

        gems.append({
            'place_id': f"mock_gem_{city.lower()}_{i}_{random.randint(1000,9999)}",
            'name': name,
            'address': f"{area}, {city}",
            'cuisine_type': cuisine,
            'average_rating': rating,
            'total_reviews': total_reviews,
            'price_level': random.randint(1, 3),
            'photo_url': random.choice(PHOTO_POOL),
            'gem_score': round(random.uniform(6.5, 9.8), 1),
            'gem_type': gem_type,
            'gem_badge': gem_badges[gem_type],
            'vibe_tags': random.sample(VIBE_POOL, k=3),
        })

    return gems