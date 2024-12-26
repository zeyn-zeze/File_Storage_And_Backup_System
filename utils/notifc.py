from datetime import datetime
from models.Notification import Notification
from models.TeamMember import TeamMember
from models.User import User
from models import db

#takım işleri
def send_team_deletion_notification(team, owner_user):
    # Bildirim mesajı oluşturuluyor
    message = f"{owner_user.username} tarafından takım ({team.name}) silindi."
    
    # Takım üyeleri için bildirim gönderilecek
    members = TeamMember.query.filter_by(team_id=team.id).all()
    for member in members:
        # Bildirimi alacak kullanıcıyı al
        member_user = User.query.get(member.user_id)
        
        # Yeni bildirim nesnesi oluşturuluyor
        new_notification = Notification(
            user_id=member_user.user_id,  # Bildirimi alacak kullanıcının ID'si
            message=message,
            timestamp=datetime.now()
        )
        
        # Bildirimi veritabanına kaydediyoruz
        db.session.add(new_notification)

    # Bildirimler veritabanına kaydediliyor
    db.session.commit()

def send_team_creation_notification(team, member_user, owner_user):
    # Bildirim mesajı oluşturuluyor
    message = f"{owner_user.username} sana yeni bir takım ({team.name}) oluşturdu."
    
    # Yeni bildirim nesnesi oluşturuluyor
    new_notification = Notification(
        user_id=member_user.user_id,  # Bildirimi alacak kullanıcının ID'si
        message=message,
        timestamp=datetime.now()
    )
    
    # Bildirimi veritabanına kaydediyoruz
    db.session.add(new_notification)
    db.session.commit()


def send_file_upload_notification(team, user, file_name):
    # Bildirim mesajı oluşturuluyor
    message = f"{user.username} yeni bir dosya yükledi: {file_name}"
    
    # Takım üyeleri için bildirim gönderilecek
    members = TeamMember.query.filter_by(team_id=team.id).all()
    for member in members:
        # Bildirimi alacak kullanıcıyı al
        member_user = User.query.get(member.user_id)
        
        # Yeni bildirim nesnesi oluşturuluyor
        new_notification = Notification(
            user_id=member_user.user_id,  # Bildirimi alacak kullanıcının ID'si
            message=message,
            timestamp=datetime.now()
        )
        
        # Bildirimi veritabanına kaydediyoruz
        db.session.add(new_notification)

    # Bildirimler veritabanına kaydediliyor
    db.session.commit()


#admin password değiştirme 
def send_password_change_notification(user, message):
    new_notification = Notification(
        user_id=user.user_id,
        message=message,
        timestamp=datetime.now()
    )
    db.session.add(new_notification)
    db.session.commit()

# Post Silindiğinde Bildirim Gönderme
def send_post_deletion_notification(post, current_user):
    # Bildirim mesajı oluşturuluyor
    message = f"{current_user.username} tarafından takım ({post.team.name}) gönderisi silindi."
    
    # Takım üyelerine bildirim gönder
    members = TeamMember.query.filter_by(team_id=post.team.id).all()
    for member in members:
        member_user = User.query.get(member.user_id)
        
        new_notification = Notification(
            user_id=member_user.user_id,
            message=message,
            timestamp=datetime.now()
        )
        
        db.session.add(new_notification)

    db.session.commit()

def send_new_post_notification(post):
    # Bildirim mesajı oluşturuluyor
    message = f"{post.user.username} tarafından yeni bir gönderi oluşturuldu: {post.content[:50]}..."  # Mesajın ilk 50 karakteri alınıyor
    
    # Takım üyelerine bildirim gönder
    members = TeamMember.query.filter_by(team_id=post.team.id).all()
    for member in members:
        member_user = User.query.get(member.user_id)
        
        # Yeni bildirim nesnesi oluşturuluyor
        new_notification = Notification(
            user_id=member_user.user_id,  # Bildirimi alacak kullanıcının ID'si
            message=message,
            timestamp=datetime.now()
        )
        
        db.session.add(new_notification)

    db.session.commit()

def send_post_rename_notification(post, current_user):
    # Bildirim mesajı oluşturuluyor
    message = f"{current_user.username} tarafından '{post.content[:50]}...' gönderisinin adı değiştirildi."

    # Takım üyelerine bildirim gönder
    members = TeamMember.query.filter_by(team_id=post.team.id).all()
    for member in members:
        member_user = User.query.get(member.user_id)
        
        # Yeni bildirim nesnesi oluşturuluyor
        new_notification = Notification(
            user_id=member_user.user_id,  # Bildirimi alacak kullanıcının ID'si
            message=message,
            timestamp=datetime.now()
        )
        
        db.session.add(new_notification)

    db.session.commit()

# Post Silindiğinde Bildirim Gönderme
def send_post_deletion_notification(post, current_user):
    # Bildirim mesajı oluşturuluyor
    message = f"{current_user.username} tarafından takım ({post.team.name}) gönderisi silindi."
    
    # Takım üyelerine bildirim gönder
    members = TeamMember.query.filter_by(team_id=post.team.id).all()
    for member in members:
        member_user = User.query.get(member.user_id)
        
        new_notification = Notification(
            user_id=member_user.user_id,
            message=message,
            timestamp=datetime.now()
        )
        
        db.session.add(new_notification)

    db.session.commit()


def send_login_anomaly_notification(user, message=None):
    """
    Giriş anomalisi durumunda hem kullanıcıya hem de admin'e bildirim oluşturur.

    Args:
    - user (User): Anomaliyle ilişkili kullanıcı.
    - message (str): Gönderilecek mesaj içeriği.
    """
    if not message:
        message = f"{user.username} hesabında 3 başarısız giriş denemesi tespit edildi."

    try:
        # Kullanıcıya bildirim oluştur
        user_notification = Notification(
            user_id=user.id,
            message=f"Hesabınızda bir güvenlik uyarısı: {message}",
            timestamp=datetime.now()
        )
        db.session.add(user_notification)

        # Admin'e bildirim oluştur
        admin_user = User.query.filter_by(role='admin').first()  # Admin rolündeki kullanıcıyı al
        if admin_user:
            admin_notification = Notification(
                user_id=admin_user.id,
                message=f"Kullanıcı {user.username} için giriş anomalisi: {message}",
                timestamp=datetime.now()
            )
            db.session.add(admin_notification)

        # Bildirimleri kaydet
        db.session.commit()
        print("Bildirimler başarıyla gönderildi ve veritabanına kaydedildi.")
    except Exception as e:
        print(f"Bildirim gönderimi sırasında hata oluştu: {e}")