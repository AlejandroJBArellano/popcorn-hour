from app import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Calificación de 1 a 5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    # Restricción única para evitar múltiples reseñas del mismo usuario para la misma película
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_review'),)

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id} for Movie {self.movie_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'rating': self.rating,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_average_rating(movie_id):
        """Calcula el rating promedio para una película específica"""
        result = db.session.query(
            db.func.avg(Review.rating)
        ).filter_by(movie_id=movie_id).scalar()
        return float(result) if result else 0.0