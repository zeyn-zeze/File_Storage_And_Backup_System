from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db
from models.Team import Team
from models.TeamMember import TeamMember
from models.Post import Post
from models.File import File
from datetime import datetime

from models.User import User

team_bp = Blueprint('team', __name__)


@team_bp.route('/teams', methods=['GET'])
@login_required
def list_teams():
    # Kullanıcının sahip olduğu takımlar
    teams = Team.query.filter_by(owner_id=current_user.user_id).all()
    
    # Takımların sadece temel bilgilerini listele
    return render_template('teams.html', teams=teams)


@team_bp.route('/teams/create', methods=['GET', 'POST'])
@login_required
def create_team():
    if request.method == 'POST':
        team_name = request.form['name']
        members = request.form.getlist('members')  # Seçilen üyeler (list olarak)

        # Yeni bir takım oluştur
        new_team = Team(
            owner_id=current_user.user_id,  # Takım sahibi şu anki kullanıcı
            name=team_name,
            created_at=datetime.now()
        )
        db.session.add(new_team)
        db.session.commit()  # Takımı veritabanına kaydet

        # Takım sahibini 'team_manager' rolüyle ekleme
        admin_member = TeamMember(
            team_id=new_team.id,
            user_id=current_user.user_id,  # Takım sahibi olarak user_id
            role='team_manager',  # Yöneticinin rolü
            created_at=datetime.now()
        )
        db.session.add(admin_member)

        # Seçilen üyeleri eklemek
        if members:  # Eğer üyeler listesi boş değilse
            for member_id in members:
                if member_id:  # Eğer geçerli bir member_id varsa
                    try:
                        member_id = int(member_id)  # ID'nin int olduğunu kontrol et
                        # Seçilen üyeyi 'member' olarak ekle
                        team_member = TeamMember(
                            team_id=new_team.id,
                            user_id=member_id,  # Seçilen üyelerin ID'leri
                            role='member',  # Üye rolü
                            created_at=datetime.now()
                        )
                        db.session.add(team_member)
                    except ValueError:
                        # Eğer member_id geçerli bir tam sayı değilse, bu kullanıcıyı ekleme
                        continue

        db.session.commit()  # Tüm üyeleri ekle ve işlemi kaydet
        flash('Yeni takım başarıyla oluşturuldu!', 'success')
        return redirect(url_for('team.list_teams'))

    # Kullanıcı listesini alma (kendisi hariç)
    users = User.query.filter(User.user_id != current_user.user_id).all()
    return render_template('create_team.html', users=users)







# Takım sayfası
@team_bp.route('/teams/<int:team_id>', methods=['GET', 'POST'])
@login_required
def team_page(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Takıma ait üyeleri çek
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
    
    # Kullanıcının sadece bu takıma ait üyelerle etkileşime girmesini sağla
    return render_template('team_page.html', 
                           team=team, 
                           posts=posts, 
                           files=files,
                           team_members=team_members)



@team_bp.route('/delete_team/<int:team_id>', methods=['POST'])
@login_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    admin = TeamMember.query.filter_by(team_id=team_id, user_id=current_user.user_id, role='team_manager').first()

    if not admin:
        flash('Bu işlemi yapmak için yetkiniz yok.', 'danger')
        return redirect(url_for('team.team_page', team_id=team_id))

    # Takımı silme işlemleri
    db.session.delete(team)
    db.session.commit()
    flash('Takım başarıyla silindi.', 'success')
    return redirect(url_for('team.list_teams'))
