import os
import requests

from config import config_by_name


class AIServiceError(Exception):
    """Yapay zeka servisi hataları."""
    pass


class AIService:
    # Groq sohbet tamamlama API'sinin adresi. 
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    # Kullanılacak yapay zekâ modeli.
    MODEL = "openai/gpt-oss-120b"


    def __init__(self):
        # Çalışma ortamını belirle; belirtilmemişse geliştirme ortamını kullan.
        environment = os.environ.get("FLASK_ENV", "development")

        # Ortama ait ayarları yükle.
        # Tanınmayan bir ortam adı verilirse geliştirme ayarlarını kullan.
        self.config = config_by_name.get(
            environment,
            config_by_name["development"]
        )

    def _sistem_talimati(self):
        """Sistem talimatını config.py üzerinden alır."""
        return self.config.BUSINESS_CONTEXT

    def _groq_istegi(self, messages):
        """Mesajları Groq API'sine gönderir."""
        api_key = self.config.GROQ_API_KEY

        # API isteğinde kimlik doğrulama ve içerik türünü belirt.

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # API isteğinde kimlik doğrulama ve içerik türünü belirt.

        payload = {
            "model": self.MODEL,
            "messages": messages
        }

            # Groq API'sine POST isteği gönder.
            # Uzun süre yanıt alınamazsa 30 saniye sonra zaman aşımına uğrat.
        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            # HTTP hatası varsa istisna oluştur.

            response.raise_for_status()
            
            # API yanıtını JSON formatına dönüştür.

            data = response.json()

            return data["choices"][0]["message"]["content"]
        
        # Ağ, HTTP, JSON veya beklenen yanıt alanlarıyla ilgili hataları yakala.
        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            raise AIServiceError(
                f"Groq istegi basarisiz: {e}"
            ) from e

    def yanit_uret(self, mesaj, gecmis=None):
        """Kullanıcı mesajına yapay zeka yanıtı üretir."""

        # API anahtarı yoksa gerçek API çağrısı yapmak yerine demo yanıtı ver.
        if not self.config.GROQ_API_KEY:
            return (
                "Demo modu: Henüz GROQ_API_KEY tanımlanmamış. "
                "API anahtarını eklediğinde gerçek yanıtlar alabilirsin."
            )

        # Konuşmanın başına sistem talimatını ekle.
        messages = [
            {
                "role": "system",
                "content": self._sistem_talimati()
            }
        ]

        if gecmis:
            messages.extend(gecmis)

        # Önceki konuşma mesajları verilmişse listeye ekle.
        messages.append({
            "role": "user",
            "content": mesaj
        })

        # Kullanıcının yeni mesajını konuşmanın sonuna ekle.
        return self._groq_istegi(messages)


# Uygulama genelinde kullanılacak tek örnek
ai_service = AIService()
