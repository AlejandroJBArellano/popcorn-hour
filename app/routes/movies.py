from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.movie import Movie
from app.models.review import Review
from app.models.comment import Comment
from app import db

bp = Blueprint('movies', __name__)

@bp.route('/movies')
def list():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'date')
    genre = request.args.get('genre')
    search = request.args.get('search')

    movies_query = Movie.query

    # Aplicar filtros
    if genre:
        movies_query = movies_query.filter(Movie.genres.any(name=genre))
    if search:
        movies_query = movies_query.filter(Movie.title.ilike(f'%{search}%'))

    # Aplicar ordenamiento
    if sort_by == 'rating':
        movies_query = movies_query.order_by(Movie.average_rating.desc())
    elif sort_by == 'title':
        movies_query = movies_query.order_by(Movie.title.asc())
    else:  # default: date
        movies_query = movies_query.order_by(Movie.created_at.desc())

    # Paginación
    movies = movies_query.paginate(page=page, per_page=12, error_out=False)
    
    return render_template('movies/list.html', movies=movies)

@bp.route('/movies/<int:id>')
def detail(id):
    movie = Movie.query.get_or_404(id)
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            movie_id=id, 
            user_id=current_user.id
        ).first()
    
    # Obtener reseñas paginadas
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(movie_id=id)\
        .order_by(Review.created_at.desc())\
        .paginate(page=page, per_page=5)
    
    # Obtener comentarios
    comments = Comment.query.filter_by(movie_id=id)\
        .order_by(Comment.created_at.desc())\
        .limit(10).all()
    
    return render_template('movies/detail.html',
                         movie=movie,
                         user_review=user_review,
                         reviews=reviews,
                         comments=comments)

@bp.route('/movies/<int:id>/review', methods=['POST'])
@login_required
def review(id):
    movie = Movie.query.get_or_404(id)
    rating = request.form.get('rating', type=int)
    content = request.form.get('content')

    if not 1 <= rating <= 5:
        flash('La calificación debe estar entre 1 y 5', 'danger')
        return redirect(url_for('movies.detail', id=id))

    existing_review = Review.query.filter_by(
        movie_id=id,
        user_id=current_user.id
    ).first()

    if existing_review:
        existing_review.rating = rating
        existing_review.content = content
        flash('Tu reseña ha sido actualizada', 'success')
    else:
        review = Review(
            movie_id=id,
            user_id=current_user.id,
            rating=rating,
            content=content
        )
        db.session.add(review)
        flash('Tu reseña ha sido publicada', 'success')

    # Actualizar rating promedio de la película
    avg_rating = Review.query.with_entities(
        db.func.avg(Review.rating)
    ).filter_by(movie_id=id).scalar()
    movie.average_rating = round(float(avg_rating), 1)

    db.session.commit()
    return redirect(url_for('movies.detail', id=id))

@bp.route('/movies/<int:id>/comment', methods=['POST'])
@login_required
def comment(id):
    Movie.query.get_or_404(id)  # Verificar que la película existe
    content = request.form.get('content')
    parent_id = request.form.get('parent_id', type=int)

    if not content:
        flash('El comentario no puede estar vacío', 'danger')
        return redirect(url_for('movies.detail', id=id))

    comment = Comment(
        movie_id=id,
        user_id=current_user.id,
        content=content,
        parent_comment_id=parent_id
    )
    db.session.add(comment)
    db.session.commit()

    flash('Tu comentario ha sido publicado', 'success')
    return redirect(url_for('movies.detail', id=id))