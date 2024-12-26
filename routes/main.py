from datetime import datetime
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import current_user, login_required
from islemler.log_manager import LogManager as log_manager
from models.Notification import Notification
from models.PasswordChangeRequest import PasswordChangeRequest
from models.User import User
from models import db,bcrypt
from utils.utils import save_log

# Blueprint oluşturma
main_bp = Blueprint('main', __name__)

# Anasayfa yönlendirmesi
@main_bp.route('/')
def home_redirect():
    if 'username' in session:  # session üzerinden kullanıcıyı kontrol et
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

@main_bp.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)


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
    
    save_log("profile", f"Profil bilgileri başarıyla güncellendi : {current_user.username} - {current_user.email} - {datetime.now()}")
    return redirect(url_for('main.profile', edit=True))  # Düzenleme moduna geçiş için 'edit' parametresi ekleniyor

# Şifre değiştirme işlemi

@main_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Check if the current password matches
    if not bcrypt.check_password_hash(current_user.password, current_password):
        flash('Eski şifreyi yanlış girdiniz.', 'danger')
        return redirect(url_for('main.profile'))

    # Ensure new passwords match
    if new_password != confirm_password:
        flash('Yeni şifreler uyuşmuyor!', 'danger')
        return redirect(url_for('main.profile'))

    # Hash the new password before storing it
    hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Create password change request
    password_request = PasswordChangeRequest(
        user_id=current_user.user_id,
        requested_at=datetime.now(),
        status='pending',
        new_password=hashed_new_password  # Store the hashed new password
    )
    db.session.add(password_request)
    db.session.commit()

    # Log the password change request
    log_manager.log_password_change_request(
        username=current_user.username, 
        status_code="REQUESTED"
    )

    flash('Şifre değişikliği talebiniz iletildi. Yönetici onayı bekleniyor.', 'info')
    return redirect(url_for('main.profile'))




@main_bp.route('/notifications', methods=['GET'])
@login_required
def notifications():
    # Kullanıcıya ait tüm bildirimleri al
    notifications = Notification.query.filter_by(user_id=current_user.user_id).order_by(Notification.timestamp.desc()).all()

    return render_template('bildirimler.html', notifications=notifications)

