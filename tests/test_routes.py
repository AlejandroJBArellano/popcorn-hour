import pytest
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review
from datetime import datetime

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False  # Deshabilitar CSRF para testing
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, test_user):
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Bienvenido' in response.data
    return client

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

class TestAuthRoutes:
    def test_login_page(self, client):
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Iniciar' in response.data

    def test_register_page(self, client):
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Crear Cuenta' in response.data

    def test_successful_registration(self, client):
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        assert b'cuenta ha sido creada' in response.data

    def test_duplicate_registration(self, client, test_user):
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        assert b'Ya existe' in response.data

class TestMovieRoutes:
    @pytest.fixture
    def sample_movie(self, app, test_user):
        with app.app_context():
            movie = Movie(
                title='Test Movie',
                description='Test Description',
                release_date=datetime.now().date(),
                duration=120,
                moderator_id=test_user.id
            )
            db.session.add(movie)
            db.session.commit()
            return movie

    def test_movie_list(self, client):
        response = client.get('/movies')
        assert response.status_code == 200

    def test_movie_detail(self, client, sample_movie):
        response = client.get(f'/movies/{sample_movie.id}')
        assert response.status_code == 200
        assert b'Test Movie' in response.data

    def test_movie_review(self, auth_client, sample_movie):
        response = auth_client.post(f'/movies/{sample_movie.id}/review', data={
            'rating': 4,
            'content': 'Great movie!'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'reseña ha sido publicada'.encode('utf-8') in response.data

    def test_invalid_movie_review(self, auth_client, sample_movie):
        response = auth_client.post(f'/movies/{sample_movie.id}/review', data={
            'rating': 6,  # Rating inválido
            'content': 'Great movie!'
        }, follow_redirects=True)
        assert b'debe estar entre 1 y 5' in response.data

class TestUserRoutes:
    def test_profile_page(self, auth_client, test_user):
        response = auth_client.get(f'/profile/{test_user.username}')
        assert response.status_code == 200
        assert test_user.username.encode() in response.data

    def test_watchlist_operations(self, auth_client, sample_movie):
        # Agregar a watchlist
        response = auth_client.post(
            f'/watchlist/add/{sample_movie.id}',
            follow_redirects=True
        )
        assert b'agregada a tu lista' in response.data

        # Actualizar estado
        response = auth_client.post(
            f'/watchlist/update/{sample_movie.id}',
            data={'status': 'watched'},
            follow_redirects=True
        )
        assert b'Lista actualizada' in response.data

        # Remover de watchlist
        response = auth_client.post(
            f'/watchlist/remove/{sample_movie.id}',
            follow_redirects=True
        )
        assert b'eliminada de tu lista' in response.data

def test_error_pages(client):
    # Test 404
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    
    # Test 403
    # Simular acceso a ruta protegida sin autenticación
    response = client.get('/watchlist')
    assert response.status_code == 302  # Redirección al login