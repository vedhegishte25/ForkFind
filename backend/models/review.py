from backend import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # review content
    rating = db.Column(db.Integer, nullable=False)             # 1-5
    written_review = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)

    # mood and occasion tagging
    mood_tag = db.Column(db.String(100), nullable=True)
    # example: "date night", "comfort food", "celebration"

    occasion_tag = db.Column(db.String(100), nullable=True)
    # example: "birthday", "solo", "family dinner"

    # sentiment (filled by AI engine)
    sentiment = db.Column(db.String(20), nullable=True)        # positive, neutral, negative
    liked = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'restaurant_id': self.restaurant_id,
            'rating': self.rating,
            'written_review': self.written_review,
            'photo_url': self.photo_url,
            'mood_tag': self.mood_tag,
            'occasion_tag': self.occasion_tag,
            'sentiment': self.sentiment,
            'liked': self.liked,
            'created_at': self.created_at.strftime('%d %b %Y')
        }

    def __repr__(self):
        return f'<Review user={self.user_id} restaurant={self.restaurant_id} rating={self.rating}>'