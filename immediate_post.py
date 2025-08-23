import random
import requests
from pytrends.request import TrendReq
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os
from datetime import datetime
import json

# Конфигурация
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
DEEPSEEK_API_KEY = "sk-53de7a895ba943f7b3a2c0873f130b2c"  # Замените на ваш ключ

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
    return [
        "тренды digital маркетинга 2024", "новости социальных сетей", 
        "SMM стратегии", "контент маркетинг", "таргетированная реклама"
    ]

def generate_text_with_deepseek(trend):
    """Генерация поста через DeepSeek API"""
    print("🧠 Генерация текста через DeepSeek...")
    
    # Промпт для генерации качественного поста
    prompt = f"""Создай engaging пост для Telegram-канала о маркетинге и рекламе на тему: "{trend}"

Требования:
- Стиль: легкий, профессиональный, с элементами юмора
- Длина: 180-280 символов
- Добавь эмодзи и призыв к обсуждению
- Сделай текст информативным и интересным
- Используй абзацы для читаемости

Формат:
Краткое введение
Основная информация
Вопрос к аудитории
Хештеги"""

    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": "Ты эксперт по маркетингу и SMM. Создавай качественные посты для Telegram."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 350,
            "temperature": 0.8,
            "top_p": 0.9
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            print("✅ Текст успешно сгенерирован через DeepSeek")
            return generated_text.strip()
        else:
            print(f"❌ Ошибка DeepSeek API: {response.status_code}")
            return generate_text_fallback(trend)
            
    except Exception as e:
        print(f"❌ Ошибка при запросе к DeepSeek: {e}")
        return generate_text_fallback(trend)

def generate_text_fallback(trend):
    """Резервная генерация текста если API не работает"""
    print("📝 Используем резервную генерацию текста...")
    
    fallback_texts = [
        f"🎯 {trend}\n\nИнтересный тренд в мире маркетинга! Что думаете об этом? 🤔\n\nОбсудим в комментариях? 👇\n\n#маркетинг #тренды #новости",
        
        f"🔥 {trend}\n\nСвежая тема для обсуждения! Как вы относитесь к этому тренду? 💫\n\nПоделитесь мнением в комментах! 💬\n\n#реклама #digital #обсуждение",
        
        f"🚀 {trend}\n\nНовое направление в digital-сфере! Уже пробовали внедрять? 📊\n\nДавайте обсудим практические кейсы! 🎯\n\n#SMM #соцсети #кейсы",
        
        f"💡 {trend}\n\nПерспективное направление для маркетологов! Какие мысли? 🌟\n\nЖду ваши идеи и опыт! ✍️\n\n#маркетинг #инсайты #опыт",
        
        f"📈 {trend}\n\nАктуальная тема для обсуждения! Как вам такой подход? ⚡\n\nРасскажите о своем опыте! ❤️\n\n#новости #аналитика #бизнес"
    ]
    
    return random.choice(fallback_texts)

def generate_image(trend):
    """Генерация картинки для поста"""
    try:
        width, height = 1000, 500
        image = Image.new('RGB', (width, height), color=(30, 30, 50))
        draw = ImageDraw.Draw(image)
        
        # Градиентный фон
        for i in range(height):
            r = int(30 + (i / height) * 25)
            g = int(30 + (i / height) * 20)
            b = int(50 + (i / height) * 25)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 42)
            text_font = ImageFont.truetype("arial.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Заголовок
        title = "АКТУАЛЬНЫЙ ТРЕНД"
        draw.text((width//2, 100), title, font=title_font, fill=(255, 215, 0), anchor="mm")
        
        # Основной текст
        wrapped_text = textwrap.fill(trend, width=30)
        draw.text((width//2, 250), wrapped_text, font=text_font, fill=(255, 255, 255), anchor="mm")
        
        # Декоративные элементы
        draw.rectangle([50, 50, width-50, height-50], outline=(255, 215, 0), width=3)
        
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
        
        response.raise_for_status()
        print("✅ Пост успешно отправлен!")
        return True
        
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
    
    # Выбираем случайный тренд
    selected_trend = random.choice(trends)
    print(f"🎯 Выбран тренд: {selected_trend}")
    
    # Генерируем текст через DeepSeek
    text = generate_text_with_deepseek(selected_trend)
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
    # Для получения бесплатного DeepSeek API ключа:
    # 1. Зарегистрируйтесь на https://platform.deepseek.com/
    # 2. Получите API ключ в личном кабинете
    # 3. Замените "your_deepseek_api_key_here" на ваш ключ
    
    exit_code = main()
    exit(exit_code)
