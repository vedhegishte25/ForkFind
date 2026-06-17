from backend import db
from datetime import datetime
import json

class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_icon = db.Column(db.String(100), nullable=True)      # emoji or icon name
    target_count = db.Column(db.Integer, nullable=False)       # how many to complete
    challenge_type = db.Column(db.String(50), nullable=False)
    # types: "unique_restaurants", "street_food", "desserts", "cuisines", "districts"

    # criteria stored as JSON
    criteria = db.Column(db.Text, default='{}')
    # example: {"cuisine": "street food", "city": "Thane"}

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    user_challenges = db.relationship('UserChallenge', backref='challenge', lazy=True)

    def get_criteria(self):
        return json.loads(self.criteria)

    def __repr__(self):
        return f'<Challenge {self.name}>'


class UserChallenge(db.Model):
    __tablename__ = 'user_challenges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)

    # progress
    current_count = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # restaurants checked in stored as JSON list
    checked_in_restaurants = db.Column(db.Text, default='[]')

    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_checked_in(self):
        return json.loads(self.checked_in_restaurants)

    def add_checkin(self, restaurant_id):
        checked = self.get_checked_in()
        if restaurant_id not in checked:
            checked.append(restaurant_id)
            self.checked_in_restaurants = json.dumps(checked)
            self.current_count = len(checked)

    def progress_percent(self):
        return round((self.current_count / self.challenge.target_count) * 100)

    def to_dict(self):
        return {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'challenge_name': self.challenge.name,
            'badge_name': self.challenge.badge_name,
            'badge_icon': self.challenge.badge_icon,
            'target_count': self.challenge.target_count,
            'current_count': self.current_count,
            'progress_percent': self.progress_percent(),
            'completed': self.completed,
            'completed_at': self.completed_at.strftime('%d %b %Y') if self.completed_at else None
        }

    def __repr__(self):
        return f'<UserChallenge user={self.user_id} challenge={self.challenge_id}>'