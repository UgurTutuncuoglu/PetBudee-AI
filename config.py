
import os
from dotenv import load_dotenv

# .env dosyasındaki değerleri ortam değişkenlerine yükle
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "insecure-development-key"
    )
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "sqlite:///petbudee.db"
    )
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")
    BUSINESS_CONTEXT = os.environ.get(
        "BUSINESS_CONTEXT",
        "Sen yardımcı ve nazik bir yapay zekâ asistanısın."
    )
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000, http://127.0.0.1:5000 "
    )

    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}