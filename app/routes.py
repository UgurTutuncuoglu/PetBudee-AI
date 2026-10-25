import hmac
import jwt

from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, render_template, request, jsonify

from app.database import petbudee_ekle, tum_petbudeeler, petbudee_sayisi, petbudee_gunluk_sayisi
from app.services.ai_service import ai_service, AIServiceError

from config import Config

pages_bp = Blueprint("pages", __name__)
api_bp = Blueprint("api", __name__)

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        # Sunucu ayarları eksikse güvenli şekilde reddet.
        if not Config.SECRET_KEY or not Config.ADMIN_MAIL:
            return jsonify({
                "basari": False,
                "mesaj": "Yönetici ayarları yapılandırılmamış."
            }), 500

        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "basari": False,
                "mesaj": "Yönetici girişi gerekli."
            }), 401

        try:
            payload = jwt.decode(
                parts[1],
                Config.SECRET_KEY,
                algorithms=["HS256"]
            )

            admin_mail = Config.ADMIN_MAIL.strip().casefold()

            if payload.get("sub") != admin_mail:
                raise jwt.InvalidTokenError("Yetkisiz kullanıcı")

        except jwt.ExpiredSignatureError:
            return jsonify({
                "basari": False,
                "mesaj": "Oturum süresi doldu. Yeniden giriş yapın."
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "basari": False,
                "mesaj": "Geçersiz token."
            }), 401

        return view(*args, **kwargs)

    return wrapped

# 1. GET /
@pages_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# 2. GET /dashboard
@pages_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


# 3. POST /api/sohbet
@api_bp.route("/sohbet", methods=["POST"])
def sohbet():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "basari": False,
            "mesaj": "Gecerli bir JSON gondermelisiniz."
        }), 400

    mesaj = data.get("mesaj")
    gecmis = data.get("gecmis", [])

    if not isinstance(mesaj, str) or not mesaj.strip():
        return jsonify({
            "basari": False,
            "mesaj": "Mesaj alani bos olamaz."
        }), 400

    if not isinstance(gecmis, list):
        return jsonify({
            "basari": False,
            "mesaj": "Gecmis alani bir liste olmalidir."
        }), 400

    try:
        cevap = ai_service.yanit_uret(mesaj.strip(), gecmis)

        return jsonify({
            "basari": True,
            "cevap": cevap
        }), 200

    except AIServiceError:
        return jsonify({
            "basari": False,
            "mesaj": "Yapay zeka servisine su anda ulasilamiyor."
        }), 503


# 4. POST /api/petbudee
@api_bp.route("/petbudee", methods=["POST"])
def yeni_petbudee():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "basari": False,
            "mesaj": "Gecerli bir JSON gondermelisiniz."
        }), 400

    isim = data.get("isim")
    soyisim = data.get("soyisim")
    email = data.get("email")
    telefon = data.get("telefon")
    mesaj = data.get("mesaj", "")

    zorunlu_alanlar = [isim, soyisim, email, telefon]

    if not all(
        isinstance(deger, str) and deger.strip()
        for deger in zorunlu_alanlar
    ):
        return jsonify({
            "basari": False,
            "mesaj": "Isim, soyisim, email ve telefon zorunludur."
        }), 400

    if not isinstance(mesaj, str):
        return jsonify({
            "basari": False,
            "mesaj": "Mesaj metin formatinda olmalidir."
        }), 400

    try:
        petbudee_ekle(
            isim.strip(),
            soyisim.strip(),
            email.strip(),
            telefon.strip(),
            mesaj.strip()
        )

        return jsonify({
            "basari": True,
            "mesaj": "Kayit basariyla eklendi."
        }), 201

    except Exception:
        return jsonify({
            "basari": False,
            "mesaj": "Kayit eklenirken bir hata olustu."
        }), 500


# 5. GET /api/petbudees
@api_bp.route("/petbudees", methods=["GET"])
@admin_required
def petbudeeleri_getir():
    try:
        records = tum_petbudeeler()

        return jsonify({
            "basari": True,
            "petbudees": [dict(record) for record in records]
        }), 200

    except Exception:
        return jsonify({
            "basari": False,
            "mesaj": "Kayitlar getirilirken bir hata olustu."
        }), 500


# 6. POST /api/admin-login
@api_bp.route("/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "basari": False,
            "mesaj": "Geçerli bir JSON göndermelisiniz."
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "basari": False,
            "mesaj": "E-posta ve şifre zorunludur."
        }), 400

    if not email.strip() or not password:
        return jsonify({
            "basari": False,
            "mesaj": "E-posta ve şifre zorunludur."
        }), 400

    admin_mail = Config.ADMIN_MAIL.strip().casefold()
    admin_password = Config.ADMIN_PASSWORD

    if not admin_mail or not admin_password or not Config.SECRET_KEY:
        return jsonify({
            "basari": False,
            "mesaj": "Yönetici ayarları yapılandırılmamış."
        }), 500

    email_match = hmac.compare_digest(
        email.strip().casefold(),
        admin_mail
    )

    password_match = hmac.compare_digest(
        password,
        admin_password
    )

    if not (email_match and password_match):
        return jsonify({
            "basari": False,
            "mesaj": "E-posta veya şifre hatalı."
        }), 401

    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": admin_mail,
            "iat": now,
            "exp": now + timedelta(minutes=15)
        },
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "basari": True,
        "mesaj": "Giriş başarılı.",
        "token": token,
        "token_type": "Bearer",
        "expires_in": 900
    }), 200



# GET /api/petbudee-sayisi
@api_bp.route("/petbudee-sayisi", methods=["GET"])
@admin_required
def petbudee_sayisini_getir():
    try:
        toplam = petbudee_sayisi()

        return jsonify({
            "basari": True,
            "toplam": toplam
        }), 200

    except Exception:
        return jsonify({
            "basari": False,
            "mesaj": "Kayıt sayısı alınırken bir hata oluştu."
        }), 500


# GET /api/petbudee-gunluk-sayisi
@api_bp.route("/petbudee-gunluk-sayisi", methods=["GET"])
@admin_required
def petbudee_gunluk_sayisini_getir():
    try:
        toplam = petbudee_gunluk_sayisi()

        return jsonify({
            "basari": True,
            "bugunku_toplam": toplam
        }), 200

    except Exception:
        return jsonify({
            "basari": False,
            "mesaj": "Günlük kayıt sayısı alınırken bir hata oluştu."
        }), 500