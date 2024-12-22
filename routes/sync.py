import os
import shutil
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app
from werkzeug.utils import secure_filename
from flask import send_from_directory
from models import db  # Veritabanı modeline erişim
from models.File import File  # File modelini import ettik
from datetime import datetime

sync_bp = Blueprint('sync', __name__)

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Yedekleme işlemi
def backup_file(filename):
    upload_folder = app.config['UPLOAD_FOLDER']
    backup_folder = os.path.join(upload_folder, 'backup')
    
    # Yedekleme klasörü yoksa oluşturuluyor
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    file_path = os.path.join(upload_folder, filename)
    backup_path = os.path.join(backup_folder, filename)
    
    shutil.copy(file_path, backup_path)

@sync_bp.route('/upload', methods=['GET', 'POST'])
@login_required  # Bu decorator, oturum açmamış kullanıcıları login sayfasına yönlendirecektir
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Dosya veritabanına kaydediliyor
            new_file = File(
                owner_id=current_user.user_id,  # Giriş yapan kullanıcının ID'si
                filename=filename,
                filepath=file_path,
                created_at=datetime.now()
            )
            db.session.add(new_file)
            db.session.commit()

            # Yedekleme işlemi
            backup_file(filename)

            flash('File successfully uploaded and backed up')
            return redirect(url_for('sync.upload_file'))
    return render_template('upload.html')

@sync_bp.route('/download/<filename>', methods=['GET'])
@login_required  # Dosya sadece oturum açmış kullanıcılar tarafından indirilebilir
def download_file(filename):
    # Kullanıcının dosyayı indirmeye yetkili olup olmadığını kontrol et
    file_record = File.query.filter_by(filename=filename, owner_id=current_user.id).first()
    if file_record:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        flash('You are not authorized to download this file', 'danger')
        return redirect(url_for('sync.upload_file'))

@sync_bp.route('/delete/<filename>', methods=['GET'])
@login_required  # Dosya sadece oturum açmış kullanıcılar tarafından silinebilir
def delete_file(filename):
    try:
        file_record = File.query.filter_by(filename=filename, owner_id=current_user.id).first()
        if file_record:
            # Dosya sisteminden sil
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.remove(file_path)

            # Yedek dosyayı da sil
            backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup')
            backup_path = os.path.join(backup_folder, filename)
            if os.path.exists(backup_path):
                os.remove(backup_path)

            # Veritabanındaki dosyayı sil
            db.session.delete(file_record)
            db.session.commit()

            flash('File successfully deleted')
        else:
            flash('File not found or you are not authorized to delete this file', 'danger')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')
    return redirect(url_for('sync.upload_file'))
