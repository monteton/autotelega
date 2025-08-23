import requests

class TelegramClient:
    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def verify_credentials(self):
        """Проверка корректности credentials"""
        print("🔍 Проверка Telegram credentials...")
        
        try:
            # Проверка бота
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code != 200:
                return False
            
            # Проверка доступа к каналу
            response = requests.post(
                f"{self.base_url}/getChat",
                data={"chat_id": self.channel_id},
                timeout=10
            )
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Ошибка проверки Telegram: {e}")
            return False
    
    def send_post(self, text, image_bytes=None):
        """Отправка поста в Telegram"""
        print("📤 Отправка в Telegram...")
        
        try:
            if image_bytes:
                url = f"{self.base_url}/sendPhoto"
                files = {'photo': ('trend_image.png', image_bytes, 'image/png')}
                data = {
                    'chat_id': self.channel_id,
                    'caption': text,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, files=files, data=data)
            else:
                url = f"{self.base_url}/sendMessage"
                data = {
                    "chat_id": self.channel_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, data=data)
            
            if response.status_code == 200:
                print("✅ Пост успешно отправлен!")
                return True
            else:
                print(f"❌ Ошибка отправки: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")
            return False
