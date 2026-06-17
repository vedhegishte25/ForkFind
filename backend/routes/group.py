from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from backend import db
from backend.models.group_session import GroupSession
from backend.services.ai_engine import solve_group_decision
from backend.services.places_service import search_restaurants

group = Blueprint('group', __name__)


@group.route('/')
@login_required
def index():
    return render_template('group.html')


@group.route('/create', methods=['POST'])
@login_required
def create_session():
    session = GroupSession(created_by=current_user.id)
    session.add_member(current_user.id)

    db.session.add(session)
    db.session.commit()

    return jsonify({
        'session_code': session.session_code,
        'message': 'Session created. Share the code with your friends.'
    })


@group.route('/join', methods=['POST'])
@login_required
def join_session():
    data = request.get_json()
    session_code = data.get('session_code', '').upper()

    session = GroupSession.query.filter_by(session_code=session_code).first()

    if not session:
        return jsonify({'error': 'Invalid session code'}), 404

    if session.status == 'solved':
        return jsonify({'error': 'This session is already solved'}), 400

    session.add_member(current_user.id)
    db.session.commit()

    return jsonify({
        'session_code': session.session_code,
        'members': session.get_members(),
        'message': f'Joined session {session_code}'
    })


@group.route('/preferences', methods=['POST'])
@login_required
def submit_preferences():
    data = request.get_json()
    session_code = data.get('session_code', '').upper()

    session = GroupSession.query.filter_by(session_code=session_code).first()

    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # save this member's preferences
    prefs = {
        'budget': data.get('budget', 500),
        'cuisines': data.get('cuisines', []),
        'distance': data.get('distance', 5),
        'dietary': data.get('dietary', 'non-veg'),
        'vibes': data.get('vibes', [])
    }

    session.set_preference(current_user.id, prefs)
    session.status = 'active'
    db.session.commit()

    return jsonify({
        'message': 'Preferences saved',
        'members_submitted': len(session.get_preferences())
    })


@group.route('/solve', methods=['POST'])
@login_required
def solve():
    data = request.get_json()
    session_code = data.get('session_code', '').upper()
    city = data.get('city', current_user.city)
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    session = GroupSession.query.filter_by(session_code=session_code).first()

    if not session:
        return jsonify({'error': 'Session not found'}), 404

    preferences = session.get_preferences()

    if len(preferences) < 2:
        return jsonify({'error': 'At least 2 members need to submit preferences'}), 400

    # ask AI to find common ground
    ai_result = solve_group_decision(preferences, city)

    # search real restaurants
    restaurants = search_restaurants(
        query=ai_result.get('search_query', 'restaurant'),
        city=city,
        latitude=latitude,
        longitude=longitude
    )

    result = {
        'ai_message': ai_result.get('message', ''),
        'common_cuisines': ai_result.get('common_cuisines', []),
        'budget_range': ai_result.get('budget_range', ''),
        'recommended_vibes': ai_result.get('vibes', []),
        'restaurants': restaurants
    }

    session.set_result(result)
    session.status = 'solved'
    db.session.commit()

    return jsonify(result)


@group.route('/status/<string:session_code>')
@login_required
def session_status(session_code):
    session = GroupSession.query.filter_by(
        session_code=session_code.upper()
    ).first()

    if not session:
        return jsonify({'error': 'Session not found'}), 404

    return jsonify({
        'session_code': session.session_code,
        'status': session.status,
        'members_count': len(session.get_members()),
        'preferences_submitted': len(session.get_preferences()),
        'result': session.get_result() if session.status == 'solved' else None
    })