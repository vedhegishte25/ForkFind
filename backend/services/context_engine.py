import requests
from datetime import datetime


WEATHER_API_URL = "https://wttr.in"


def get_current_context(city):
    now = datetime.now()

    return {
        'weather': get_weather(city),
        'time_of_day': get_time_of_day(now),
        'day_type': get_day_type(now),
        'season': get_season(now),
        'festival': get_festival(now),
        'hour': now.hour
    }


def get_weather(city):
    try:
        if not city:
            return 'clear'

        response = requests.get(
            f"{WEATHER_API_URL}/{city}?format=%C",
            timeout=3
        )

        if response.status_code == 200:
            weather = response.text.strip().lower()
            return classify_weather(weather)

        return 'clear'

    except Exception:
        return 'clear'


def classify_weather(weather_text):
    if any(w in weather_text for w in ['rain', 'drizzle', 'shower']):
        return 'rainy'
    elif any(w in weather_text for w in ['cloud', 'overcast', 'fog', 'mist']):
        return 'cloudy'
    elif any(w in weather_text for w in ['sun', 'clear', 'bright']):
        return 'sunny'
    elif any(w in weather_text for w in ['thunder', 'storm']):
        return 'stormy'
    elif any(w in weather_text for w in ['snow', 'sleet', 'hail']):
        return 'cold'
    else:
        return 'clear'


def get_time_of_day(now):
    hour = now.hour

    if 5 <= hour < 9:
        return 'early_morning'
    elif 9 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 15:
        return 'lunch'
    elif 15 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 21:
        return 'dinner'
    elif 21 <= hour < 24:
        return 'late_night'
    else:
        return 'midnight'


def get_day_type(now):
    day = now.weekday()

    if day == 6:
        return 'sunday'
    elif day == 5:
        return 'saturday'
    elif day == 4:
        return 'friday'
    else:
        return 'weekday'


def get_season(now):
    month = now.month

    if month in [3, 4, 5]:
        return 'summer'
    elif month in [6, 7, 8, 9]:
        return 'monsoon'
    elif month in [10, 11]:
        return 'autumn'
    else:
        return 'winter'


def get_festival(now):
    month = now.month
    day = now.day

def get_festival(now):
    month = now.month
    day = now.day

    festivals = {
        (1, 1): 'New Year',
        (1, 14): 'Makar Sankranti',
        (3, 25): 'Holi',
        (8, 15): 'Independence Day',
        (8, 19): 'Raksha Bandhan',
        (9, 7): 'Ganesh Chaturthi',
        (10, 2): 'Gandhi Jayanti',
        (10, 12): 'Dussehra',
        (10, 24): 'Diwali',
        (10, 25): 'Diwali',
        (11, 1): 'Diwali',
        (12, 25): 'Christmas',
        (12, 31): 'New Year Eve',
    }

    return festivals.get((month, day), None)


FESTIVAL_FOOD_SUGGESTIONS = {
    'New Year': {
        'cuisines': ['Continental', 'Italian'],
        'message': 'Ring in the new year with celebratory dining',
        'icon': '🎊'
    },
    'Makar Sankranti': {
        'cuisines': ['Street Food', 'Desserts'],
        'message': 'Try til-gud sweets and seasonal festive treats',
        'icon': '🪁'
    },
    'Holi': {
        'cuisines': ['Street Food', 'Desserts', 'Indian'],
        'message': 'Gujiya, thandai and festive Holi specials are calling',
        'icon': '🎨'
    },
    'Raksha Bandhan': {
        'cuisines': ['Desserts', 'Indian'],
        'message': 'Sweet shops are stocked up for the occasion',
        'icon': '🎀'
    },
    'Ganesh Chaturthi': {
        'cuisines': ['Indian', 'Street Food', 'Desserts'],
        'message': 'Modak season — find the best ones near you',
        'icon': '🐘'
    },
    'Dussehra': {
        'cuisines': ['Indian', 'Street Food'],
        'message': 'Festive thalis and street food fairs are in full swing',
        'icon': '🏹'
    },
    'Diwali': {
        'cuisines': ['Desserts', 'Indian'],
        'message': 'Special Diwali menus and mithai are everywhere',
        'icon': '🪔'
    },
    'Christmas': {
        'cuisines': ['Continental', 'Desserts'],
        'message': 'Festive Christmas specials and cakes are in season',
        'icon': '🎄'
    },
    'New Year Eve': {
        'cuisines': ['Continental', 'Italian'],
        'message': 'Book ahead — NYE spots fill up fast',
        'icon': '🎆'
    },
    'Independence Day': {
        'cuisines': ['Indian', 'Street Food'],
        'message': 'Tricolour-themed menus at many restaurants today',
        'icon': '🇮🇳'
    },
    'Gandhi Jayanti': {
        'cuisines': ['Indian'],
        'message': 'Many restaurants offer simple, traditional thalis today',
        'icon': '🕊️'
    },
}


def get_festival_suggestion(festival_name):
    if not festival_name:
        return None
    return FESTIVAL_FOOD_SUGGESTIONS.get(festival_name)


def get_context_recommendation(context):
    recommendations = []

    # weather based
    if context['weather'] == 'rainy':
        recommendations.append('Cozy indoor spots, hot soups and chai cafes')
    elif context['weather'] == 'sunny':
        recommendations.append('Rooftop dining and open air restaurants')
    elif context['weather'] == 'stormy':
        recommendations.append('Comfort food and warm interiors')

    # time based
    if context['time_of_day'] == 'early_morning':
        recommendations.append('Breakfast spots and chai stalls')
    elif context['time_of_day'] == 'lunch':
        recommendations.append('Quick lunch spots and thali places')
    elif context['time_of_day'] == 'late_night':
        recommendations.append('Late night dhabas and 24 hour restaurants')
    elif context['time_of_day'] == 'midnight':
        recommendations.append('24 hour joints and night canteens')

    # day based
    if context['day_type'] in ['saturday', 'sunday']:
        recommendations.append('Brunch spots and family restaurants')
    elif context['day_type'] == 'friday':
        recommendations.append('Happy hour spots and casual dining')

    # festival based
    if context['festival']:
        recommendations.append(f'Special {context["festival"]} menus and festive restaurants')

    return recommendations