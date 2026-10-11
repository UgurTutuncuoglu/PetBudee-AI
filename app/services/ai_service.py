import os
import requests

from config import config_by_name


class AIServiceError(Exception):
    """Yapay zeka servisi hataları."""
    pass


class AIService:

    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "openai/gpt-oss-120b"

    def __init__(self):
        environment = os.environ.get("FLASK_ENV", "development")
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

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.MODEL,
            "messages": messages
        }

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            raise AIServiceError(
                f"Groq istegi basarisiz: {e}"
            ) from e

    def yanit_uret(self, mesaj, gecmis=None):
        """Kullanıcı mesajına yapay zeka yanıtı üretir."""

        if not self.config.GROQ_API_KEY:
            return (
                "Demo modu: Henüz GROQ_API_KEY tanımlanmamış. "
                "API anahtarını eklediğinde gerçek yanıtlar alabilirsin."
            )

        messages = [
            {
                "role": "system",
                "content": self._sistem_talimati()
            }
        ]

        if gecmis:
            messages.extend(gecmis)

        messages.append({
            "role": "user",
            "content": mesaj
        })

        return self._groq_istegi(messages)


# Uygulama genelinde kullanılacak tek örnek
ai_service = AIService()
