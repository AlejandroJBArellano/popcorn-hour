from app import db
from datetime import datetime

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    
    # Para comentarios anidados
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # Estado del comentario
    is_edited = db.Column(db.Boolean, default=False)
    is_hidden = db.Column(db.Boolean, default=False)
    hidden_reason = db.Column(db.String(200))

    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'parent_comment_id': self.parent_comment_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_edited': self.is_edited,
            'is_hidden': self.is_hidden
        }

    def hide(self, reason=''):
        """Oculta un comentario con una razón opcional"""
        self.is_hidden = True
        self.hidden_reason = reason
        db.session.commit()

    def unhide(self):
        """Muestra un comentario previamente ocultado"""
        self.is_hidden = False
        self.hidden_reason = None
        db.session.commit()

    def edit(self, new_content):
        """Edita el contenido del comentario"""
        self.content = new_content
        self.is_edited = True
        self.updated_at = datetime.utcnow()
        db.session.commit()