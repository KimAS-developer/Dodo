from flask import Blueprint

from domain.user import User
from dev.extensions import db

user = Blueprint('user', __name__)

@user.route('/signin/<name>')
def sign_in(name):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return 'hello'