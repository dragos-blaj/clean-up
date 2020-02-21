import functools

from flask import (
    Blueprint, g, request, session,
    jsonify)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash

from cleanup.auth.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@bp.route('/login', methods=('POST',))
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    error = None
    user = User.query.filter_by(username=username).first()  # type: User

    if user is None:
        error = {'error': 'incorrect username'}
    elif not check_password_hash(user.password, password):
        error = {'error': 'incorrect password'}

    if error is None:
        session.clear()
        session['user_id'] = user.id
        return jsonify({
            'username': user.username
        })

    return jsonify(error)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(401)

        return view(**kwargs)

    return wrapped_view
