from flask import Blueprint, request, jsonify, session
from app.models import User, Post, Comment, Vote
from app.db import get_db
import sys

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/users', methods=['POST'])
def signup():
    data = request.get_json()
    db = get_db()

    try:
        # Attempt creating a new user
        newUser = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )

        db.add(newUser)
        db.commit()

        # User created successfully, set session variables
        session['user_id'] = newUser.id
        session['loggedIn'] = True

    except Exception as e:  # Catching general exceptions for debugging
        print(sys.exc_info()[0])
        print(e)  # Print the exception message

        # Insert failed, so rollback and clear session
        db.rollback()
        session.clear()
        return jsonify(message='Signup failed'), 500

    return jsonify(id=newUser.id)

@bp.route('/users/logout', methods=['POST'])
def logout():
    # Remove session variables
    session.clear()
    return '', 204

@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()

    try:
        user = db.query(User).filter(User.email == data['email']).one()
    except:
        print(sys.exc_info()[0])
        return jsonify(message='User not found'), 404

    if not user.verify_password(data['password']):
        return jsonify(message='Incorrect credentials'), 400

    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True

    return jsonify(id=user.id)

@bp.route('/comments', methods=['POST'])
def comment():
    data = request.get_json()
    db = get_db()

    try:
        # Create a new comment
        newComment = Comment(
            comment_text=data['comment_text'],
            post_id=data['post_id'],
            user_id=session.get('user_id')
        )

        db.add(newComment)
        db.commit()

    except:
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message='Comment failed'), 500

    return jsonify(id=newComment.id)

@bp.route('/posts/upvote', methods=['PUT'])
def upvote():
    data = request.get_json()
    db = get_db()

    try:
        # create a new vote with incomign id and session id
        newVote = Vote(
            post_id = data['post_id'],
            user_id = session.get('user_id')
        )

        db.add(newVote)
        db.commit()
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Upvote failed'), 500

    return '', 204

@bp.route('/posts', methods=['POST'])
def create():
    data = request.get_json()
    db = get_db()

    try:
    # create a new post
        newPost = Post(
        title = data['title'],
        post_url = data['post_url'],
        user_id = session.get('user_id')
        )

        db.add(newPost)
        db.commit()
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Post failed'), 500

    return jsonify(id = newPost.id)

@bp.route('/posts/<id>', methods=['PUT'])
def update(id):
    data = request.get_json()
    db = get_db()

    try:
        # retrieve post and update title property
        post = db.query(Post).filter(Post.id == id).one()
        post.title = data['title']
        db.commit()
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Post not found'), 404

    return '', 204

@bp.route('/posts/<id>', methods=['DELETE'])
def delete(id):
    db = get_db()

    try:
        # delete post from db
        db.delete(db.query(Post).filter(Post.id == id).one())
        db.commit()
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Post not found'), 404

    return '', 204