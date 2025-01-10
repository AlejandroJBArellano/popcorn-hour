import os
import tempfile
import pytest
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review
from app.models.comment import Comment

@pytest.fixture(scope='session')
def app():
    """Crear aplicación para las pruebas."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    return app

@pytest.fixture(scope='session')
def _db(app):
    """Crear y configurar base de datos para las pruebas."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(_db):
    """Crear una nueva sesión de base de datos para cada test."""
    connection = _db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)
    
    _db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def test_user(db_session):
    """Crear usuario de prueba."""
    user = User(
        username='testuser',
        email='test@example.com',
        user_type='standard'
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope='function')
def moderator_user(db_session):
    """Crear usuario moderador de prueba."""
    moderator = User(
        username='moderator',
        email='moderator@example.com',
        user_type='moderator'
    )
    moderator.set_password('moderator123')
    db_session.add(moderator)
    db_session.commit()
    return moderator

@pytest.fixture(scope='function')
def test_movie(db_session, moderator_user):
    """Crear película de prueba."""
    movie = Movie(
        title='Test Movie',
        description='Test movie description',
        release_date=datetime.now().date(),
        duration=120,
        moderator_id=moderator_user.id
    )
    db_session.add(movie)
    db_session.commit()
    return movie

@pytest.fixture(scope='function')
def test_review(db_session, test_user, test_movie):
    """Crear reseña de prueba."""
    review = Review(
        content='Test review content',
        rating=4,
        user_id=test_user.id,
        movie_id=test_movie.id
    )
    db_session.add(review)
    db_session.commit()
    return review

@pytest.fixture(scope='function')
def test_comment(db_session, test_user, test_movie):
    """Crear comentario de prueba."""
    comment = Comment(
        content='Test comment content',
        user_id=test_user.id,
        movie_id=test_movie.id
    )
    db_session.add(comment)
    db_session.commit()
    return comment

@pytest.fixture(scope='function')
def client(app):
    """Crear cliente de prueba."""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_client(client, test_user):
    """Crear cliente autenticado."""
    with client:
        client.post('/login', data={
            'email': test_user.email,
            'password': 'password123'
        }, follow_redirects=True)
        yield client

@pytest.fixture(scope='function')
def mod_client(client, moderator_user):
    """Crear cliente moderador autenticado."""
    with client:
        client.post('/login', data={
            'email': moderator_user.email,
            'password': 'moderator123'
        }, follow_redirects=True)
        yield client