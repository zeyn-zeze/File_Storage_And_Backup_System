from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_user
from models.User import User, db
from utils.utils import save_log
from datetime import datetime
from islemler.log_manager import LogManager  # LogManager sınıfını içe aktarın

log_manager = LogManager()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            if user.check_password(password):
                login_user(user)
                session['username'] = user.username
                user.failed_attempts = 0
                db.session.commit()
                
                # Log kaydı: Kullanıcı adı kullanılıyor
                log_manager.log_login(username=user.username, status_code="SUCCESS")

                flash(f'{user.username} adlı kullanıcı giriş yaptı.', 'success')
                return redirect(url_for('main.home'))
            else:
                user.failed_attempts += 1
                db.session.commit()
                
                # Log kaydı: Kullanıcı adı hatalı giriş için kullanılıyor
                log_manager.log_login(username=user.username, status_code="FAILED")

                flash('Kullanıcı adı veya şifre hatalı!', 'danger')
                return render_template('login.html')

        flash('Kullanıcı adı veya şifre hatalı!', 'danger')
        return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:  # Kullanıcı oturumu açık mı kontrol et
        username = current_user.username  # Kullanıcının kullanıcı adı
        session.pop('username', None)

        # Log kaydı (kullanıcı adı kullanılıyor)
        log_manager.log_login(username=username, status_code="LOGOUT")

        flash(f'{username} adlı kullanıcı başarıyla çıkış yaptı.', 'success')
    else:
        flash('Oturum bulunamadı.', 'danger')
    return redirect(url_for('auth.login'))


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            if user.check_password(password):
                if user.role == 'admin':  # Admin kontrolü
                    login_user(user)  # Flask-Login ile oturum başlat
                    session['username'] = user.username  # Kullanıcıyı oturuma ekle



                    flash('Admin girişi başarılı!', 'success')
                    return redirect(url_for('admin.dashboard'))  # Admin paneline yönlendir
                else:
                    flash('Admin girişi için yetkiniz yok.', 'danger')
        
        flash('Kullanıcı adı veya şifre hatalı!', 'danger')
        return render_template('admin_login.html')

    return render_template('admin_login.html')

@auth_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Kullanıcı adı kontrolü
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Kullanıcı adı zaten alınmış!', 'danger')
        else:
            # Admin kullanıcısı oluştur
            new_user = User(username=username, email=email, role='admin')  # Rolü 'admin' olarak ayarlıyoruz
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()


            flash('Admin kullanıcı kaydı başarılı!', 'success')
            return redirect(url_for('auth.admin_login'))  # Admin login sayfasına yönlendir
    return render_template('admin_register.html')

@auth_bp.route('/admin/logout')
def admin_logout():
    username = session.get('username', 'Anonim')  # Kullanıcı adı oturumdan alınır
    user = User.query.filter_by(username=username).first()
    
    if user:
        # Eğer admin çıkışı yapıyorsa, profil durumunu 'passive' olarak ayarlayabilirsiniz
        if user.role == 'admin':

            session.pop('username', None)  # Admin oturumu sonlandırılır
            flash('Başarıyla admin çıkışı yaptınız.', 'success')
        else:
            flash('Admin girişi için yetkiniz yok.', 'danger')
    else:
        flash('Oturum bulunamadı.', 'danger')

    return redirect(url_for('auth.admin_login'))  # Admin login sayfasına yönlendir

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Kullanıcı adı zaten alınmış!', 'danger')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html')
