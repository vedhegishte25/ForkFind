import random
from backend.services.mock_data import MOOD_TO_CUISINE, MOOD_TO_VIBE

# ── Mock AI Engine — no API calls, zero cost ──
# Same function signatures as the real version.
# Swap this file out later when ready to use real Anthropic API.

MOOD_MESSAGES = {
    'comfort': [
        "Sounds like you need something warm and familiar today.",
        "Comfort food coming right up — these spots feel like home."
    ],
    'date_night': [
        "Setting the mood with some romantic picks for tonight.",
        "These spots have the perfect ambience for date night."
    ],
    'celebration': [
        "Time to celebrate! Here are some places worth the occasion.",
        "Big moments deserve big flavours — check these out."
    ],
    'late_night': [
        "Late night cravings hit different. Here's what's open.",
        "Found some solid late night spots still serving."
    ],
    'family': [
        "Family friendly spots with something for everyone.",
        "Spacious, welcoming places perfect for the whole family."
    ],
    'solo_work': [
        "Quiet corners with good wifi and better coffee.",
        "Perfect spots to get work done with a great cup of coffee."
    ],
    'rainy_day': [
        "Rainy day calls for something warm and cozy.",
        "Perfect weather for soup, chai and comfort."
    ],
    'hangover': [
        "We've got you. Heavy, greasy and exactly what you need.",
        "Recovery mode activated — these will fix you right up."
    ],
    'healthy': [
        "Fresh, light and nutritious options for a clean day.",
        "Healthy doesn't mean boring — check these out."
    ],
    'cheat_meal': [
        "No regrets today. Full send, here we go.",
        "Cheat day rules apply — these are worth every bite."
    ],
}


def get_mood_recommendations(mood, user_prefs, context, city):
    """
    Mock version — generates realistic looking recommendations
    using rule based logic instead of calling Claude API.
    """

    # find mood_id from mood label
    mood_id = None
    for key in MOOD_TO_CUISINE.keys():
        if key.replace('_', ' ') in mood.lower() or key in mood.lower():
            mood_id = key
            break

    if not mood_id:
        mood_id = 'comfort'

    cuisines = MOOD_TO_CUISINE.get(mood_id, ['Indian', 'Continental'])
    vibes = MOOD_TO_VIBE.get(mood_id, ['casual', 'cozy'])

    messages = MOOD_MESSAGES.get(mood_id, ["Here are some great picks for you."])
    message = random.choice(messages)

    # personalize message slightly using user prefs
    if user_prefs.get('diet_type') == 'veg':
        message += " All filtered for vegetarian options."
    elif user_prefs.get('diet_type') == 'vegan':
        message += " Vegan friendly spots included."

    if context.get('weather') == 'rainy' and mood_id != 'rainy_day':
        message += " Also factored in the rain outside."

    return {
        "message": message,
        "cuisines": cuisines[:3],
        "vibes": vibes[:2],
        "search_query": f"{mood} restaurant in {city}",
        "mood_id": mood_id
    }


def solve_group_decision(preferences, city):
    """
    Mock version — finds overlap in group preferences using
    simple rule based logic instead of calling Claude API.
    """

    all_cuisines = []
    all_vibes = []
    all_budgets = []
    all_dietary = []

    for user_id, prefs in preferences.items():
        all_cuisines.extend(prefs.get('cuisines', []))
        all_vibes.extend(prefs.get('vibes', []))
        all_budgets.append(prefs.get('budget', 500))
        all_dietary.append(prefs.get('dietary', 'non-veg'))

    # find most common cuisines
    cuisine_counts = {}
    for c in all_cuisines:
        cuisine_counts[c] = cuisine_counts.get(c, 0) + 1
    common_cuisines = sorted(
        cuisine_counts, key=cuisine_counts.get, reverse=True
    )[:3]

    if not common_cuisines:
        common_cuisines = ['Indian', 'Continental']

    # find most common vibes
    vibe_counts = {}
    for v in all_vibes:
        vibe_counts[v] = vibe_counts.get(v, 0) + 1
    common_vibes = sorted(
        vibe_counts, key=vibe_counts.get, reverse=True
    )[:2]

    if not common_vibes:
        common_vibes = ['casual', 'family-friendly']

    # budget range covering everyone
    min_budget = min(all_budgets) if all_budgets else 300
    max_budget = max(all_budgets) if all_budgets else 800
    budget_range = f"₹{min_budget}–₹{max_budget} per person"

    # dietary notes
    dietary_notes = "Mixed dietary preferences — vegetarian options recommended"
    if all(d == 'veg' for d in all_dietary):
        dietary_notes = "Everyone prefers vegetarian"
    elif all(d == 'non-veg' for d in all_dietary):
        dietary_notes = "Everyone is okay with non-vegetarian"
    elif 'vegan' in all_dietary:
        dietary_notes = "Vegan options needed — choose accordingly"

    messages = [
        f"Found great overlap! Everyone seems to enjoy {common_cuisines[0]} food.",
        f"Based on everyone's picks, {common_cuisines[0]} feels like a safe win for the group.",
        "Balanced things out so nobody has to compromise too much."
    ]

    return {
        "message": random.choice(messages),
        "common_cuisines": common_cuisines,
        "budget_range": budget_range,
        "vibes": common_vibes,
        "dietary_notes": dietary_notes,
        "search_query": f"{common_cuisines[0]} restaurant in {city}"
    }


def analyze_review_sentiment(review_text):
    """
    Mock version — simple keyword based sentiment instead
    of calling Claude API.
    """

    text = review_text.lower()

    positive_words = [
        'great', 'amazing', 'love', 'excellent', 'awesome',
        'delicious', 'best', 'good', 'fantastic', 'perfect',
        'wonderful', 'tasty', 'recommend', 'friendly'
    ]
    negative_words = [
        'bad', 'terrible', 'worst', 'awful', 'poor', 'slow',
        'rude', 'disappointing', 'cold', 'overpriced', 'dirty'
    ]

    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)

    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'


def detect_restaurant_vibe(name, address, reviews_text):
    """
    Mock version — picks plausible vibe tags randomly
    instead of calling Claude API.
    """

    all_vibes = [
        'romantic', 'luxury', 'cozy', 'family-friendly', 'loud',
        'instagrammable', 'work-friendly', 'pet-friendly', 'rooftop',
        'street-side', 'casual', 'fine-dining', 'late-night',
        'brunch-spot', 'hidden-gem'
    ]

    return random.sample(all_vibes, k=3)