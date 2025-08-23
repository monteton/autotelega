import requests
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap

class AIGenerator:
    def __init__(self, grok_api_key):
        self.grok_api_key = grok_api_key
        self.api_url = "https://api.x.ai/v1"
    
    def generate_text(self, trend):
        """Генерация текста поста через Grok API"""
        print("🧠 Генерация текста через Grok API...")
        
        prompt = self._create_text_prompt(trend)
        
        try:
            response = self._make_grok_request(
                endpoint="/chat/completions",
                data={
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Ты эксперт по digital-маркетингу. Создавай качественные посты с реальными фактами."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-4-latest",
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            if response:
                return response['choices'][0]['message']['content'].strip()
            return None
            
        except Exception as e:
            print(f"❌ Ошибка генерации текста: {e}")
            return None
    
    def generate_image(self, trend):
        """Генерация изображения через Grok API"""
        print("🎨 Генерация изображения через Grok API...")
        
        try:
            response = self._make_grok_request(
                endpoint="/images/generations",
                data={
                    "model": "grok-image-gen-latest",
                    "prompt": self._create_image_prompt(trend),
                    "size": "1024x1024",
                    "quality": "standard",
                    "n": 1
                }
            )
            
            if response and 'data' in response:
                image_url = response['data'][0]['url']
                return self._download_image(image_url)
            return self._generate_fallback_image(trend)
            
        except Exception as e:
            print(f"❌ Ошибка генерации изображения: {e}")
            return self._generate_fallback_image(trend)
    
    def _make_grok_request(self, endpoint, data):
        """Выполнение запроса к Grok API"""
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.grok_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка API: {response.status_code} - {response.text}")
            return None
    
    def _create_text_prompt(self, trend):
        """Создание промпта для генерации текста"""
        return f"""Создай профессиональный пост для Telegram-канала о маркетинге на тему: "{trend}"

Требования:
- Основа на реальных трендах 2024-2025
- Конкретные цифры и статистика
- Длина: 250-400 символов
- Стиль: профессиональный с элементами легкости
- Эмодзи и призыв к обсуждению
- 3-4 релевантных хештега"""
    
    def _create_image_prompt(self, trend):
        """Создание промпта для генерации изображения"""
        return f"Современное изображение для поста о маркетинге на тему '{trend}'. Стиль: профессиональный, digital, с иконками маркетинга и аналитики."
    
    def _download_image(self, image_url):
        """Скачивание изображения"""
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        return None
    
    def _generate_fallback_image(self, trend):
        """Резервная генерация изображения"""
        try:
            width, height = 1000, 500
            image = Image.new('RGB', (width, height), color=(25, 35, 45))
            draw = ImageDraw.Draw(image)
            
            # Градиентный фон
            for i in range(height):
                r = int(25 + (i / height) * 20)
                g = int(35 + (i / height) * 15)
                b = int(45 + (i / height) * 20)
                draw.line([(0, i), (width, i)], fill=(r, g, b))
            
            font = ImageFont.load_default()
            
            # Заголовок
            title = "АКТУАЛЬНЫЙ ТРЕНД"
            draw.text((width//2, 100), title, font=font, fill=(255, 215, 0), anchor="mm")
            
            # Основной текст
            wrapped_text = textwrap.fill(trend, width=25)
            draw.text((width//2, 250), wrapped_text, font=font, fill=(255, 255, 255), anchor="mm")
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr
            
        except Exception as e:
            print(f"❌ Ошибка резервной генерации изображения: {e}")
            return None
