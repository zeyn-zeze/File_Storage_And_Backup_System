from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user
from models.User import User, db

auth_bp = Blueprint('auth', __name__)

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

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
         login_user(user)  # Flask-Login ile oturum başlat
         session['username'] = user.username  # Kullanıcıyı oturuma ekle
         flash('Giriş başarılı!', 'success')
         return redirect(url_for('main.home'))  # Ana sayfaya yönlendir

            
        flash('Kullanıcı adı veya şifre hatalı!', 'danger')
        return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
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
