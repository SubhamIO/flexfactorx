from datetime import datetime
from flask import Blueprint, redirect, url_for, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
oauth    = OAuth()


def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )


@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tools'))
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    try:
        token    = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo') or {}
    except Exception:
        return redirect(url_for('auth.login'))

    google_id = userinfo.get('sub')
    if not google_id:
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(google_id=google_id).first()
    if user:
        user.name       = userinfo.get('name', user.name)
        user.picture    = userinfo.get('picture', user.picture)
        user.last_login = datetime.utcnow()
    else:
        user = User(
            google_id=google_id,
            email=userinfo.get('email', ''),
            name=userinfo.get('name', ''),
            picture=userinfo.get('picture', ''),
        )
        db.session.add(user)

    db.session.commit()
    login_user(user, remember=True)

    next_url = request.args.get('next') or url_for('tools')
    return redirect(next_url)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@auth_bp.route('/me')
def me():
    if current_user.is_authenticated:
        return jsonify({
            'id':      current_user.id,
            'name':    current_user.name,
            'email':   current_user.email,
            'picture': current_user.picture,
        })
    return jsonify(None)
