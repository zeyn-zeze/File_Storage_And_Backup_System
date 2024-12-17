# File_Storage_And_Backup_System
Kullanıcıların dosyalarını güvenli bir şekilde yedeklemelerini, senkronize etmelerini ve yönetmelerini sağlayan; aynı zamanda logları gerçek zamanlı olarak izleyip anormallikleri tespit eden ve kullanıcı davranışlarını analiz ederek veri güvenliğini sağlayan bir Dosya Depolama ve Yedekleme Sistemi.

# Dosya Depolama ve Yedekleme Sistemi

Bu proje, kullanıcıların dosyalarını güvenli bir şekilde yedekleyip senkronize etmelerine, log dosyalarını izleyip analiz etmelerine ve anormal kullanıcı davranışlarını tespit etmelerine olanak sağlayan bir **Dosya Depolama ve Yedekleme Sistemi**dir.

---

## 🚀 Proje Hakkında

### Özellikler:
- Kullanıcı yönetimi (kayıt, giriş, çıkış)
- Şifrelenmiş kullanıcı parolası saklama
- Dosya yedekleme ve senkronizasyon
- Log dosyalarını izleme ve anormallik tespiti
- Kullanıcı davranışı analizi ve raporlama
- Web tabanlı kullanıcı arayüzü

---

## 🛠️ Kullanılan Teknolojiler

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: Flask-HTML, Bootstrap
- **Şifreleme**: Bcrypt
- **Log ve Analiz**: Pandas, Logging
- **Zamanlama ve Görev Yönetimi**: APScheduler veya Celery

---

## 📂 Proje Yapısı

```plaintext
project/
│
├── app.py                   # Uygulamayı çalıştıran ana dosya
├── config.py                # Flask yapılandırma ayarları
├── requirements.txt         # Gerekli Python kütüphaneleri
├── migrations/              # Flask-Migrate için dosyalar
│
├── models/                  # Veritabanı modelleri
│   ├── __init__.py          # SQLAlchemy ve Bcrypt başlatıcı
│   ├── User.py              # Kullanıcı modeli
│   └── OtherModels.py       # Diğer modeller
│
├── routes/                  # Uygulama rotaları
│   ├── __init__.py          # Blueprint başlatıcı
│   ├── auth_routes.py       # Kayıt, giriş ve çıkış işlemleri
│   ├── file_routes.py       # Dosya yedekleme ve senkronizasyon rotaları
│   └── log_routes.py        # Log görüntüleme ve anomali tespiti rotaları
│
├── templates/               # HTML şablonları
│   ├── base.html            # Ana HTML şablonu
│   ├── register.html        # Kayıt sayfası
│   ├── login.html           # Giriş sayfası
│   └── home.html            # Ana sayfa
│
├── static/                  # Statik dosyalar (CSS, JS, resimler)
│   ├── css/
│   │   └── style.css        # CSS dosyası
│   ├── js/
│   │   └── script.js        # JavaScript dosyası
│   └── images/              # Görseller
│
└── utils/                   # Yardımcı modüller
    ├── __init__.py          # Yardımcı araçlar
    ├── security.py          # Şifreleme ve güvenlik işlevleri
    └── scheduler.py         # Periyodik görevler (yedekleme vb.)

