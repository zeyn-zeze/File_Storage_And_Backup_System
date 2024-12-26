from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash
from flask_login import current_user, login_required
from islemler.log_manager import LogManager as log_manager
from models import db
from models.Team import Team
from models.TeamMember import TeamMember
from models.Post import Post
from models.File import File
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from models.User import User
from utils.notifc import send_file_upload_notification, send_new_post_notification, send_post_rename_notification, send_team_creation_notification, send_team_deletion_notification, send_post_deletion_notification
from utils.utils import save_log

team_bp = Blueprint('team', __name__)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','docx'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@team_bp.route('/teams', methods=['GET'])
@login_required
def list_teams():
    # Query teams where the current user is a member (either as owner or team member)
    teams = db.session.query(Team).join(TeamMember).filter(
        (TeamMember.user_id == current_user.user_id)
    ).all()
    return render_template('teams.html', teams=teams)


@team_bp.route('/teams/create', methods=['GET', 'POST'])
@login_required
def create_team():
    if request.method == 'POST':
        team_name = request.form['name']
        members = request.form.getlist('members')

        # Yeni takım oluştur
        new_team = Team(
            owner_id=current_user.user_id,  # Şu anki kullanıcı oluşturdu
            name=team_name,
            created_at=datetime.now()
        )
        db.session.add(new_team)
        db.session.commit()

        # Takımı oluşturan kullanıcı team_manager oldu
        admin_member = TeamMember(
            team_id=new_team.id,
            user_id=current_user.user_id,
            role='team_manager',
            created_at=datetime.now()
        )
        db.session.add(admin_member)

        # Seçilen takım üyelerini kullanıcı ID'lerinden çek
        member_usernames = []
        if members:
            for member_id in members:
                if member_id:
                    try:
                        member_id = int(member_id)
                        team_member = TeamMember(
                            team_id=new_team.id,
                            user_id=member_id,
                            role='member',
                            created_at=datetime.now()
                        )
                        db.session.add(team_member)

                        # Takım üyelerini al
                        member_user = User.query.get(member_id)
                        if member_user:
                            member_usernames.append(member_user.username)
                        
                        # Bildirim yolla
                        send_team_creation_notification(new_team, member_user, current_user)
                    except ValueError:
                        continue

        db.session.commit()  # Database'e takım kaydet

        # Loglama
        log_manager.log_team_creation(
            username=current_user.username,
            team_name=team_name,
            member_usernames=member_usernames,
            status_code="SUCCESS"
        )

        flash('Yeni takım başarıyla oluşturuldu!', 'success')
        return redirect(url_for('team.list_teams'))

    users = User.query.filter(User.user_id != current_user.user_id).all()
    return render_template('create_team.html', users=users)


#TAKIM SAYFASINI DÖNDÜR

@team_bp.route('/teams/<int:team_id>', methods=['GET', 'POST'])
@login_required
def team_page(team_id):
    team = Team.query.get_or_404(team_id)
    team_members = TeamMember.query.filter_by(team_id=team.id).all()

    if request.method == 'POST':
        content = request.form.get('content')
        file_id = request.form.get('file_id')

        new_post = Post(
            team_id=team.id,
            user_id=current_user.user_id,
            content=content,
            file_id=file_id
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Gönderi başarıyla eklendi!", "success")
        return redirect(url_for('team.team_page', team_id=team_id))

    posts = Post.query.filter_by(team_id=team_id).all()
    files = File.query.filter_by(owner_id=current_user.user_id).all()

    return render_template('team_page.html', 
                           team=team, 
                           posts=posts, 
                           files=files,
                           team_members=team_members)

                         

@team_bp.route('/delete_team/<int:team_id>', methods=['POST'])
@login_required
def delete_team(team_id):
    # Takımı al
    team = Team.query.get_or_404(team_id)

    # Kullanıcının takım üzerindeki rolünü kontrol et
    admin = TeamMember.query.filter_by(team_id=team_id, user_id=current_user.user_id, role='team_manager').first()

    # Yalnızca 'team_manager' rolüne sahip kullanıcıların silmesine izin ver
    if not admin:
        flash('Bu işlemi yapmak için yetkiniz yok.', 'danger')
        return redirect(url_for('team.team_page', team_id=team_id))

    try:
        # Takım silinmeden önce üyelerine bildirim gönder
        send_team_deletion_notification(team, current_user)

        # Log kaydını yap
        log_message = f"Takım silindi: {team.name} (Takım sahibi: {current_user.username})"
        save_log("team", log_message)

        # Takımı sil
        db.session.delete(team)
        db.session.commit()

        flash('Takım başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Takım silinirken bir hata oluştu: {str(e)}", 'danger')

    return redirect(url_for('team.list_teams'))


@team_bp.route('/teams/<int:team_id>/upload', methods=['POST'])
@login_required
def upload_post(team_id):
    team = Team.query.get_or_404(team_id)

    # Kullanıcının takım üyesi olup olmadığını kontrol et
    if not TeamMember.query.filter_by(team_id=team.id, user_id=current_user.user_id).first():
        flash('Bu takıma üye değilsiniz!', 'danger')
        return redirect(url_for('team.team_page', team_id=team.id))

    # Dosya yükleme işlemi
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Yeni dosyayı veritabanına kaydet
        new_file = File(
            owner_id=current_user.user_id,
            filename=filename,
            filepath=filepath,
            team_id=team.id,
        )
        db.session.add(new_file)
        db.session.commit()

        # **Loglama**
        log_manager.log_file_upload(
            username=current_user.username,
            file_name=filename,
            file_size=os.path.getsize(filepath),
            upload_dir=UPLOAD_FOLDER,
            status_code="SUCCESS"
        )

        # Dosya yükleme sonrası bildirim gönder
        send_file_upload_notification(team, current_user, filename)

        flash('Dosya başarıyla yüklendi!', 'success')
        return redirect(url_for('team.team_page', team_id=team.id))

    # Loglama: Başarısız dosya yükleme
    if file:
        log_manager.log_file_upload(
            username=current_user.username,
            file_name=file.filename,
            file_size=0,
            upload_dir=UPLOAD_FOLDER,
            status_code="FAILED"
        )

    flash('Geçersiz dosya türü!', 'danger')
    return redirect(url_for('team.team_page', team_id=team.id))



@team_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Ensure the user is authorized to delete the post
    team_member = TeamMember.query.filter_by(team_id=post.team_id, user_id=current_user.user_id).first()
    
    if not team_member or (team_member.role != 'team_manager' and post.user_id != current_user.user_id):
        flash('Bu gönderiyi silmeye yetkiniz yok.', 'danger')
        return redirect(url_for('team.team_page', team_id=post.team_id))

    # Send notification before deleting the post
    send_post_deletion_notification(post, current_user)

    # Log the post deletion
    log_message = f"Post silindi: {post.content} | Takım: {post.team.name} | Silen: {current_user.username}"
    save_log("tean", log_message)  # Post silme işlemi için log kaydını yapıyoruz

    # Delete the post (not the associated file, just the post)
    db.session.delete(post)
    db.session.commit()

    flash('Gönderi başarıyla silindi.', 'success')
    return redirect(url_for('team.team_page', team_id=post.team_id))


@team_bp.route('/teams/<int:team_id>/create_post', methods=['GET', 'POST'])
@login_required
def create_post(team_id):
    team = Team.query.get_or_404(team_id)

    # Kullanıcının takım üyesi olup olmadığını kontrol et
    team_member = TeamMember.query.filter_by(team_id=team.id, user_id=current_user.user_id).first()
    if not team_member:
        flash("Bu takıma ait değilsiniz!", "danger")
        return redirect(url_for('team.team_page', team_id=team_id))

    if request.method == 'POST':
        content = request.form.get('content')
        file_id = request.form.get('file_id')

        # Dosya adı için file_id kontrolü
        file_name = None
        if file_id:
            file = File.query.get(file_id)
            if file:
                file_name = file.filename

        # İçerik doğrulaması
        if not content:
            flash("Gönderi içeriği boş olamaz!", "danger")
            return render_template('gonderi.html', team=team, files=files)

        # Yeni gönderiyi oluştur
        new_post = Post(
            team_id=team.id,
            user_id=current_user.user_id,
            content=content,
            file_id=file_id if file_id else None,
            created_at=datetime.now()  # UTC zamanını kullan
        )
        db.session.add(new_post)
        db.session.commit()

        # Bildirim gönderme
        send_new_post_notification(new_post)

        # **Loglama işlemi**
        log_manager.log_post_creation(
            username=current_user.username,
            team_name=team.name,
            content=content,
            attached_file=file_name,
            status_code="SUCCESS"
        )

        flash("Gönderi başarıyla oluşturuldu!", "success")
        return redirect(url_for('team.team_page', team_id=team.id))

    # Kullanıcının dosyalarını al
    files = File.query.filter_by(owner_id=current_user.user_id).all()
    return render_template('gonderi.html', team=team, files=files)



@team_bp.route('/teams/open/<int:post_id>', methods=['GET'])
@login_required
def open_post(post_id):
    # Postu ve dosyasını getir
    post = Post.query.get_or_404(post_id)

    # Gönderinin ait olduğu takımı bul
    team = Team.query.get_or_404(post.team_id)

    # Kullanıcı bu takımın bir üyesi mi diye kontrol et
    team_member = TeamMember.query.filter_by(team_id=team.id, user_id=current_user.user_id).first()
    
    if not team_member:
        flash('Bu takıma ait değilsiniz!', 'danger')
        return redirect(url_for('team.team_page', team_id=team.id))

    # Eğer postun bir dosyası varsa, dosyayı aç
    if post.file_id:
        file_record = File.query.get_or_404(post.file_id)
        file_path = file_record.filepath  # Dosyanın dosya yolu

        if os.path.exists(file_path):
            # Dosyayı tarayıcıda aç (indirilen dosya yerine)
            return send_file(file_path, as_attachment=False)
        else:
            flash('Dosya sunucuda bulunamadı', 'danger')
            return redirect(url_for('team.team_page', team_id=post.team_id))

    flash('Bu gönderiye ait dosya yok', 'danger')
    return redirect(url_for('team.team_page', team_id=post.team_id))

@team_bp.route('/post/rename/<int:post_id>', methods=['POST'])
@login_required
def rename_post(post_id):
    post = Post.query.get(post_id)  # Veritabanından postu al

    if post:
        new_name = request.form['new_name']  # Yeni dosya adını al
        new_name = secure_filename(new_name)  # Yeni dosya adını güvenli hale getir

        # Post'a ait dosya id'si ile dosyayı al
        file = File.query.get(post.file_id)  # Post'a ait dosya

        if file:
            # Eski dosya yolunu al
            old_file_path = file.filepath
            new_file_path = os.path.join(os.path.dirname(old_file_path), new_name)  # Yeni dosya yolunu oluştur

            try:
                # Dosya adını değiştirme işlemi
                os.rename(old_file_path, new_file_path)

                # Veritabanındaki dosya yolunu güncelle
                file.filename = new_name
                file.filepath = new_file_path  # Dosyanın yeni yolunu güncelle
                db.session.commit()  # Veritabanına kaydet

                # Post içeriğini güncelle (dosya adını değiştirdik)
                post.content = new_name  # Post içeriği yeni dosya adıyla güncelleniyor
                db.session.commit()

                # Bildirim gönderme işlemi
                send_post_rename_notification(post, current_user)

                # Log kaydı ekleme
                log_message = f"Post ID: {post.id} için dosya adı değiştirildi: Eski Adı: {old_file_path}, Yeni Adı: {new_file_path}"
                save_log("takım", log_message)  # Dosya adı değiştirme işlemi için log kaydını yapıyoruz

                flash('Gönderi adı başarıyla değiştirildi!', 'success')
                return redirect(url_for('team.team_page', team_id=post.team_id))

            except Exception as e:
                flash(f"Gönderi adı değiştirilirken bir hata oluştu: {e}", 'danger')
                return redirect(url_for('team.team_page', team_id=post.team_id))

        else:
            flash("Dosya bulunamadı.", 'danger')
            return redirect(url_for('team.team_page', team_id=post.team_id))

    else:
        flash('Gönderi bulunamadı.', 'danger')
        return redirect(url_for('team.team_page', team_id=post.team_id))


@team_bp.route('/team/<int:team_id>/info')
@login_required
def team_info(team_id):
    team = Team.query.get_or_404(team_id)  # Get the team by ID
    owner = User.query.get_or_404(team.owner_id)  # Fetch the owner based on the owner_id

    # Fetch the members, join TeamMember and User to get member details
    members = db.session.query(User, TeamMember).join(TeamMember).filter(TeamMember.team_id == team.id).all()

    return render_template('team_info.html', team=team, owner=owner, members=members)

