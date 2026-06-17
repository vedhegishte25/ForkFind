def calculate_gem_score(restaurant_data):
    """
    Calculates a hidden gem score (0-10) for a restaurant.
    High score = high quality but low popularity = hidden gem.

    Factors:
    - High rating but low number of reviews = undiscovered gem
    - Newer restaurants with good ratings
    - Not a chain or franchise
    """

    score = 0.0

    rating = restaurant_data.get('rating', 0)
    total_reviews = restaurant_data.get('total_reviews', 0)
    price_level = restaurant_data.get('price_level', 2)
    name = restaurant_data.get('name', '').lower()

    # factor 1 — rating score (0-4 points)
    # good rating is the foundation of a hidden gem
    if rating >= 4.5:
        score += 4.0
    elif rating >= 4.0:
        score += 3.0
    elif rating >= 3.5:
        score += 2.0
    elif rating >= 3.0:
        score += 1.0

    # factor 2 — low review count = undiscovered (0-3 points)
    # sweet spot is good rating with very few reviews
    if 5 <= total_reviews <= 50:
        score += 3.0
    elif 51 <= total_reviews <= 150:
        score += 2.0
    elif 151 <= total_reviews <= 300:
        score += 1.0
    elif total_reviews < 5:
        score += 1.5  # brand new, worth a look

    # factor 3 — not a known chain (0-2 points)
    known_chains = [
        'mcdonalds', 'kfc', 'subway', 'dominos', 'pizza hut',
        'burger king', 'starbucks', 'cafe coffee day', 'ccd',
        'haldirams', 'barbeque nation', 'mainland china',
        'faasos', 'behrouz', 'box8', 'wow momo'
    ]

    is_chain = any(chain in name for chain in known_chains)
    if not is_chain:
        score += 2.0

    # factor 4 — price accessibility bonus (0-1 point)
    # hidden gems are usually affordable
    if price_level in [1, 2]:
        score += 1.0
    elif price_level == 3:
        score += 0.5

    # cap score at 10
    score = min(score, 10.0)

    return round(score, 1)


def classify_gem_type(restaurant_data):
    """
    Classifies what kind of hidden gem a restaurant is.
    """
    rating = restaurant_data.get('rating', 0)
    total_reviews = restaurant_data.get('total_reviews', 0)
    gem_score = restaurant_data.get('gem_score', 0)

    if total_reviews < 50 and rating >= 4.0:
        return 'undiscovered'       # barely anyone knows about it

    elif total_reviews < 150 and rating >= 4.5:
        return 'local_favourite'    # locals love it, tourists dont know

    elif gem_score >= 8.0:
        return 'rare_find'          # exceptional in every way

    elif total_reviews < 300 and rating >= 4.0:
        return 'rising_star'        # gaining traction slowly

    else:
        return 'neighbourhood_gem'  # solid local spot


def get_gem_badge(gem_type):
    """
    Returns emoji badge for gem type.
    """
    badges = {
        'undiscovered': '🔍 Undiscovered',
        'local_favourite': '❤️ Local Favourite',
        'rare_find': '💎 Rare Find',
        'rising_star': '⭐ Rising Star',
        'neighbourhood_gem': '🏘️ Neighbourhood Gem'
    }

    return badges.get(gem_type, '✨ Hidden Gem')