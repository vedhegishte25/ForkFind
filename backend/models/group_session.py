from backend import db
from datetime import datetime
import json
import random
import string

def generate_session_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class GroupSession(db.Model):
    __tablename__ = 'group_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_code = db.Column(db.String(10), unique=True, nullable=False, default=generate_session_code)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # members stored as JSON list of user ids
    members = db.Column(db.Text, default='[]')

    # each member's preferences stored as JSON
    member_preferences = db.Column(db.Text, default='{}')
    # example: {
    #   "1": {"budget": 500, "cuisine": "Italian", "distance": 2, "dietary": "veg"},
    #   "2": {"budget": 800, "cuisine": "Sushi", "distance": 5, "dietary": "non-veg"}
    # }

    # AI merged result stored as JSON
    merged_result = db.Column(db.Text, default='{}')

    # status
    status = db.Column(db.String(20), default='waiting')
    # waiting → active → solved

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    solved_at = db.Column(db.DateTime, nullable=True)

    # helpers
    def get_members(self):
        return json.loads(self.members)

    def add_member(self, user_id):
        members = self.get_members()
        if user_id not in members:
            members.append(user_id)
            self.members = json.dumps(members)

    def get_preferences(self):
        return json.loads(self.member_preferences)

    def set_preference(self, user_id, prefs):
        preferences = self.get_preferences()
        preferences[str(user_id)] = prefs
        self.member_preferences = json.dumps(preferences)

    def get_result(self):
        return json.loads(self.merged_result)

    def set_result(self, result_dict):
        self.merged_result = json.dumps(result_dict)

    def __repr__(self):
        return f'<GroupSession code={self.session_code} status={self.status}>'