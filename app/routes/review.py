from flask import Blueprint, request, jsonify
from models import Review, db

review_bp = Blueprint('review', __name__)

@review_bp.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.all()
    return jsonify([review.to_dict() for review in reviews])

@review_bp.route('/reviews/<int:id>', methods=['GET'])
def get_review(id):
    review = Review.query.get_or_404(id)
    return jsonify(review.to_dict())

@review_bp.route('/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    new_review = Review(
        user_id=data['user_id'],
        movie_id=data['movie_id'],
        rating=data['rating'],
        comment=data['comment']
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify(new_review.to_dict()), 201

@review_bp.route('/reviews/<int:id>', methods=['PUT'])
def update_review(id):
    review = Review.query.get_or_404(id)
    data = request.get_json()
    review.rating = data.get('rating', review.rating)
    review.comment = data.get('comment', review.comment)
    db.session.commit()
    return jsonify(review.to_dict())

@review_bp.route('/reviews/<int:id>', methods=['DELETE'])
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return '', 204