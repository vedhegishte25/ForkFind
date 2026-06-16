from backend import db
from datetime import datetime
import json

class FoodProfile(db.Model):
    __tablename__ = 'food_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # taste preferences
    spice_tolerance = db.Column(db.Integer, default=5)        # 1-10
    diet_type = db.Column(db.String(50), default='non-veg')   # veg, non-veg, vegan
    budget_min = db.Column(db.Integer, default=200)            # per person in ₹
    budget_max = db.Column(db.Integer, default=800)            # per person in ₹

    # vibe preferences stored as JSON
    preferred_vibes = db.Column(db.Text, default='[]')         # ["rooftop", "cozy", "quiet"]
    favourite_cuisines = db.Column(db.Text, default='[]')      # ["Indian", "Italian"]
    disliked_cuisines = db.Column(db.Text, default='[]')       # ["Chinese"]

    # food DNA stored as JSON
    food_dna = db.Column(db.Text, default='{}')
    # example: {"Indian": 40, "Italian": 25, "Asian": 15, "Street Food": 10, "Desserts": 10}

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # helpers
    def get_vibes(self):
        return json.loads(self.preferred_vibes)

    def set_vibes(self, vibes_list):
        self.preferred_vibes = json.dumps(vibes_list)

    def get_cuisines(self):
        return json.loads(self.favourite_cuisines)

    def set_cuisines(self, cuisines_list):
        self.favourite_cuisines = json.dumps(cuisines_list)

    def get_food_dna(self):
        return json.loads(self.food_dna)

    def set_food_dna(self, dna_dict):
        self.food_dna = json.dumps(dna_dict)

    def __repr__(self):
        return f'<FoodProfile user_id={self.user_id}>'