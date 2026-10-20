
from flask import Blueprint, render_template, request, jsonify

from app.database import petbudee_ekle, tum_petbudeeler
from app.services.ai_service import ai_service, AIServiceError



pages_bp = Blueprint("pages", __name__)
api_bp = Blueprint("api", __name__)

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


# 6. Admin Login api/admin-login
@app.route("/api/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().casefold()

    admin_mail = os.getenv("ADMIN_MAIL", "").strip().casefold()

    if not admin_mail:
        return jsonify({
            "basari": False,
            "mesaj": "Yönetici e-posta ayarı yapılandırılmamış."
        }), 500

    if email == admin_mail:
        return jsonify({
            "basari": True,
            "mesaj": "E-posta eşleşti."
        }), 200

    return jsonify({
        "basari": False,
        "mesaj": "Bu e-posta adresi yetkili değil."
    }), 401