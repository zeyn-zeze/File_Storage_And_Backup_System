from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.User import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home_redirect():
    if 'username' in session:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

@main_bp.route('/home')
def home():
    if 'username' not in session:
        flash('Lütfen giriş yapınız!', 'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Kullanıcı bulunamadı!', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('home.html', user=user)


@main_bp.route('/profile')
def profile():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template('profile.html', user=user)
    flash('Lütfen giriş yapınız!', 'warning')
    return redirect(url_for('auth.login'))
