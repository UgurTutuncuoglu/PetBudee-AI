from flask import Flask, jsonify
from flask_cors import CORS

from config import config_by_name
from app.database import init_db
from app.routes import pages_bp, api_bp


def create_app():
    app = Flask(__name__, template_folder="templates")

    # 1. Ayarları yükle
    app.config.from_object(config_by_name["development"])

    # 2. CORS ayarlarını config.py üzerinden al
    origins = [
        origin.strip()
        for origin in app.config["CORS_ORIGINS"].split(",")
        if origin.strip()
    ]
    CORS(app, origins=origins)

    
    # 3. Veritabanını başlat
    with app.app_context():
        init_db(app)

    # 4. Blueprint'leri kaydet
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # 5. Sağlık kontrolü
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app



