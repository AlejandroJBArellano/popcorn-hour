from app import db
from datetime import datetime

class Genre(db.Model):
    """
    Modelo para los géneros de películas y series.
    Permite categorizar el contenido y facilitar la búsqueda y filtrado.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para SEO y organización
    slug = db.Column(db.String(50), unique=True, nullable=False)
    icon_class = db.Column(db.String(50))  # Para iconos de Font Awesome o similar
    
    # Estadísticas
    movie_count = db.Column(db.Integer, default=0)
    series_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Genre {self.name}>'

    def __str__(self):
        return self.name

    @staticmethod
    def get_or_create(name, description=None):
        """
        Obtiene un género existente o crea uno nuevo si no existe.
        
        Args:
            name (str): Nombre del género
            description (str, optional): Descripción del género
            
        Returns:
            Genre: Instancia del género obtenido o creado
        """
        from slugify import slugify
        
        genre = Genre.query.filter_by(name=name).first()
        if not genre:
            genre = Genre(
                name=name,
                description=description,
                slug=slugify(name)
            )
            db.session.add(genre)
            db.session.commit()
        return genre

    def update_counts(self):
        """
        Actualiza los contadores de películas y series para este género.
        """
        from app.models.movie import Movie
        
        self.movie_count = Movie.query.filter_by(
            content_type='movie'
        ).filter(
            Movie.genres.contains(self)
        ).count()
        
        self.series_count = Movie.query.filter_by(
            content_type='series'
        ).filter(
            Movie.genres.contains(self)
        ).count()
        
        db.session.commit()

    def to_dict(self):
        """
        Convierte el género a un diccionario.
        
        Returns:
            dict: Representación del género en formato diccionario
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'movie_count': self.movie_count,
            'series_count': self.series_count,
            'total_content': self.movie_count + self.series_count,
            'icon_class': self.icon_class
        }

    @classmethod
    def get_popular(cls, limit=10):
        """
        Obtiene los géneros más populares basados en la cantidad total de contenido.
        
        Args:
            limit (int): Número máximo de géneros a retornar
            
        Returns:
            list: Lista de géneros ordenados por popularidad
        """
        return cls.query.order_by(
            (cls.movie_count + cls.series_count).desc()
        ).limit(limit).all()

    @classmethod
    def initialize_default_genres(cls):
        """
        Inicializa los géneros por defecto en la base de datos.
        Útil para el setup inicial de la aplicación.
        """
        default_genres = [
            ('Acción', 'Películas llenas de secuencias intensas y emocionantes'),
            ('Comedia', 'Contenido diseñado para hacer reír'),
            ('Drama', 'Historias serias con enfoque en las emociones y conflictos'),
            ('Ciencia Ficción', 'Historias basadas en avances científicos y futuristas'),
            ('Terror', 'Contenido diseñado para asustar y generar tensión'),
            ('Romance', 'Historias centradas en relaciones románticas'),
            ('Documental', 'Contenido basado en hechos reales'),
            ('Animación', 'Contenido creado mediante técnicas de animación'),
            ('Aventura', 'Historias de viajes y descubrimientos'),
            ('Fantasía', 'Historias con elementos mágicos y sobrenaturales')
        ]

        for name, description in default_genres:
            cls.get_or_create(name, description)