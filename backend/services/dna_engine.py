def update_food_dna(reviews, current_dna, latest_restaurant=None):
    """
    Updates user's Food DNA based on their review history.
    Food DNA is a percentage breakdown of cuisine preferences.
    Example: {"Indian": 40, "Italian": 25, "Asian": 15, "Street Food": 10, "Desserts": 10}
    """

    # cuisine category mapping
    cuisine_categories = {
        'indian': 'Indian',
        'north indian': 'Indian',
        'south indian': 'Indian',
        'mughlai': 'Indian',
        'punjabi': 'Indian',
        'gujarati': 'Indian',
        'maharashtrian': 'Indian',
        'italian': 'Italian',
        'pizza': 'Italian',
        'pasta': 'Italian',
        'chinese': 'Asian',
        'japanese': 'Asian',
        'thai': 'Asian',
        'korean': 'Asian',
        'asian': 'Asian',
        'sushi': 'Asian',
        'street food': 'Street Food',
        'chaat': 'Street Food',
        'vada pav': 'Street Food',
        'pav bhaji': 'Street Food',
        'fast food': 'Fast Food',
        'burger': 'Fast Food',
        'sandwich': 'Fast Food',
        'dessert': 'Desserts',
        'ice cream': 'Desserts',
        'cake': 'Desserts',
        'bakery': 'Desserts',
        'cafe': 'Cafe',
        'coffee': 'Cafe',
        'continental': 'Continental',
        'american': 'Continental',
        'mediterranean': 'Continental',
        'seafood': 'Seafood',
        'biryani': 'Indian',
        'kebab': 'Indian',
    }

    # count cuisine visits from reviews
    cuisine_counts = {}

    for review in reviews:
        if not review.restaurant:
            continue

        cuisine = review.restaurant.cuisine_type
        if not cuisine:
            continue

        cuisine_lower = cuisine.lower()

        # find matching category
        matched_category = None
        for key, category in cuisine_categories.items():
            if key in cuisine_lower:
                matched_category = category
                break

        if not matched_category:
            matched_category = 'Other'

        # liked reviews count more
        weight = 2 if review.liked else 1
        cuisine_counts[matched_category] = cuisine_counts.get(
            matched_category, 0
        ) + weight

    # add latest restaurant if provided
    if latest_restaurant and latest_restaurant.cuisine_type:
        cuisine_lower = latest_restaurant.cuisine_type.lower()
        matched_category = 'Other'

        for key, category in cuisine_categories.items():
            if key in cuisine_lower:
                matched_category = category
                break

        cuisine_counts[matched_category] = cuisine_counts.get(
            matched_category, 0
        ) + 1

    # if no reviews yet return current dna
    if not cuisine_counts:
        return current_dna

    # convert counts to percentages
    total = sum(cuisine_counts.values())
    new_dna = {}

    for cuisine, count in cuisine_counts.items():
        percentage = round((count / total) * 100)
        if percentage > 0:
            new_dna[cuisine] = percentage

    # make sure percentages add up to 100
    total_pct = sum(new_dna.values())
    if total_pct != 100 and new_dna:
        largest = max(new_dna, key=new_dna.get)
        new_dna[largest] += 100 - total_pct

    # blend with existing dna (70% new, 30% old) for smooth evolution
    if current_dna:
        blended_dna = {}
        all_cuisines = set(list(new_dna.keys()) + list(current_dna.keys()))

        for cuisine in all_cuisines:
            new_val = new_dna.get(cuisine, 0)
            old_val = current_dna.get(cuisine, 0)
            blended = round((new_val * 0.7) + (old_val * 0.3))
            if blended > 0:
                blended_dna[cuisine] = blended

        # normalize blended to 100
        total_blended = sum(blended_dna.values())
        if total_blended != 100 and blended_dna:
            largest = max(blended_dna, key=blended_dna.get)
            blended_dna[largest] += 100 - total_blended

        return blended_dna

    return new_dna


def get_dna_insights(food_dna):
    """
    Returns human readable insights about a user's food DNA.
    """
    if not food_dna:
        return []

    insights = []
    sorted_dna = sorted(food_dna.items(), key=lambda x: x[1], reverse=True)

    # top cuisine
    if sorted_dna:
        top_cuisine, top_pct = sorted_dna[0]
        insights.append(f"You are a {top_cuisine} food lover at heart ({top_pct}%)")

    # diversity score
    diversity = len([v for v in food_dna.values() if v >= 10])
    if diversity >= 4:
        insights.append("You have an adventurous and diverse palate")
    elif diversity >= 2:
        insights.append("You enjoy a good mix of cuisines")
    else:
        insights.append("You know exactly what you love and stick to it")

    # street food lover
    if food_dna.get('Street Food', 0) >= 20:
        insights.append("You are a true street food enthusiast")

    # dessert lover
    if food_dna.get('Desserts', 0) >= 15:
        insights.append("You never say no to dessert")

    return insights
def compare_food_dna(dna_a, dna_b):
    """
    Compares two Food DNA profiles and returns an overlap score (0-100)
    plus a breakdown of shared and unique cuisines.
    """
    if not dna_a or not dna_b:
        return {
            'overlap_score': 0,
            'shared_cuisines': [],
            'unique_to_a': list(dna_a.keys()) if dna_a else [],
            'unique_to_b': list(dna_b.keys()) if dna_b else []
        }

    all_cuisines = set(list(dna_a.keys()) + list(dna_b.keys()))

    overlap_sum = 0
    shared_cuisines = []

    for cuisine in all_cuisines:
        val_a = dna_a.get(cuisine, 0)
        val_b = dna_b.get(cuisine, 0)
        overlap_sum += min(val_a, val_b)

        if val_a > 0 and val_b > 0:
            shared_cuisines.append({
                'cuisine': cuisine,
                'a_pct': val_a,
                'b_pct': val_b
            })

    shared_cuisines.sort(key=lambda x: min(x['a_pct'], x['b_pct']), reverse=True)

    unique_to_a = [c for c in dna_a.keys() if dna_b.get(c, 0) == 0]
    unique_to_b = [c for c in dna_b.keys() if dna_a.get(c, 0) == 0]

    return {
        'overlap_score': round(overlap_sum),
        'shared_cuisines': shared_cuisines,
        'unique_to_a': unique_to_a,
        'unique_to_b': unique_to_b
    }


def get_match_message(overlap_score):
    if overlap_score >= 80:
        return "You two basically share a stomach. Incredible match!"
    elif overlap_score >= 60:
        return "Strong food compatibility — you'd agree on most places."
    elif overlap_score >= 40:
        return "Decent overlap — some negotiation needed, but workable."
    elif overlap_score >= 20:
        return "Pretty different tastes — could be fun to explore together."
    else:
        return "Total opposites! You might just discover something new."