from flask import Blueprint, flash, redirect, render_template, request, url_for

from models.File import File
from models.TeamMember import TeamMember
from models.User import User
from models.Team import Team
from models.PasswordResetRequest import PasswordResetRequest
from models import  db,bcrypt

admin_bp = Blueprint('admin', __name__)
from flask_login import current_user, login_required

@admin_bp.route('/admin/dashboard')
def dashboard():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            # Veri gönder
            password_requests = PasswordResetRequest.query.filter_by(status='pending').all()
            logs = []  # Log verisi ekleyin
            anomaly_logs = []  # Anomali logları ekleyin
            
            return render_template('admin_dashboard.html', 
                                   password_requests=password_requests, 
                                   logs=logs, 
                                   anomaly_logs=anomaly_logs)  # Verilerle birlikte şablonu render edin
        else:
            flash('Yetkiniz yok!', 'danger')
            return redirect(url_for('auth.admin_login'))  # Yetkisi olmayanlar login sayfasına yönlendir
    else:
        flash('Giriş yapmanız gerekiyor!', 'danger')
        return redirect(url_for('auth.admin_login'))  # Giriş yapmamış kullanıcıyı login sayfasına yönlendir



# Route for displaying users and handling the update form
@admin_bp.route('/admin/manage_users', methods=['GET'])
def manage_users():
    users = User.query.all()  # Get all users
    return render_template('manage_users.html', users=users)

# Route for handling user updates
@admin_bp.route('/admin/update_user', methods=['POST'])
def update_user():
    user_id = request.form.get('user_id')
    user_to_update = User.query.get(user_id)

    if user_to_update:
        # Update fields except active
        user_to_update.username = request.form.get('username')
        user_to_update.email = request.form.get('email')
        user_to_update.role = request.form.get('role')

        # Update password only if provided
        new_password = request.form.get('password')
        if new_password:
            user_to_update.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # Commit changes to the database
        db.session.commit()
        flash("User updated successfully!")
    else:
        flash("User not found!")

    return redirect(url_for('admin.manage_users'))


# Route for handling user deletions
@admin_bp.route('/delete_user', methods=['POST'])

def delete_user():
    user_id = request.form.get('user_id')
    user_to_delete = User.query.get(user_id)
    
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")
    else:
        flash("User not found!")

    return redirect(url_for('admin.manage_users'))



@admin_bp.route('/admin/user_info/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_info(user_id):
    if current_user.role != 'admin':
        flash("Bu işlemi yapmaya yetkiniz yok.", "danger")
        return redirect(url_for('auth.admin_login'))  # Redirect if not an admin

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Capture the new storage limit from the form
        new_storage_limit = request.form.get('storage_limit')
        # Update the user's storage limit
        user.storage_limit = new_storage_limit
        db.session.commit()
        flash('Depolama limiti başarıyla güncellendi.', 'success')

        # Redirect back to the user info page
        return redirect(url_for('admin.user_info', user_id=user.user_id))  # Or the appropriate route

    # Fetch teams and backup files
    teams = TeamMember.query.filter_by(user_id=user_id).all()
    backup_files = File.query.filter_by(owner_id=user_id).all()

    return render_template('user_info.html', user=user, teams=teams, backup_files=backup_files)







@admin_bp.route('/admin/delete_team', methods=['POST'])
def delete_team():
    team_id = request.form.get('team_id')
    user_id = request.form.get('user_id')
    team = Team.query.get(team_id)
    if team:
        # Takımı ve ilişkili üyeyi silebilirsiniz
        db.session.delete(team)
        db.session.commit()
    return redirect(url_for('admin.user_info', user_id=user_id))




@admin_bp.route('/admin/set_storage_limit', methods=['GET', 'POST'])
@login_required
def set_storage_limit():
    if current_user.role != 'admin':
        flash("Bu işlemi yapmaya yetkiniz yok.", "danger")
        return redirect(url_for('auth.admin_login'))

    # Logic for updating storage limit (similar to the one in user_info)
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_limit = request.form.get('storage_limit')
        user = User.query.get(user_id)
        if user:
            user.storage_limit = new_limit
            db.session.commit()
            flash("Depolama limiti başarıyla güncellendi.", "success")
        else:
            flash("Kullanıcı bulunamadı.", "danger")
        
    return redirect(url_for('admin.user_info', user_id=user_id))


#Şifre Değişim istekleri yönetimi


@admin_bp.route('/admin/password_requests', methods=['GET', 'POST'])
@login_required
def manage_password_requests():
    if current_user.role != 'admin':
        flash("Bu işlemi yapmaya yetkiniz yok.", "danger")
        return redirect(url_for('main.dashboard'))

    # Bekleyen talepleri çek
    requests = PasswordResetRequest.query.filter_by(status='pending').all()

    if request.method == 'POST':
        request_id = request.form.get('request_id')
        new_password = request.form.get('new_password')
        reset_request = PasswordResetRequest.query.get(request_id)

        if reset_request:
            user = User.query.get(reset_request.user_id)
            if user:
                # Yeni şifreyi hash'le ve kaydet
                user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                reset_request.status = 'approved'
                db.session.commit()
                flash(f"{user.username} kullanıcısının şifresi başarıyla değiştirildi.", "success")
            else:
                flash("Kullanıcı bulunamadı.", "danger")
        else:
            flash("Talep bulunamadı.", "danger")

    return render_template('password_requests.html', requests=requests)

