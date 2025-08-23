import random
import requests
from pytrends.request import TrendReq
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os
from datetime import datetime
import json
import base64

# Конфигурация
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GROK_API_KEY = "xai-RW56kLsDPrR7Wwm4xj9QDXFkeVYVIFQ2BpnP507yuziqcWPUQTwGnxgzKVVqzWwFo3oOCopD3OOyStp1"

NISHA = ["маркетинг", "реклама", "новости", "социальные сети", "digital", "SMM"]
GEO_LOCATION = 'RU'

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

def generate_text_with_grok(trend):
    """Генерация поста через Grok API"""
    print("🧠 Генерация текста через Grok API...")
    
    prompt = f"""Создай профессиональный пост для Telegram-канала о маркетинге и рекламе на тему: "{trend}"

Требования:
- Пост должен быть основан на реальных трендах 2024-2025 года
- Добавь конкретные цифры, статистику и полезные инсайты
- Длина: 250-400 символов
- Стиль: профессиональный, но доступный и engaging
- Добавь эмодзи и призыв к обсуждению
- Сделай 2-3 абзаца для лучшей читаемости
- В конце добавь 3-4 релевантных хештега
- Используй только реальные факты и данные"""

    try:
        url = "https://api.x.ai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "role": "system", 
                    "content": "Ты эксперт по digital-маркетингу с 10-летним опытом. Создавай качественные, информативные посты с конкретными данными и статистикой."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "grok-4-latest",
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            print("✅ Текст успешно сгенерирован через Grok API")
            return generated_text.strip()
        else:
            print(f"❌ Ошибка Grok API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при запросе к Grok: {e}")
        return None

def generate_image_with_grok(trend):
    """Генерация картинки через Grok API"""
    print("🎨 Генерация изображения через Grok API...")
    
    try:
        url = "https://api.x.ai/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "grok-image-gen-latest",
            "prompt": f"Создай изображение для поста о маркетинге на тему '{trend}'. Стиль: профессиональный, современный, с элементами digital-арта. Добавь иконки связанные с маркетингом, соцсетями, аналитикой.",
            "size": "1024x1024",
            "quality": "standard",
            "n": 1
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Скачиваем изображение
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code == 200:
                img_bytes = io.BytesIO(img_response.content)
                print("✅ Изображение успешно сгенерировано через Grok API")
                return img_bytes
            else:
                print(f"❌ Ошибка загрузки изображения: {img_response.status_code}")
                return None
        else:
            print(f"❌ Ошибка генерации изображения: {response.status_code} - {response.text}")
            return generate_fallback_image(trend)
            
    except Exception as e:
        print(f"❌ Ошибка при генерации изображения: {e}")
        return generate_fallback_image(trend)

def generate_fallback_image(trend):
    """Резервная генерация изображения"""
    print("🖼️ Создаем резервное изображение...")
    
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
        
        # Используем стандартный шрифт
        font = ImageFont.load_default()
        
        # Заголовок
        title = "АКТУАЛЬНЫЙ ТРЕНД"
        draw.text((width//2, 100), title, font=font, fill=(255, 215, 0), anchor="mm")
        
        # Основной текст
        wrapped_text = textwrap.fill(trend, width=25)
        draw.text((width//2, 250), wrapped_text, font=font, fill=(255, 255, 255), anchor="mm")
        
        # Декоративные элементы
        draw.rectangle([50, 50, width-50, height-50], outline=(255, 215, 0), width=3)
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
        
    except Exception as e:
        print(f"❌ Ошибка генерации резервного изображения: {e}")
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

def verify_telegram_credentials():
    """Проверка корректности Telegram credentials"""
    print("🔍 Проверка Telegram credentials...")
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Бот: {bot_info['result']['first_name']} (@{bot_info['result']['username']})")
            
            # Проверка доступа к каналу
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat"
            data = {"chat_id": TELEGRAM_CHANNEL_ID}
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                chat_info = response.json()
                print(f"✅ Канал: {chat_info['result']['title']}")
                return True
            else:
                print(f"❌ Ошибка доступа к каналу: {response.text}")
                return False
        else:
            print(f"❌ Неверный Telegram token: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки Telegram: {e}")
        return False

def main():
    """Основная функция"""
    print("🤖 Запуск генерации поста...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверяем Telegram credentials
    if not verify_telegram_credentials():
        print("❌ Проблема с Telegram credentials")
        return 1
    
    # Получаем тренды из Google Trends
    trends = get_google_trends()
    print(f"📊 Найдены тренды: {trends}")
    
    if not trends:
        print("❌ Не удалось получить тренды")
        return 1
    
    # Выбираем случайный тренд
    selected_trend = random.choice(trends)
    print(f"🎯 Выбран тренд: {selected_trend}")
    
    # Генерируем текст через Grok
    text = generate_text_with_grok(selected_trend)
    
    if not text:
        print("❌ Не удалось сгенерировать текст")
        return 1
        
    print(f"📝 Текст поста:\n{text}")
    print(f"📏 Длина текста: {len(text)} символов")
    
    # Генерируем картинку через Grok
    image_bytes = generate_image_with_grok(selected_trend)
    
    # Отправляем пост
    success = post_to_telegram(text, image_bytes)
    
    if success:
        print("🎉 Пост успешно опубликован!")
        return 0
    else:
        print("⚠️ Завершено с ошибками.")
        return 1

if __name__ == "__main__":
    # Установите зависимости:
    # pip install pytrends requests Pillow
    
    exit_code = main()
    exit(exit_code)
