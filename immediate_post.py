import random
import requests
from pytrends.request import TrendReq
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os
from datetime import datetime

# Конфигурация
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'

FALLBACK_TRENDS = [
    "тренды маркетинга 2025", "новости digital", "SMM стратегии",
    "контент маркетинг", "таргетированная реклама", "тренды соцсетей",
    "нейросети в маркетинге", "email рассылки", "вирусный контент"
]

def get_google_trends():
    """Получение трендов из Google Trends"""
    print("📊 Запрос к Google Trends...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=180)  # UTC+3 для Белграда
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        
        all_trends = []
        for key in NISHA:
            if key in trends_data and trends_data[key]['top'] is not None:
                all_trends.extend([row['query'] for _, row in trends_data[key]['top'].iterrows()])
        
        return list(set(all_trends)) if all_trends else FALLBACK_TRENDS
    except Exception as e:
        print(f"❌ Ошибка Google Trends: {e}")
        return FALLBACK_TRENDS

def generate_text(trend):
    """Генерация текста поста"""
    # Локальная генерация текста с юмором
    templates = [
        f"🔥 {trend} — вот это поворот! Что думаете? 🤔\n\nОбсудим в комментах? 👇",
        f"🚀 {trend} — тренд сезона! А вы в теме? 💫\n\nЖду ваши мнения! 💬",
        f"📈 {trend} — все только об этом и говорят! А вы? 🎯\n\nДавайте поспорим? 😄",
        f"💡 {trend} — гениально или переоценено? Ваше мнение! 🤷‍♂️\n\nПишите в комментарии! ✍️",
        f"🌟 {trend} — вот это новость! Как вам? 🎉\n\nЖду ваши реакции! ❤️",
        f"🎯 {trend} — хайп или действительно важно? Решаем вместе! 🤔\n\nВаши мысли?",
        f"💥 {trend} — взрывная тема! Уже пробовали? 🚀\n\nДелитесь опытом!",
        f"📱 {trend} — новый тренд в соцсетях! Успеете за хайпом? 🌊\n\nКак вам?",
        f"🤖 {trend} — будущее уже здесь! Готовы? ⚡\n\nОбсудим?",
        f"🎨 {trend} — креативный подход или банальность? Ваше мнение! 🎭"
    ]
    
    text = random.choice(templates)
    
    # Добавляем хештеги
    hashtags = ["#маркетинг", "#реклама", "#новости", "#соцсети", "#тренды", "#digital"]
    random_hashtags = random.sample(hashtags, 3)
    text += f"\n\n{' '.join(random_hashtags)}"
    
    return text

def generate_image(trend):
    """Генерация картинки для поста"""
    try:
        # Создаем простое изображение с текстом
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color=(45, 45, 65))
        draw = ImageDraw.Draw(image)
        
        # Пробуем разные шрифты
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 36)
            except:
                font = ImageFont.load_default()
        
        # Форматируем текст
        wrapped_text = textwrap.fill(trend, width=25)
        
        # Рисуем текст
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        draw.text((x, y), wrapped_text, font=font, fill=(255, 215, 0))
        
        # Добавляем декоративные элементы
        draw.rectangle([50, 50, width-50, height-50], outline=(255, 215, 0), width=2)
        
        # Сохраняем в байтовый поток
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
            # Отправка с картинкой
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            files = {'photo': ('trend_image.png', image_bytes, 'image/png')}
            data = {
                'chat_id': TELEGRAM_CHANNEL_ID,
                'caption': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, files=files, data=data)
        else:
            # Отправка только текста
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
    
    # Получаем тренды
    trends = get_google_trends()
    print(f"📊 Найдены тренды: {trends}")
    
    # Выбираем случайный тренд
    selected_trend = random.choice(trends)
    print(f"🎯 Выбран тренд: {selected_trend}")
    
    # Генерируем текст
    text = generate_text(selected_trend)
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
    # Установите зависимости:
    # pip install pytrends requests Pillow
    
    exit_code = main()
    exit(exit_code)
