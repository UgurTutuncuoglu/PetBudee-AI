# SmartLead AI

SmartLead AI, Flask tabanlı bir web uygulamasıdır. Yapay zekâ destekli sohbet hizmeti sunar ve kullanıcı bilgilerini SQLite veritabanında saklar. Groq API, yapay zekâ yanıtlarının oluşturulması için kullanılır.

## Özellikler

- Yapay zekâ destekli sohbet
- Kullanıcı bilgilerinin kaydedilmesi
- Kayıtların listelenmesi
- SQLite veritabanı entegrasyonu
- Flask REST API
- CORS desteği
- Render üzerinde yayınlanabilir uygulama yapısı

## Kullanılan Teknolojiler

- Python
- Flask
- SQLite
- Groq API
- Flask-CORS
- python-dotenv
- Requests
- Gunicorn

## Proje Yapısı

```text
smartlead_ai/
├── run.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
└── app/
    ├── __init__.py
    ├── database.py
    ├── routes.py
    ├── templates/
    │   ├── index.html
    │   └── dashboard.html
    └── services/
        ├── __init__.py
        └── ai_service.py
```

## Kurulum

### Gereksinimler

- Python 3
- pip
- Git (isteğe bağlı)

### 1. Projeyi klonlama

```bash
git clone https://github.com/KULLANICI_ADI/smartlead-ai.git
cd smartlead-ai
```

GitHub depo adresini kendi depo adresinizle değiştirin.

### 2. Sanal ortam oluşturma

Windows:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları yükleme

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarlama

Projenin ana dizininde `.env` dosyası oluşturun:

```env
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
AI_PROVIDER=groq
DATABASE_URL=sqlite:///petbudee.db
BUSINESS_CONTEXT="Sen yardımcı ve nazik bir yapay zekâ asistanısın."
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5000
```

`GROQ_API_KEY` alanına kendi API anahtarınızı girin. Gerçek anahtarları GitHub'a yüklemeyin. Üretim ortamında ortam değişkenleri Render üzerinden ayarlanmalıdır.

### 5. Uygulamayı çalıştırma

```bash
python run.py
```

## API Endpointleri

API rotaları `/api` ön ekiyle sunulur.

| Metot | Endpoint | Açıklama |
|---|---|---|
| GET | `/health` | Sunucu sağlık kontrolü |
| POST | `/api/sohbet` | Yapay zekâ ile sohbet |
| POST | `/api/petbudee` | Yeni kullanıcı kaydı oluşturma |
| GET | `/api/petbudees` | Kayıtları listeleme |

### 1. Sağlık kontrolü

**İstek:**

```http
GET /health
```

**Başarılı yanıt — HTTP 200:**

```json
{
  "status": "ok"
}
```

### 2. Yapay zekâ sohbeti

**İstek:**

```http
POST /api/sohbet
Content-Type: application/json
```

**Örnek istek gövdesi:**

```json
{
  "mesaj": "SmartLead AI ne işe yarar?",
  "gecmis": []
}
```

`mesaj` zorunludur. `gecmis`, önceki konuşma mesajlarını içeren isteğe bağlı bir listedir.

**Başarılı yanıt — HTTP 200:**

```json
{
  "basari": true,
  "cevap": "Yapay zekâ tarafından oluşturulan yanıt."
}
```

Geçersiz JSON veya boş mesaj gönderildiğinde HTTP 400; yapay zekâ servisi hatası oluştuğunda HTTP 503 döndürülebilir.

### 3. Yeni kayıt oluşturma

**İstek:**

```http
POST /api/petbudee
Content-Type: application/json
```

**Örnek istek gövdesi:**

```json
{
  "isim": "Ali",
  "soyisim": "Yılmaz",
  "email": "ali@example.com",
  "telefon": "05551234567",
  "mesaj": "Bilgi almak istiyorum."
}
```

`isim`, `soyisim`, `email` ve `telefon` zorunludur. `mesaj` alanı isteğe bağlıdır.

**Başarılı yanıt — HTTP 201:**

```json
{
  "basari": true,
  "mesaj": "Kayit basariyla eklendi."
}
```

### 4. Kayıtları listeleme

**İstek:**

```http
GET /api/petbudees
```

**Başarılı yanıt — HTTP 200:**

```json
{
  "basari": true,
  "petbudees": [
    {
      "id": 1,
      "isim": "Ali",
      "soyisim": "Yılmaz",
      "email": "ali@example.com",
      "telefon": "05551234567",
      "mesaj": "Bilgi almak istiyorum.",
      "tarih": "2026-10-11"
    }
  ]
}
```

Yanıttaki örnek tarih biçimi temsilidir; gerçek tarih biçimi veritabanı koduna bağlıdır. Kayıtlar en yeniden eskiye sıralanır.

## Veritabanı Şeması

Uygulama SQLite kullanır. Veritabanı bağlantısı ve SQL işlemleri `app/database.py` dosyasında yönetilir.

Tablo adı: `petbudee`

| Alan | Açıklama |
|---|---|
| `id` | Otomatik artan birincil anahtar |
| `isim` | Kullanıcının adı |
| `soyisim` | Kullanıcının soyadı |
| `email` | E-posta adresi |
| `telefon` | Telefon numarası |
| `mesaj` | Kullanıcının mesajı |
| `tarih` | Kaydın oluşturulma tarihi |

Örnek SQL şeması:

```sql
CREATE TABLE IF NOT EXISTS petbudee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isim TEXT NOT NULL,
    soyisim TEXT NOT NULL,
    email TEXT NOT NULL,
    telefon TEXT NOT NULL,
    mesaj TEXT,
    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Not: Bu SQL, alanların amaçlanan yapısını gösteren örnektir. Kesin şema, `app/database.py` içindeki `CREATE TABLE` sorgusuyla aynı olmalıdır.

## Yayınlama

Uygulama GitHub ve Render üzerinden yayınlanabilir.

Render Web Service ayarları:

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn run:app
```

`GROQ_API_KEY`, `SECRET_KEY`, `DATABASE_URL`, `BUSINESS_CONTEXT` ve `CORS_ORIGINS` gibi değişkenler Render'ın Environment bölümünden ayarlanmalıdır.

Canlı ortamda Wix entegrasyonu yapılacaksa API adresi, yerel adres yerine Render tarafından sağlanan HTTPS adresi olmalıdır.

## Güvenlik

- `.env` dosyası GitHub'a yüklenmemelidir.
- API anahtarları istemci tarafındaki Wix koduna eklenmemelidir.
- Üretim ortamında güçlü bir `SECRET_KEY` kullanılmalıdır.
- CORS yalnızca izin verilen origin adreslerini kapsamalıdır.
- Veritabanı yedekleme ve kalıcılık gereksinimleri yayın ortamında ayrıca değerlendirilmelidir.

## Lisans

Bu proje eğitim ve geliştirme amacıyla hazırlanmıştır.

# Sonuçlar
<img width="483" height="152" alt="Ekran görüntüsü 2026-10-11 194709" src="https://github.com/user-attachments/assets/71330753-d050-44e8-9f6c-628fe08ef4e5" />
<img width="402" height="197" alt="Ekran görüntüsü 2026-10-11 194728" src="https://github.com/user-attachments/assets/b81d6ffb-84f2-4e0a-bd54-65b4b8d04509" />
<img width="500" height="195" alt="Ekran görüntüsü 2026-10-11 194749" src="https://github.com/user-attachments/assets/44bb3454-e5d7-47d6-8cf4-ce643ff6d80b" />
<img width="545" height="551" alt="Ekran görüntüsü 2026-10-11 194844" src="https://github.com/user-attachments/assets/d410f916-2d7e-49d7-bb48-dea305ead900" />
<img width="1598" height="500" alt="Ekran görüntüsü 2026-10-11 195208" src="https://github.com/user-attachments/assets/63e2fbaf-a29f-491c-8c28-58a6477fc125" />
<img width="1617" height="532" alt="Ekran görüntüsü 2026-10-11 195234" src="https://github.com/user-attachments/assets/fb75269e-a348-4c8c-8e60-d521daae9a54" />







