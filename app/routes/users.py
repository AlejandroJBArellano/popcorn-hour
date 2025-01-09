from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User
from app.models.review import Review
from app.models.movie import Movie
from app.models.watchlist import Watchlist
from app import db

bp = Blueprint('users', __name__)

@bp.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Obtener estadísticas del usuario
    stats = {
        'total_reviews': Review.query.filter_by(user_id=user.id).count(),
        'average_rating': db.session.query(
            db.func.avg(Review.rating)
        ).filter_by(user_id=user.id).scalar() or 0,
        'total_comments': user.comments.count(),
        'watchlist_count': user.watchlist.count()
    }
    
    # Obtener últimas reseñas
    recent_reviews = Review.query.filter_by(user_id=user.id)\
        .order_by(Review.created_at.desc())\
        .limit(5).all()
    
    return render_template('users/profile.html',
                         user=user,
                         stats=stats,
                         recent_reviews=recent_reviews)

@bp.route('/watchlist')
@login_required
def watchlist():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Watchlist.query.filter_by(user_id=current_user.id)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    watchlist = query.order_by(Watchlist.added_at.desc())\
        .paginate(page=page, per_page=12)
    
    return render_template('users/watchlist.html', watchlist=watchlist)

@bp.route('/watchlist/add/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if Watchlist.query.filter_by(
        user_id=current_user.id,
        movie_id=movie_id
    ).first():
        flash('Esta película ya está en tu lista', 'info')
        return redirect(url_for('movies.detail', id=movie_id))
    
    watchlist_item = Watchlist(
        user_id=current_user.id,
        movie_id=movie_id,
        status='pending'
    )
    db.session.add(watchlist_item)
    db.session.commit()
    
    flash('Película agregada a tu lista', 'success')
    return redirect(url_for('movies.detail', id=movie_id))

@bp.route('/watchlist/update/<int:movie_id>', methods=['POST'])
@login_required
def update_watchlist(movie_id):
    status = request.form.get('status')
    if status not in ['watched', 'pending', 'dropped']:
        flash('Estado no válido', 'danger')
        return redirect(url_for('users.watchlist'))
    
    item = Watchlist.query.filter_by(
        user_id=current_user.id,
        movie_id=movie_id
    ).first_or_404()
    
    item.status = status
    db.session.commit()
    
    flash('Lista actualizada', 'success')
    return redirect(url_for('users.watchlist'))

@bp.route('/watchlist/remove/<int:movie_id>', methods=['POST'])
@login_required
def remove_from_watchlist(movie_id):
    Watchlist.query.filter_by(
        user_id=current_user.id,
        movie_id=movie_id
    ).delete()
    db.session.commit()
    
    flash('Película eliminada de tu lista', 'success')
    return redirect(url_for('users.watchlist'))