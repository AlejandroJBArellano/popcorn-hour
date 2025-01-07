from flask import Blueprint, render_template
from flask_login import current_user
from app.models.user import User

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home/home_authenticated.html')
    return render_template('home/home_guest.html')
