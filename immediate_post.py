import random
import requests
from pytrends.request import TrendReq
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os
from datetime import datetime
from google import genai
from google.genai import types

# Конфигурация из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI")
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', "-1002201089739")
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', "AIzaSyCuWBy5qkUMO5oTAcIivzYSC0R9xiZjoUU")

NISHA = ["маркетинг", "реклама", "новости", "социальные сети", "digital", "SMM"]
GEO_LOCATION = 'RU'

# Инициализируем клиент Gemini
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("✅ Gemini client initialized")
except Exception as e:
    print(f"❌ Gemini client error: {e}")
    client = None

def get_google_trends():
    """Получение актуальных трендов из Google Trends"""
    print("📊 Запрос к Google Trends...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=180)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        
        all_trends = []
        for key in NISHA:
            if key in trends_data and trends_data[key]['top'] is not None:
                all_trends.extend([row['query'] for _, row in trends_data[key]['top'].iterrows()])
        
        # Фильтруем только релевантные тренды
        filtered_trends = [t for t in all_trends if any(niche in t.lower() for niche in NISHA)]
        
        return list(set(filtered_trends)) if filtered_trends else get_fallback_trends()
        
    except Exception as e:
        print(f"❌ Ошибка Google Trends: {e}")
        return get_fallback_trends()

def get_fallback_trends():
    """Резервные тренды если Google Trends не работает"""
    current_date = datetime.now().strftime("%Y")
    return [
        f"тренды digital маркетинга {current_date}",
        f"новости социальных сетей {current_date}",
        "SMM стратегии для малого бизнеса",
        "контент маркетинг для привлечения клиентов",
        "таргетированная реклама в соцсетях",
        "нейросети в маркетинге и рекламе"
    ]

def generate_text_with_gemini(trend):
    """Генерация поста через Gemini API"""
    print("🧠 Генерация текста через Gemini API...")
    
    prompt = f"""Создай профессиональный пост для Telegram-канала о маркетинге и рекламе на тему: "{trend}"

Требования:
- Пост должен быть основан на реальных трендах и фактах 2024 года
- Добавь конкретные цифры, статистику и полезные инсайты
- Длина: 250-400 символов
- Стиль: профессиональный, но доступный и engaging
- Добавь эмодзи и призыв к обсуждению
- Сделай 2-3 абзаца для лучшей читаемости
- В конце добавь 3-4 релевантных хештега"""

    try:
        if client:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.8,
                    max_output_tokens=500
                )
            )
            generated_text = response.text.strip()
            print("✅ Текст успешно сгенерирован через Gemini SDK")
            return generated_text
        else:
            return generate_text_direct_api(trend)
        
    except Exception as e:
        print(f"❌ Ошибка Gemini SDK: {e}")
        return generate_text_direct_api(trend)

def generate_text_direct_api(trend):
    """Прямой запрос к Gemini API через HTTP"""
    print("🌐 Прямой запрос к Gemini API...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.8,
            "maxOutputTokens": 500
        }
    }
    
    try:
        response = requests.post(
            url, 
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            print("✅ Текст успешно сгенерирован через прямой API")
            return text.strip()
        else:
            print(f"❌ Ошибка прямого API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка прямого запроса: {e}")
        return None

def generate_image(trend):
    """Генерация картинки для поста"""
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
        
        try:
            # Попробуем использовать доступные шрифты
            font = ImageFont.load_default()
            # Или создадим простой шрифт
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42) if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") else font
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28) if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf") else font
        except:
            font = ImageFont.load_default()
            title_font = font
            text_font = font
        
        # Заголовок
        title = "АКТУАЛЬНЫЙ ТРЕНД"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        draw.text(((width - title_width) // 2, 120), title, font=title_font, fill=(255, 215, 0))
        
        # Основной текст
        wrapped_text = textwrap.fill(trend, width=25)
        draw.text((width // 2, 280), wrapped_text, font=text_font, fill=(255, 255, 255), anchor="mm")
        
        # Декоративные элементы
        draw.rectangle([40, 40, width-40, height-40], outline=(255, 215, 0), width=4)
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
        
    except Exception as e:
        print(f"❌ Ошибка генерации изображения: {e}")
        return None

def post_to_telegram(text, image_bytes=None):
    """Отправка поста в Telegram"""
    print("📤 Отправка в Telegram...")
    
    try:
        if image_bytes:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            files = {'photo': ('trend_image.png', image_bytes, 'image/png')}
            data = {
                'chat_id': TELEGRAM_CHANNEL_ID,
                'caption': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, files=files, data=data)
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHANNEL_ID,
                "text": text,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Пост успешно отправлен!")
            return True
        else:
            print(f"❌ Ошибка отправки: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return False

def main():
    """Основная функция"""
    print("🤖 Запуск генерации поста...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Получаем тренды из Google Trends
    trends = get_google_trends()
    print(f"📊 Найдены тренды: {trends}")
    
    if not trends:
        print("❌ Не удалось получить тренды")
        return 1
    
    # Выбираем случайный тренд
    selected_trend = random.choice(trends)
    print(f"🎯 Выбран тренд: {selected_trend}")
    
    # Генерируем текст через Gemini
    text = generate_text_with_gemini(selected_trend)
    
    if not text:
        print("❌ Не удалось сгенерировать текст")
        return 1
        
    print(f"📝 Текст поста:\n{text}")
    print(f"📏 Длина текста: {len(text)} символов")
    
    # Генерируем картинку
    image_bytes = generate_image(selected_trend)
    
    # Отправляем пост
    success = post_to_telegram(text, image_bytes)
    
    if success:
        print("🎉 Пост успешно опубликован!")
        return 0
    else:
        print("⚠️ Завершено с ошибками.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
