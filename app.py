from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.User import db, bcrypt, User
from models import Sync# Import db and bcrypt from models
from models import FileHandler
import shutil
import os

app = Flask(__name__)
app.secret_key = 'yedek'

UPLOAD_FOLDER = 'uploads'  # Yükleme dizini
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # İzin verilen dosya türleri

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksimum dosya boyutu 16 MB

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with the app
db.init_app(app)  # Initialize SQLAlchemy with the Flask app
bcrypt.init_app(app)  # Initialize Bcrypt with the Flask app

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()  
        if existing_user:
            flash('Kullanıcı adı zaten alınmış!', 'danger')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password) 
            db.session.add(new_user)
            db.session.commit()

            flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kullanıcıyı veritabanından al
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):  # Kullanıcıyı ve şifreyi kontrol et
            session['username'] = username
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'danger')

    return render_template('login.html')

@app.route('/')
def home_redirect():
    # Eğer kullanıcı giriş yapmışsa, home sayfasına yönlendir
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        # Kullanıcı giriş yapmamışsa, login sayfasına yönlendir
        return redirect(url_for('login'))
    
@app.route('/home')
def home():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template('home.html', user=user)
    else:
        flash('Lütfen giriş yapınız!', 'warning')
        return redirect(url_for('login'))  # Eğer giriş yapılmamışsa login sayfasına yönlendir

@app.route('/profile')
def profile():
    if 'username' in session:
        # Kullanıcı profilini al
        user = User.query.filter_by(username=session['username']).first()
        return render_template('profile.html', user=user)
    else:
        flash('Lütfen giriş yapınız!', 'warning')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('login'))


@app.route('/sync', methods=['GET', 'POST'])
def sync_page():
    if 'username' not in session:
        flash('Lütfen giriş yapınız!', 'warning')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()  # Kullanıcı bilgilerini al

    if request.method == 'POST':
        # Senkronizasyon işlemi başlatılır
        threading.Thread(target=start_sync).start()  # Senkronizasyonu arka planda çalıştırıyoruz
        flash('Senkronizasyon işlemi başlatıldı!', 'success')
        return redirect(url_for('sync_page'))  # Senkronizasyonu başlatan sayfaya yönlendir

    return render_template('sync.html', user=user)  # `user` bilgilerini template'e geçiriyoruz


@app.route('/start_sync', methods=['POST'])
def start_sync():
    # Burada dosya senkronizasyonu işlemi yapılacak
    # Dosya senkronizasyonu başlatılabilir, bu örnek bir işlem olacak
    flash('Senkronizasyon işlemi başladı!', 'success')
    
    # İşlem sonrası senkronizasyon sayfasına yönlendir
    return redirect(url_for('sync_page'))

if __name__ == '__main__':
    app.run(debug=True)
