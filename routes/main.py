from flask import Blueprint, render_template, request, session, redirect, url_for, flash, g
from flask_login import current_user, login_required
from models.User import User
from models import db


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
@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    is_editing = False

    if request.args.get('edit'):  # Eğer düzenleme linkine tıklanmışsa
        is_editing = True

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        # Kullanıcı bilgilerini güncelleme
        current_user.username = username
        current_user.email = email
        db.session.commit()

        flash('Profiliniz başarıyla güncellendi!', 'success')
        return redirect(url_for('main.profile'))  # Profil sayfasına yönlendir
    
    return render_template('profile.html', user=current_user, is_editing=is_editing)

# Profil düzenle sayfası
@main_bp.route('/edit_profile')
@login_required
def edit_profile():
    return redirect(url_for('main.profile', edit=True))  # Düzenleme moduna geçiş için 'edit' parametresi ekleniyor
