from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import current_user, login_required
from models.User import User
from models import db

# Blueprint oluşturma
main_bp = Blueprint('main', __name__)

# Anasayfa yönlendirmesi
@main_bp.route('/')
def home_redirect():
    if 'username' in session:  # session üzerinden kullanıcıyı kontrol et
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

# Anasayfa
@main_bp.route('/home')
@login_required
def home():
    if 'username' not in session:  # session üzerinden kullanıcıyı kontrol et
        flash('Kullanıcı bulunamadı!', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()  # Kullanıcıyı session'dan al
    return render_template('home.html', user=user)

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

# Şifre değiştirme işlemi
@main_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Eski şifreyi doğrulama
    if not current_user.check_password(current_password):  # Kullanıcı nesnesi üzerinden şifre kontrolü yapıyoruz
        flash('Eski şifreyi yanlış girdiniz.', 'danger')
        return redirect(url_for('main.profile'))

    # Yeni şifreler eşleşiyor mu?
    if new_password != confirm_password:
        flash('Yeni şifreler uyuşmuyor!', 'danger')
        return redirect(url_for('main.profile'))

    # Yeni şifreyi hash'leyip kaydetme
    hashed_password = current_user.generate_pass(new_password)  # Şifreyi set_password fonksiyonu ile hash'leyip alıyoruz

    # Eğer şifre hash'lenmişse, güncelleme işlemini yap
    if hashed_password:
        current_user.password = hashed_password
        db.session.commit()
        flash('Şifreniz başarıyla değiştirildi!', 'success')
    else:
        flash('Şifre güncellenirken bir hata oluştu!', 'danger')

    return redirect(url_for('main.profile'))


