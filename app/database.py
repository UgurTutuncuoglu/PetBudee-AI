
import sqlite3
from flask import g, current_app


def get_db():
    """Veritabanı bağlantısını oluşturur veya mevcut bağlantıyı döndürür."""
    if "db" not in g:
        database_url = current_app.config.get(
            "DATABASE_URL", "sqlite:///petbudee.db"
        )

        # sqlite:///petbudee.db -> petbudee.db
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            raise ValueError("Desteklenmeyen DATABASE_URL biçimi")

        db_path = database_url[len(prefix):]

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row

    return g.db


def init_db(app):
    """Uygulama bağlamında veritabanı bağlantısını ve tabloyu hazırlar."""
    with app.app_context():
        db = get_db()

        db.execute("""
            CREATE TABLE IF NOT EXISTS petbudee (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                soyisim TEXT NOT NULL,
                email TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mesaj TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()

    # Her istek tamamlandığında bağlantıyı kapat.
    app.teardown_appcontext(close_db)


def close_db(exception=None):
    """Uygulama bağlamı sona erdiğinde bağlantıyı kapatır."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def petbudee_ekle(isim,soyisim,email, telefon, mesaj):
    """Yeni müşteri adayı ekler."""
    db = get_db()

    db.execute(
        """
        INSERT INTO petbudee (isim, soyisim, email, telefon, mesaj)
        VALUES (?, ?, ?, ?, ?)
        """,
        (isim, soyisim, email, telefon, mesaj)
    )

    db.commit()


def tum_petbudeeler():
    """Müşteri adaylarını en yeniden eskiye listeler."""
    db = get_db()

    records = db.execute(
        "SELECT * FROM petbudee ORDER BY tarih DESC, id DESC"
    ).fetchall()

    return records