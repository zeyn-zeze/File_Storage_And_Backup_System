from flask import Blueprint, render_template, request, redirect, send_file, url_for, flash
from flask_login import current_user, login_required
from models import db
from models.Team import Team
from models.TeamMember import TeamMember
from models.Post import Post
from models.File import File
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from models.User import User

team_bp = Blueprint('team', __name__)

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'txt', 'csv'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# List teams owned by the current user
@team_bp.route('/teams', methods=['GET'])
@login_required
def list_teams():
    teams = Team.query.filter_by(owner_id=current_user.user_id).all()
    return render_template('teams.html', teams=teams)

# Create a new team
@team_bp.route('/teams/create', methods=['GET', 'POST'])
@login_required
def create_team():
    if request.method == 'POST':
        team_name = request.form['name']
        members = request.form.getlist('members')  # Selected members list

        # Create a new team and add the owner (current user)
        new_team = Team(
            owner_id=current_user.user_id,
            name=team_name,
            created_at=datetime.now()
        )
        db.session.add(new_team)
        db.session.commit()

        # Add the owner as a team manager
        admin_member = TeamMember(
            team_id=new_team.id,
            user_id=current_user.user_id,
            role='team_manager',
            created_at=datetime.now()
        )
        db.session.add(admin_member)

        # Add selected members to the team
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
                    except ValueError:
                        continue  # Ignore invalid member_id

        db.session.commit()  # Commit the transaction
        flash('Yeni takım başarıyla oluşturuldu!', 'success')
        return redirect(url_for('team.list_teams'))

    # Fetch all users (excluding the current user)
    users = User.query.filter(User.user_id != current_user.user_id).all()
    return render_template('create_team.html', users=users)

# Team page displaying posts and files
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

# Delete a team
@team_bp.route('/delete_team/<int:team_id>', methods=['POST'])
@login_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    admin = TeamMember.query.filter_by(team_id=team_id, user_id=current_user.user_id, role='team_manager').first()

    if not admin:
        flash('Bu işlemi yapmak için yetkiniz yok.', 'danger')
        return redirect(url_for('team.team_page', team_id=team_id))

    db.session.delete(team)
    db.session.commit()
    flash('Takım başarıyla silindi.', 'success')
    return redirect(url_for('team.list_teams'))

# Upload a file for a team
@team_bp.route('/teams/<int:team_id>/upload', methods=['POST'])
@login_required
def upload_post(team_id):
    team = Team.query.get_or_404(team_id)

    # Ensure user is a member of the team
    if not TeamMember.query.filter_by(team_id=team.id, user_id=current_user.user_id).first():
        flash('You are not a member of this team!', 'danger')
        return redirect(url_for('team.team_page', team_id=team.id))

    # Handle file upload
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        new_file = File(
            owner_id=current_user.user_id,
            filename=filename,
            filepath=filepath,
            team_id=team.id,
        )
        db.session.add(new_file)
        db.session.commit()

        flash('File uploaded successfully!', 'success')
        return redirect(url_for('team.team_page', team_id=team.id))

    flash('Invalid file type!', 'danger')
    return redirect(url_for('team.team_page', team_id=team.id))

@team_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Ensure the user is authorized to delete the post
    # A team manager or the user who created the post can delete it
    team_member = TeamMember.query.filter_by(team_id=post.team_id, user_id=current_user.user_id).first()
    
    if not team_member or (team_member.role != 'team_manager' and post.user_id != current_user.user_id):
        flash('Bu gönderiyi silmeye yetkiniz yok.', 'danger')
        return redirect(url_for('team.team_page', team_id=post.team_id))

    # If the post has an associated file, delete it as well
    if post.file_id:
        file = File.query.get_or_404(post.file_id)
        db.session.delete(file)

    # Now delete the post
    db.session.delete(post)
    db.session.commit()

    flash('Gönderi başarıyla silindi.', 'success')
    return redirect(url_for('team.team_page', team_id=post.team_id))


# Create a new post for a team
@team_bp.route('/teams/<int:team_id>/create_post', methods=['GET', 'POST'])
@login_required
def create_post(team_id):
    team = Team.query.get_or_404(team_id)

    # Ensure the user is part of the team
    team_member = TeamMember.query.filter_by(team_id=team.id, user_id=current_user.user_id).first()
    if not team_member:
        flash("Bu takıma ait değilsiniz!", "danger")
        return redirect(url_for('team.team_page', team_id=team_id))

    if request.method == 'POST':
        content = request.form.get('content')
        file_id = request.form.get('file_id')

        # Validation for content
        if not content:
            flash("Gönderi içeriği boş olamaz!", "danger")
            return render_template('gonderi.html', team=team, files=files)

        # Creating a new post
        new_post = Post(
            team_id=team.id,
            user_id=current_user.user_id,
            content=content,
            file_id=file_id if file_id else None,
            created_at=datetime.now()  # Use UTC time
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Gönderi başarıyla oluşturuldu!", "success")
        return redirect(url_for('team.team_page', team_id=team.id))

    # Get user's files for the form
    files = File.query.filter_by(owner_id=current_user.user_id).all()
    return render_template('gonderi.html', team=team, files=files)

@team_bp.route('/open/<int:post_id>', methods=['GET'])
@login_required
def open_post(post_id):
    # Fetch the post based on the given post_id
    post = Post.query.get(post_id)
    
    if post and post.user_id == current_user.user_id:  # Check if the post exists and belongs to the current user
        # Get the associated file
        file_record = post.file
        
        if file_record:
            file_path = file_record.filepath  # Get the file path from the 'file' record
            
            # Check if the file exists in the system
            if os.path.exists(file_path):
                # Serve the file in the browser
                return send_file(file_path, as_attachment=False)  # Opens the file in the browser
            else:
                flash('File not found on the server', 'danger')
                return redirect(url_for('team.team_page', team_id=post.team_id))  # Redirect back to the team page
        else:
            flash('No file associated with this post', 'danger')
            return redirect(url_for('team.team_page', team_id=post.team_id))  # Redirect back to the team page
    else:
        flash('Post not found or you do not have permission to access this post', 'danger')
        return redirect(url_for('team.team_page')) 
    


@team_bp.route('/team/<int:team_id>/info')
@login_required
def team_info(team_id):
    team = Team.query.get_or_404(team_id)  # Get the team by ID
    owner = User.query.get_or_404(team.owner_id)  # Fetch the owner based on the owner_id

    # Fetch the members, join TeamMember and User to get member details
    members = db.session.query(User, TeamMember).join(TeamMember).filter(TeamMember.team_id == team.id).all()

    return render_template('team_info.html', team=team, owner=owner, members=members)

