import pytest
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.movie import Movie, movie_genres
from app.models.review import Review
from app.models.comment import Comment

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

class TestUserModel:
    def test_create_user(self, db_session):
        user = User(
            username='testuser',
            email='test@example.com',
            user_type='standard'
        )
        user.set_password('password123')
        db_session.add(user)
        db_session.commit()

        saved_user = User.query.filter_by(username='testuser').first()
        assert saved_user is not None
        assert saved_user.email == 'test@example.com'
        assert saved_user.check_password('password123')

    def test_user_unique_constraints(self, db_session):
        user1 = User(username='user1', email='user1@example.com')
        user2 = User(username='user1', email='user2@example.com')
        
        db_session.add(user1)
        db_session.commit()
        
        with pytest.raises(Exception):
            db_session.add(user2)
            db_session.commit()

class TestMovieModel:
    @pytest.fixture
    def sample_movie(self, db_session):
        moderator = User(
            username='mod',
            email='mod@example.com',
            user_type='moderator'
        )
        db_session.add(moderator)
        db_session.commit()

        movie = Movie(
            title='Test Movie',
            description='Test Description',
            release_date=datetime.now().date(),
            duration=120,
            moderator_id=moderator.id
        )
        db_session.add(movie)
        db_session.commit()
        return movie

    def test_create_movie(self, sample_movie):
        assert sample_movie.id is not None
        assert sample_movie.title == 'Test Movie'
        assert sample_movie.average_rating == 0.0

    def test_movie_reviews(self, db_session, sample_movie):
        user = User(username='reviewer', email='reviewer@example.com')
        db_session.add(user)
        db_session.commit()

        review = Review(
            content='Great movie!',
            rating=5,
            user_id=user.id,
            movie_id=sample_movie.id
        )
        db_session.add(review)
        db_session.commit()

        assert len(sample_movie.reviews.all()) == 1
        assert sample_movie.reviews.first().rating == 5

class TestReviewModel:
    def test_review_constraints(self, db_session, sample_movie):
        user = User(username='reviewer', email='reviewer@example.com')
        db_session.add(user)
        db_session.commit()

        # Primera reseña - debería funcionar
        review1 = Review(
            content='First review',
            rating=4,
            user_id=user.id,
            movie_id=sample_movie.id
        )
        db_session.add(review1)
        db_session.commit()

        # Segunda reseña del mismo usuario - debería fallar
        review2 = Review(
            content='Second review',
            rating=3,
            user_id=user.id,
            movie_id=sample_movie.id
        )
        with pytest.raises(Exception):
            db_session.add(review2)
            db_session.commit()

    def test_average_rating(self, db_session, sample_movie):
        user1 = User(username='user1', email='user1@example.com')
        user2 = User(username='user2', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()

        review1 = Review(
            content='Review 1',
            rating=4,
            user_id=user1.id,
            movie_id=sample_movie.id
        )
        review2 = Review(
            content='Review 2',
            rating=2,
            user_id=user2.id,
            movie_id=sample_movie.id
        )
        db_session.add_all([review1, review2])
        db_session.commit()

        avg_rating = Review.get_average_rating(sample_movie.id)
        assert avg_rating == 3.0

class TestCommentModel:
    def test_nested_comments(self, db_session, sample_movie):
        user = User(username='commenter', email='commenter@example.com')
        db_session.add(user)
        db_session.commit()

        # Comentario principal
        parent_comment = Comment(
            content='Parent comment',
            user_id=user.id,
            movie_id=sample_movie.id
        )
        db_session.add(parent_comment)
        db_session.commit()

        # Respuesta al comentario
        reply = Comment(
            content='Reply comment',
            user_id=user.id,
            movie_id=sample_movie.id,
            parent_comment_id=parent_comment.id
        )
        db_session.add(reply)
        db_session.commit()

        assert len(parent_comment.replies.all()) == 1
        assert parent_comment.replies.first().content == 'Reply comment'

    def test_comment_moderation(self, db_session, sample_movie):
        user = User(username='commenter', email='commenter@example.com')
        db_session.add(user)
        db_session.commit()

        comment = Comment(
            content='Test comment',
            user_id=user.id,
            movie_id=sample_movie.id
        )
        db_session.add(comment)
        db_session.commit()

        # Probar ocultamiento
        comment.hide('Inappropriate content')
        assert comment.is_hidden
        assert comment.hidden_reason == 'Inappropriate content'

        # Probar mostrar
        comment.unhide()
        assert not comment.is_hidden
        assert comment.hidden_reason is None