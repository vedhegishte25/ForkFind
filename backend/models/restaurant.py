from backend import db
from datetime import datetime
import json

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(300), unique=True, nullable=False)  # Google Places ID
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(400), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # details
    cuisine_type = db.Column(db.String(200), nullable=True)
    price_level = db.Column(db.Integer, nullable=True)         # 1-4 (Google scale)
    average_rating = db.Column(db.Float, nullable=True)
    total_reviews = db.Column(db.Integer, default=0)
    photo_url = db.Column(db.String(500), nullable=True)
    google_maps_url = db.Column(db.String(500), nullable=True)

    # vibe tags stored as JSON
    vibe_tags = db.Column(db.Text, default='[]')
    # example: ["rooftop", "romantic", "instagrammable"]

    # hidden gem score
    gem_score = db.Column(db.Float, default=0.0)               # 0-10
    is_hidden_gem = db.Column(db.Boolean, default=False)
    is_newly_opened = db.Column(db.Boolean, default=False)

    # meta
    last_fetched = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    reviews = db.relationship('Review', backref='restaurant', lazy=True)

    # helpers
    def get_vibes(self):
        return json.loads(self.vibe_tags)

    def set_vibes(self, vibes_list):
        self.vibe_tags = json.dumps(vibes_list)

    def to_dict(self):
        return {
            'id': self.id,
            'place_id': self.place_id,
            'name': self.name,
            'address': self.address,
            'cuisine_type': self.cuisine_type,
            'price_level': self.price_level,
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews,
            'photo_url': self.photo_url,
            'vibe_tags': self.get_vibes(),
            'gem_score': self.gem_score,
            'is_hidden_gem': self.is_hidden_gem,
        }

    def __repr__(self):
        return f'<Restaurant {self.name}>'