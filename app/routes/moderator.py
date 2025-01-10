from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.movie import Movie
from app.models.genre import Genre
from app import db
from app.forms.movie import MovieForm
from datetime import datetime
from functools import wraps

bp = Blueprint('moderator', __name__, url_prefix='/moderator')

def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'moderator':
            flash('Acceso denegado. Se requieren privilegios de moderador.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@moderator_required
def dashboard():
    # Obtener películas subidas por el moderador actual
    movies = Movie.query.filter_by(moderator_id=current_user.id)\
        .order_by(Movie.created_at.desc()).all()
    return render_template('moderator/dashboard.html', movies=movies)

@bp.route('/movies/add', methods=['GET', 'POST'])
@login_required
@moderator_required
def add_movie():
    form = MovieForm()
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name')]

    if form.validate_on_submit():
        movie = Movie(
            title=form.title.data,
            description=form.description.data,
            release_date=form.release_date.data,
            duration=form.duration.data,
            content_type=form.content_type.data,
            moderator_id=current_user.id
        )

        # Manejar la imagen del póster
        if form.poster.data:
            try:
                filename = save_poster(form.poster.data)
                movie.poster_url = filename
            except Exception as e:
                flash('Error al guardar el póster. La película se guardará sin imagen.', 'warning')

        # Agregar géneros
        selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        movie.genres.extend(selected_genres)

        db.session.add(movie)
        db.session.commit()

        flash('Película agregada exitosamente', 'success')
        return redirect(url_for('moderator.dashboard'))

    return render_template('moderator/add_movie.html', form=form)

@bp.route('/movies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@moderator_required
def edit_movie(id):
    movie = Movie.query.get_or_404(id)
    
    # Verificar que el moderador sea el propietario
    if movie.moderator_id != current_user.id:
        flash('No tienes permiso para editar esta película', 'danger')
        return redirect(url_for('moderator.dashboard'))

    form = MovieForm(obj=movie)
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by('name')]

    if form.validate_on_submit():
        movie.title = form.title.data
        movie.description = form.description.data
        movie.release_date = form.release_date.data
        movie.duration = form.duration.data
        movie.content_type = form.content_type.data

        if form.poster.data:
            try:
                filename = save_poster(form.poster.data)
                movie.poster_url = filename
            except Exception as e:
                flash('Error al actualizar el póster.', 'warning')

        movie.genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
        db.session.commit()

        flash('Película actualizada exitosamente', 'success')
        return redirect(url_for('moderator.dashboard'))

    # Pre-seleccionar géneros actuales
    form.genres.data = [g.id for g in movie.genres]
    return render_template('moderator/edit_movie.html', form=form, movie=movie)

@bp.route('/movies/<int:id>/delete', methods=['POST'])
@login_required
@moderator_required
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    
    if movie.moderator_id != current_user.id:
        flash('No tienes permiso para eliminar esta película', 'danger')
        return redirect(url_for('moderator.dashboard'))

    db.session.delete(movie)
    db.session.commit()
    
    flash('Película eliminada exitosamente', 'success')
    return redirect(url_for('moderator.dashboard'))