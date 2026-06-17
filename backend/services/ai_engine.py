import anthropic
import json
from config import Config

client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)


def get_mood_recommendations(mood, user_prefs, context, city):
    prompt = f"""
You are ForkFind's AI food matchmaker. A user in {city} wants restaurant recommendations.

User Mood: {mood}

User Food Profile:
- Spice tolerance: {user_prefs.get('spice_tolerance', 5)}/10
- Diet type: {user_prefs.get('diet_type', 'non-veg')}
- Budget: ₹{user_prefs.get('budget_min', 200)} - ₹{user_prefs.get('budget_max', 800)} per person
- Preferred vibes: {', '.join(user_prefs.get('preferred_vibes', []))}
- Favourite cuisines: {', '.join(user_prefs.get('favourite_cuisines', []))}
- Food DNA: {json.dumps(user_prefs.get('food_dna', {}))}

Current Context:
- Weather: {context.get('weather', 'unknown')}
- Time of day: {context.get('time_of_day', 'unknown')}
- Day type: {context.get('day_type', 'weekday')}

Based on the mood, user profile and context, respond ONLY with a JSON object:
{{
    "message": "A warm, personal 1-2 sentence message about why these suggestions fit right now",
    "cuisines": ["cuisine1", "cuisine2", "cuisine3"],
    "vibes": ["vibe1", "vibe2"],
    "search_query": "best [cuisine] restaurant in {city} for [mood]"
}}

Be specific, personal and accurate. Match the mood perfectly.
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        text = response.content[0].text
        clean = text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception:
        return {
            "message": f"Perfect picks for your {mood} mood!",
            "cuisines": ["Indian", "Continental"],
            "vibes": ["cozy", "casual"],
            "search_query": f"{mood} restaurant in {city}"
        }


def solve_group_decision(preferences, city):
    prefs_text = json.dumps(preferences, indent=2)

    prompt = f"""
You are ForkFind's Group Decision Solver. A group of friends in {city} can't decide where to eat.

Here are everyone's preferences:
{prefs_text}

Find the best common ground for the entire group. Respond ONLY with a JSON object:
{{
    "message": "A fun, friendly 2 sentence explanation of how you found common ground",
    "common_cuisines": ["cuisine1", "cuisine2"],
    "budget_range": "₹X - ₹Y per person",
    "vibes": ["vibe1", "vibe2"],
    "dietary_notes": "any dietary restrictions to keep in mind",
    "search_query": "best restaurant in {city} for groups"
}}

Make sure dietary restrictions are respected. Find genuine overlap, not just a compromise.
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        text = response.content[0].text
        clean = text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception:
        return {
            "message": "Found some great options everyone will enjoy!",
            "common_cuisines": ["Indian", "Continental"],
            "budget_range": "₹300 - ₹600 per person",
            "vibes": ["casual", "family-friendly"],
            "dietary_notes": "vegetarian options available",
            "search_query": f"group restaurant in {city}"
        }


def analyze_review_sentiment(review_text):
    prompt = f"""
Analyze the sentiment of this restaurant review and respond with ONLY one word:
positive, neutral, or negative.

Review: {review_text}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )

    sentiment = response.content[0].text.strip().lower()
    if sentiment not in ['positive', 'neutral', 'negative']:
        return 'positive'
    return sentiment


def detect_restaurant_vibe(name, address, reviews_text):
    prompt = f"""
You are ForkFind's Vibe Detection AI.

Restaurant: {name}
Address: {address}
Sample reviews: {reviews_text[:500]}

Based on this information, identify the top 3 vibe tags for this restaurant.
Choose ONLY from these options:
romantic, luxury, cozy, family-friendly, loud, instagrammable, 
work-friendly, pet-friendly, rooftop, street-side, casual, fine-dining,
late-night, brunch-spot, hidden-gem

Respond ONLY with a JSON array:
["vibe1", "vibe2", "vibe3"]
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        text = response.content[0].text
        clean = text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception:
        return ['casual', 'cozy', 'family-friendly']