from flask import Blueprint, render_template, session, redirect, url_for, flash, g
from models.User import User
from functools import wraps

# Blueprint oluşturma
main_bp = Blueprint('main', __name__)

# Kullanıcıyı her istek öncesinde yüklemek
@main_bp.before_app_request
def load_user():
    if 'username' in session:
        g.user = User.query.filter_by(username=session['username']).first()
    else:
        g.user = None

# Giriş yapmamış kullanıcıları yönlendirmek için dekoratör
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Lütfen giriş yapınız!', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Anasayfa yönlendirmesi
@main_bp.route('/')
def home_redirect():
    if g.user:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

# Anasayfa
@main_bp.route('/home')
@login_required
def home():
    if not g.user:
        flash('Kullanıcı bulunamadı!', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('home.html', user=g.user)

# Profil sayfası
@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=g.user)
