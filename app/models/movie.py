from app import db
from datetime import datetime

movie_genres = db.Table('movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duración en minutos
    poster_url = db.Column(db.String(500))
    average_rating = db.Column(db.Float, default=0.0)
    content_type = db.Column(db.String(20), default='movie')  # 'movie' o 'series'
    
    # Información de moderación
    moderator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    genres = db.relationship('Genre', secondary=movie_genres, backref='movies')
    reviews = db.relationship('Review', backref='movie', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='movie', lazy='dynamic', cascade='all, delete-orphan')
    
    # Watchlist - relación muchos a muchos con User a través de Watchlist
    watchers = db.relationship('User', secondary='watchlist', backref=db.backref('watched_movies', lazy='dynamic'))

    def __repr__(self):
        return f'<Movie {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'release_date': self.release_date.strftime('%Y-%m-%d'),
            'duration': self.duration,
            'poster_url': self.poster_url,
            'average_rating': self.average_rating,
            'content_type': self.content_type,
            'genres': [genre.name for genre in self.genres],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }