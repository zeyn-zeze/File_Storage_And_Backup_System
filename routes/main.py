from flask import Blueprint, render_template, session, redirect, url_for, flash, g
from flask_login import current_user, login_required
from models.User import User


# Blueprint oluşturma
main_bp = Blueprint('main', __name__)

# Kullanıcıyı her istek öncesinde yüklemek
@main_bp.before_app_request
def load_user():
    if 'username' in session:
        g.user = User.query.filter_by(username=session['username']).first()
    else:
        g.user = None



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
