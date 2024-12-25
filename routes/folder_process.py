from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash, current_app as app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from models import db
from models.Folder import Folder
from models.File import File
from datetime import datetime
import os
import shutil

folder_bp = Blueprint('folder', __name__)

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_total_size(files):
    """Klasördeki toplam dosya boyutunu hesapla."""
    return sum(file.size for file in files)

def backup_file(file_record):
    """Dosya yedekleme işlemi."""
    backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup', file_record.folder.name)
    os.makedirs(backup_folder, exist_ok=True)
    backup_path = os.path.join(backup_folder, file_record.filename)

    if not os.path.exists(backup_path) or os.path.getmtime(file_record.filepath) > os.path.getmtime(backup_path):
        shutil.copy2(file_record.filepath, backup_path)
        flash(f'Dosya "{file_record.filename}" başarıyla yedeklendi.', 'success')
    else:
        flash(f'Dosya "{file_record.filename}" zaten güncel.', 'info')

@folder_bp.route('/upload/<int:folder_id>', methods=['GET', 'POST'])
@login_required
def upload_file(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    storage_limit = current_user.storage_limit  # Kullanıcının depolama limiti (bytes cinsinden)
    total_size = calculate_total_size(folder.files)

    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            flash("Dosya seçilmedi!", 'danger')
            return redirect(url_for('folder.folder_details', folder_id=folder_id))

        if not allowed_file(file.filename):
            flash("Geçersiz dosya uzantısı!", 'danger')
            return redirect(url_for('folder.folder_details', folder_id=folder_id))

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder.name, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file.save(file_path)
        file_size = os.path.getsize(file_path)

        total_size_mb = total_size / (1024 * 1024)  # Toplam dosya boyutunu MB'ye dönüştür
        file_size_mb = file_size / (1024 * 1024)  # Yeni yüklenen dosyanın boyutunu MB'ye dönüştür
        
        # Toplam boyuta yeni dosyayı ekleyerek sınırı kontrol et
        if total_size_mb + file_size_mb > storage_limit:
            flash("Depolama sınırını aşıyorsunuz!", 'danger')
            os.remove(file_path)  # Yüklenen dosyayı sil
            return redirect(url_for('folder.folder_details', folder_id=folder_id))

        # Veritabanına dosya kaydetme
        try:
            new_file = File(
                owner_id=current_user.user_id,
                filename=filename,
                filepath=file_path,
                created_at=datetime.now(),
                folder_id=folder_id,
                size=file_size,
            )
            
            db.session.add(new_file)
            db.session.commit()

            flash("Dosya başarıyla yüklendi!", 'success')

            # Yedekleme işlemi
            backup_file(new_file)
        except Exception as e:
            db.session.rollback()
            flash(f"Veritabanı hatası: {e}", 'danger')

        return redirect(url_for('folder.folder_details', folder_id=folder_id))

    return render_template('folder_details.html', folder=folder, files=folder.files, total_size=total_size, storage_limit=storage_limit)


@folder_bp.route('/rename_file/<int:file_id>', methods=['GET', 'POST'])
@login_required
def rename_file(file_id):
    file = File.query.get_or_404(file_id)

    if request.method == 'POST':
        new_name = secure_filename(request.form['new_name'])
        if not new_name:
            flash('Geçersiz dosya adı!', 'danger')
            return redirect(url_for('folder.rename_file', file_id=file_id))

        # Dosya adını güncelleme
        old_path = file.filepath
        new_path = os.path.join(os.path.dirname(file.filepath), new_name)

        try:
            os.rename(old_path, new_path)
            file.filename = new_name
            file.filepath = new_path
            db.session.commit()
            flash('Dosya adı başarıyla değiştirildi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Dosya adı değiştirilirken bir hata oluştu: {e}", 'danger')

        return redirect(url_for('folder.folder_details', folder_id=file.folder_id))

    return render_template('rename_file.html', file=file)

@folder_bp.route('/delete_file/<int:file_id>', methods=['GET'])
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    folder_id = file.folder_id

    try:
        os.remove(file.filepath)  # Fiziksel dosyayı sil
        db.session.delete(file)
        db.session.commit()
        flash('Dosya başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Dosya silinirken bir hata oluştu: {e}", 'danger')

    return redirect(url_for('folder.folder_details', folder_id=folder_id))

@folder_bp.route('/folder/<int:folder_id>', methods=['GET', 'POST'])
@login_required
def folder_details(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    files = folder.files
    total_size = calculate_total_size(files)
    storage_limit = current_user.storage_limit

    return render_template('folder_details.html', folder=folder, files=files, total_size=total_size, storage_limit=storage_limit)

@folder_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_folder():
    if request.method == 'POST':
        folder_name = secure_filename(request.form['folder_name'])
        if not folder_name:
            flash('Geçersiz klasör adı!', 'danger')
            return redirect(url_for('folder.create_folder'))

        try:
            new_folder = Folder(name=folder_name, owner_id=current_user.user_id, created_at=datetime.now())
            db.session.add(new_folder)
            db.session.commit()
            flash(f'Klasör "{folder_name}" başarıyla oluşturuldu.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Klasör oluşturulurken bir hata oluştu: {e}", 'danger')

        return redirect(url_for('folder.list_folders'))

    return render_template('create_folder.html')

@folder_bp.route('/delete_folder/<int:folder_id>', methods=['GET'])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)

    try:
        # Klasördeki dosyaları sil
        for file in folder.files:
            os.remove(file.filepath)
            db.session.delete(file)

        db.session.delete(folder)
        db.session.commit()
        flash(f'Klasör "{folder.name}" başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Klasör silinirken bir hata oluştu: {e}", 'danger')

    return redirect(url_for('folder.list_folders'))


@folder_bp.route('/folders', methods=['GET'])
@login_required
def list_folders():
    # Veritabanından kullanıcıya ait tüm klasörleri alıyoruz
    folders = Folder.query.filter_by(owner_id=current_user.user_id).all()
    return render_template('create_folder.html', folders=folders)


@folder_bp.route('/download_file/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Ensure the file exists and get its path
    file_path = file.filepath
    
    if not os.path.exists(file_path):
        flash('Dosya bulunamadı.', 'danger')
        return redirect(url_for('folder.folder_details', folder_id=file.folder_id))
    
    # Send the file to the user
    return send_file(file_path, as_attachment=True, download_name=file.filename)


@folder_bp.route('/move_file/<int:file_id>', methods=['GET', 'POST'])
@login_required
def move_file(file_id):
    file = File.query.get_or_404(file_id)
    
    if request.method == 'POST':
        new_folder_id = request.form.get('new_folder_id')  # Yeni klasör ID'si alınır
        new_folder = Folder.query.get_or_404(new_folder_id)
        
        # Dosyayı taşıma işlemi (veritabanındaki klasör ilişkisini güncelle)
        file.folder_id = new_folder.id
        db.session.commit()
        
        flash('Dosya başarıyla taşındı!', 'success')
        return redirect(url_for('folder.folder_details', folder_id=new_folder.id))
    
    # Kullanıcının sahip olduğu tüm klasörleri al
    folders = Folder.query.filter_by(owner_id=current_user.user_id).all()
    return render_template('move_file.html', file=file, folders=folders)
