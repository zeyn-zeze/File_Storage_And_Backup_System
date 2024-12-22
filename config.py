class Config:
    SECRET_KEY = 'yedek'
    # Veritabanı bağlantı dizesini güncelledim ve özel karakterler için URL encode kullandım.
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/flaskdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dosya yükleme ayarları
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maksimum dosya boyutu 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
