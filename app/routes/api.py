from flask import Blueprint, request, jsonify, session
from app.models import User
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
