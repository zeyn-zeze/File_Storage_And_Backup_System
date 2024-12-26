from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash, current_app as app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from models import db
from models.Folder import Folder
from models.File import File
from datetime import datetime
import os
from utils.utils import save_log 




folder_bp = Blueprint('folder', __name__)

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_total_size(folders):
    total_size = 0
    for folder in folders:
        if hasattr(folder, 'files'):  # Klasörde `files` ilişkisi var mı kontrol edin
            total_size += sum(file.size for file in folder.files)  # Dosya boyutlarını topla
    return total_size

        
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



            
            save_log("folder", f"Dosya başarıyla yüklendi: {new_file.filename} - {datetime.now()}")

        except Exception as e:
            db.session.rollback()
            flash(f"Veritabanı hatası: {e}", 'danger')
            save_log("anormallik", f"Dosya yüklenirken bir hata oluştu: {e}")

        return redirect(url_for('folder.folder_details', folder_id=folder_id))

    return render_template('folder_details.html', folder=folder, files=folder.files, total_size=total_size, storage_limit=storage_limit)




@folder_bp.route('/rename_file/<int:file_id>', methods=['POST'])
@login_required
def rename_file(file_id):
    file = File.query.get(file_id)  # Veritabanından dosyayı al
    if file:
        new_name = request.form['new_name']  # Yeni dosya adını al
        new_name = secure_filename(new_name)  # Yeni dosya adını güvenli hale getir

        # Klasör yolunu al
        folder = Folder.query.get(file.folder_id)
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder.name)

        # Eski ve yeni dosya yolunu oluştur
        old_file_path = os.path.join(folder_path, file.filename)
        new_file_path = os.path.join(folder_path, new_name)

        try:
            # Dosya adını değiştirme işlemi
            os.rename(old_file_path, new_file_path)

            # Veritabanındaki dosya adını güncelle
            file.filename = new_name
            file.filepath = new_file_path  # Dosyanın yeni yolunu güncelle
            db.session.commit()  # Veritabanına kaydet

            # Loglama
            save_log("folder", f" {file.filename}Dosya adı değiştirildi: {file.filename} - {datetime.now()}")

            flash('Dosya adı başarıyla değiştirildi!', 'success')
            return redirect(request.referrer)  # Aynı sayfaya geri döndür

        except Exception as e:
            flash(f"Dosya adı değiştirilirken bir hata oluştu: {e}", 'danger')
            save_log("folder", f"Dosya adı değiştirilirken bir hata oluştu: {e}")
            return redirect(request.referrer)

    else:
        flash('Dosya bulunamadı.', 'danger')
        return redirect(request.referrer)


@folder_bp.route('/delete_file/<int:file_id>', methods=['GET'])
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    folder_id = file.folder_id

    try:
        os.remove(file.filepath)  # Remove the physical file
        db.session.delete(file)
        db.session.commit()

        # Loglama
        save_log("folder", f"Dosya silindi: {file.filename} - {datetime.now()}")

        flash('Dosya başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Dosya silinirken bir hata oluştu: {e}", 'danger')
        save_log("anormallik", f"Dosya silinirken bir hata oluştu: {e}")

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
    total_size = calculate_total_size(folders)
    storage_limit = current_user.storage_limit
    return render_template('create_folder.html', folders=folders,total_size=total_size,storage_limit=storage_limit)


@folder_bp.route('/download_file/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Ensure the file exists and get its path
    file_path = file.filepath
    
    if not os.path.exists(file_path):
        flash('Dosya bulunamadı.', 'danger')
        
        # Log the failed attempt to download the file
        save_log("anormallik", f"Dosya bulunamadı: {file.filename} - {datetime.now()}")
        
        return redirect(url_for('folder.folder_details', folder_id=file.folder_id))
    
    # Log the successful download attempt
    save_log("folder", f"Dosya indirildi: {file.filename} - {datetime.now()}")
    
    # Send the file to the user
    return send_file(file_path, as_attachment=True, download_name=file.filename)


@folder_bp.route('/move_file/<int:file_id>', methods=['GET', 'POST'])
@login_required
def move_file(file_id):
    # Dosya bilgisi alınır
    file = File.query.get_or_404(file_id)
    
    # Kullanıcıya ait klasörleri al (dosyanın mevcut olduğu klasör hariç)
    folders = Folder.query.filter_by(owner_id=current_user.user_id, id = file.id).all()

    if request.method == 'POST':
        # Kullanıcının seçtiği klasör ID'sini al
        selected_folder_id = request.form.get('folder')
        selected_folder = Folder.query.get(selected_folder_id)

        # Seçilen klasörün geçerli olup olmadığını kontrol et
        if selected_folder and selected_folder.owner_id == current_user.user_id:
            # Eski ve yeni dosya yolu
            old_path = file.filepath
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], selected_folder.name, file.filename)

            try:
                # Yeni klasör yoksa oluştur
                os.makedirs(os.path.dirname(new_path), exist_ok=True)

                # Dosyayı taşı
                os.rename(old_path, new_path)

                # Veritabanını güncelle
                file.folder_id = selected_folder.id
                file.filepath = new_path
                db.session.commit()

                # Loglama
                save_log("folder", f"Dosya taşındı: {file.filename} -> {selected_folder.name}")
                flash('Dosya başarıyla taşındı.', 'success')
            except Exception as e:
                db.session.rollback()
                save_log("anormallik", f"Dosya taşınırken hata: {e}")
                flash(f"Dosya taşınırken bir hata oluştu: {e}", 'danger')
            
            return redirect(url_for('folder.folder_details', folder_id=selected_folder.id))
        else:
            flash('Geçersiz klasör seçimi.', 'danger')

    # GET isteği sırasında klasör listesini ve dosya bilgisini şablona gönder
    return render_template('file_details.html', file=file, folders=folders)



@folder_bp.route('/file_status', methods=['GET'])
@login_required
def file_status():
    files = File.query.filter_by(owner_id=current_user.user_id).all()
    return render_template('file_status.html', files=files)




