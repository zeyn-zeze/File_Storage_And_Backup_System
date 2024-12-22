import os
import shutil
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash, current_app as app
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

@sync_bp.route('/backup')
@login_required
def backup_files():
  
    # İzin verilen dosyalar
    files = File.query.filter_by(owner_id=current_user.user_id).all()
    # Şablona dosyalar gönderiliyor
    return render_template('backup.html', files=files)


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


            flash('File successfully uploaded and backed up')
            return redirect(url_for('sync.upload_file'))
    return render_template('upload.html')

@sync_bp.route('/open/<file_id>', methods=['GET'])
@login_required
def open_file(file_id):
    # Veritabanından dosya kaydını al
    file_record = File.query.filter_by(id=file_id, owner_id=current_user.user_id).first()
    
    if file_record:
        # Dosya yolunu al
        file_path = file_record.filepath  # Assuming 'filepath' stores the absolute path
        
        # Dosyanın mevcut olup olmadığını kontrol et
        if os.path.exists(file_path):
            # Dosyayı tarayıcıda açmak için gönder
            return send_file(file_path, as_attachment=False)  # Dosyayı tarayıcıda açar
        else:
            flash('File not found on the server', 'danger')
            return redirect(url_for('sync.upload_file'))
    else:
        flash('File not found in database', 'danger')
        return redirect(url_for('sync.backup_files'))



@sync_bp.route('/delete/<file_id>', methods=['GET'])
@login_required
def delete_file(file_id):
    try:
        # Veritabanında dosyanın kaydını buluyoruz
        file_record = File.query.filter_by(id=file_id, owner_id=current_user.user_id).first()
        
        if file_record:
            # Dosya yolunu belirliyoruz
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record.filename)
            
            # Dosyanın varlığını kontrol et ve sil
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                flash(f'Dosya bulunamadı: {file_path}', 'danger')

            # Yedek dosyayı silme işlemi
            backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup')
            backup_path = os.path.join(backup_folder, file_record.filename)
            if os.path.exists(backup_path):
                os.remove(backup_path)
            else:
                flash(f'Yedek dosya bulunamadı: {backup_path}', 'danger')

            # Veritabanındaki dosya kaydını siliyoruz
            db.session.delete(file_record)
            db.session.commit()

            flash('File successfully deleted')
        else:
            flash('File not found or you are not authorized to delete this file', 'danger')
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')
    
    # Dosya silindikten sonra yükleme sayfasına yönlendiriyoruz
    return redirect(url_for('sync.backup_files'))




