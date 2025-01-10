from app import db
from datetime import datetime

class Watchlist(db.Model):
    """
    Modelo que representa la lista de películas que un usuario quiere ver o ha visto.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Estado de la película en la lista del usuario
    status = db.Column(db.String(20), default='pending')  # pending, watched, dropped
    
    # Fecha en que se vio la película (opcional)
    watched_at = db.Column(db.DateTime)
    
    # Nota personal del usuario (opcional)
    notes = db.Column(db.String(500))

    # Relaciones
    user = db.relationship('User', back_populates='watchlist_items')
    movie = db.relationship('Movie', back_populates='watchlist_items')

    __table_args__ = (
        # Un usuario no puede tener la misma película dos veces en su watchlist
        db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_watchlist'),
    )

    def __repr__(self):
        return f'<Watchlist {self.user_id}:{self.movie_id}>'

    @property
    def status_display(self):
        """Retorna el estado en formato legible."""
        status_dict = {
            'pending': 'Por ver',
            'watched': 'Visto',
            'dropped': 'Descartado'
        }
        return status_dict.get(self.status, self.status)

    def mark_as_watched(self):
        """Marca la película como vista."""
        self.status = 'watched'
        self.watched_at = datetime.utcnow()
        db.session.commit()

    def mark_as_pending(self):
        """Marca la película como pendiente."""
        self.status = 'pending'
        self.watched_at = None
        db.session.commit()

    def mark_as_dropped(self):
        """Marca la película como descartada."""
        self.status = 'dropped'
        db.session.commit()

    def add_note(self, note):
        """Agrega una nota personal a la entrada de la watchlist."""
        self.notes = note
        db.session.commit()

    @classmethod
    def get_user_watchlist(cls, user_id, status=None):
        """
        Obtiene la watchlist de un usuario, opcionalmente filtrada por estado.
        
        Args:
            user_id: ID del usuario
            status: Estado opcional para filtrar ('pending', 'watched', 'dropped')
        """
        query = cls.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.added_at.desc()).all()

    @classmethod
    def get_user_stats(cls, user_id):
        """
        Obtiene estadísticas de la watchlist de un usuario.
        
        Returns:
            dict: Diccionario con estadísticas
        """
        stats = {
            'total': cls.query.filter_by(user_id=user_id).count(),
            'pending': cls.query.filter_by(user_id=user_id, status='pending').count(),
            'watched': cls.query.filter_by(user_id=user_id, status='watched').count(),
            'dropped': cls.query.filter_by(user_id=user_id, status='dropped').count()
        }
        return stats

    def to_dict(self):
        """Convierte la entrada de watchlist a diccionario."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'status': self.status,
            'status_display': self.status_display,
            'added_at': self.added_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'watched_at': self.watched_at.isoformat() if self.watched_at else None,
            'notes': self.notes,
            'movie': {
                'title': self.movie.title,
                'poster_url': self.movie.poster_url
            } if self.movie else None
        }