
import os
from dotenv import load_dotenv

# .env dosyasındaki değerleri ortam değişkenlerine yükle
load_dotenv()


class Config:
    
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "insecure-development-key"
    )

    # Veritabanı bağlantı adresi.
    # Varsayılan olarak SQLite veritabanı kullanılır.
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "sqlite:///petbudee.db"
    )

     # Groq API anahtarı; tanımlanmamışsa boş metin kullanılır.
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

    # Groq AI modeli
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")

    # Yapay zekânın rolünü, davranışını ve uygulama hakkındaki
    # bilgilerini belirleyen sistem talimatı.
    BUSINESS_CONTEXT = os.environ.get(
        "BUSINESS_CONTEXT",
        "Sen yardımcı ve nazik bir yapay zekâ asistanısın."
    )

    # API'ye hangi web adreslerinden erişilebileceğini belirler.
    # Birden fazla adres virgülle ayrılabilir.
    # Varsayılan değerler yerel geliştirme içindir.
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000, http://127.0.0.1:5000 "
    )

    ADMIN_MAIL = os.getenv("ADMIN_MAIL", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

    DEBUG = False

    """Yerel geliştirme ortamının ayarlarını tanımlar."""

class DevelopmentConfig(Config):
    DEBUG = True

    """Canlı yayın ortamının ayarlarını tanımlar."""

class ProductionConfig(Config):
    DEBUG = False

# Ortam adına göre kullanılacak yapılandırma sınıfını eşleştir.
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}