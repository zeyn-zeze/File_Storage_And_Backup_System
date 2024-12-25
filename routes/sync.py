import os
import shutil
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash, current_app as app
from werkzeug.utils import secure_filename
from datetime import datetime
from models.File import File
from models import db 


# Blueprint tanımı
sync_bp = Blueprint('sync', __name__)

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Yedekleme sayfası
@sync_bp.route('/backup')
@login_required
def backup_files():
    files = File.query.filter_by(owner_id=current_user.user_id).all()
    return render_template('backup.html', files=files)

# Dosya yükleme
@sync_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Dosya veritabanına kaydediliyor
            new_file = File(
                owner_id=current_user.user_id,
                filename=filename,
                filepath=file_path,
                created_at=datetime.now()
            )
            db.session.add(new_file)
            db.session.commit()

            # Yedekleme işlemi
            backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup')
            os.makedirs(backup_folder, exist_ok=True)  # Yedekleme klasörünü oluştur
            backup_path = os.path.join(backup_folder, filename)

            # Eğer yedek dosya yoksa veya kaynak dosya daha yeni ise, yedekleme yap
            if not os.path.exists(backup_path) or os.path.getmtime(file_path) > os.path.getmtime(backup_path):
                shutil.copy2(file_path, backup_path)  # Dosyayı yedekleme

            flash('File successfully uploaded and backed up', 'success')
            return redirect(url_for('sync.upload_file'))
    return render_template('upload.html')


# Dosya açma
@sync_bp.route('/open/<int:file_id>', methods=['GET'])
@login_required
def open_file(file_id):
    file_record = File.query.filter_by(id=file_id, owner_id=current_user.user_id).first()
    if file_record:
        file_path = file_record.filepath
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=False)
        else:
            flash('File not found on the server', 'danger')
            return redirect(url_for('sync.upload_file'))
    else:
        flash('File not found in database', 'danger')
        return redirect(url_for('sync.backup_files'))

@sync_bp.route('/delete/<int:file_id>', methods=['GET'])
@login_required
def delete_file(file_id):
    try:
        # Fetch the file record from the database
        file_record = File.query.filter_by(id=file_id, owner_id=current_user.user_id).first()
        print(f"File ID: {file_id}")  # Add this print statement for debugging

        if file_record:
            # Get the file paths
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record.filename)
            backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup')
            backup_path = os.path.join(backup_folder, file_record.filename)

            print(f"Deleting file: {file_path}")
            print(f"Deleting backup file: {backup_path}")

            # Check and delete original file
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} deleted.")
            else:
                flash(f'Dosya bulunamadı: {file_path}', 'danger')

            # Check and delete backup file
            if os.path.exists(backup_path):
                os.remove(backup_path)
                print(f"Backup {backup_path} deleted.")
            else:
                flash(f'Yedek dosya bulunamadı: {backup_path}', 'danger')

            # Delete file record from the database
            db.session.delete(file_record)
            db.session.commit()

            flash('File successfully deleted', 'success')
        else:
            flash('File not found or unauthorized', 'danger')

    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')
        print(f"Error: {str(e)}")

    return redirect(url_for('sync.backup_files'))

# Yedekleme işlemi (otomatik yedekleme modülü)
@sync_bp.route('/auto_backup', methods=['POST'])
@login_required
def auto_backup():
    backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup')
    os.makedirs(backup_folder, exist_ok=True)

    user_files = File.query.filter_by(owner_id=current_user.user_id).all()
    for file_record in user_files:
        source_path = file_record.filepath
        backup_path = os.path.join(backup_folder, file_record.filename)

        # Yedekleme yapılması gereken dosyayı kontrol et
        if not os.path.exists(backup_path) or os.path.getmtime(source_path) > os.path.getmtime(backup_path):
            shutil.copy2(source_path, backup_path)

    flash('All files successfully backed up', 'success')
    return redirect(url_for('sync.backup_files'))
