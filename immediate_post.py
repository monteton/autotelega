import random
import requests
import time
import schedule
from datetime import datetime
from pytrends.request import TrendReq
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# Конфигурация
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
TIMEZONE = 'Europe/Belgrade'

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
    """Генерация текста поста с использованием открытых API"""
    try:
        # Попробуем использовать ChatGPT через неофициальный API
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer sk-your-free-key",  # Нужно получить бесплатный ключ
            "Content-Type": "application/json"
        }
        
        prompt = f"""Напиши короткий engaging пост для Telegram на тему '{trend}'. 
        Стиль: легкий, с юмором, неформальный. Длина: 150-300 символов. 
        Добавь эмодзи и призыв к обсуждению."""
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
            
    except Exception:
        pass  # Если API не работает, используем локальную генерацию
    
    # Локальная генерация текста
    templates = [
        f"🔥 {trend} — вот это поворот! Что думаете? 🤔\n\nОбсудим в комментах? 👇",
        f"🚀 {trend} — тренд сезона! А вы в теме? 💫\n\nЖду ваши мнения! 💬",
        f"📈 {trend} — все только об этом и говорят! А вы? 🎯\n\nДавайте поспорим? 😄",
        f"💡 {trend} — гениально или переоценено? Ваше мнение! 🤷‍♂️\n\nПишите в комментарии! ✍️",
        f"🌟 {trend} — вот это новость! Как вам? 🎉\n\nЖду ваши реакции! ❤️"
    ]
    
    return random.choice(templates)

def generate_image(trend):
    """Генерация картинки для поста"""
    try:
        # Создаем простое изображение с текстом
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color=(45, 45, 65))
        draw = ImageDraw.Draw(image)
        
        # Загружаем шрифт (можно использовать стандартный)
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Форматируем текст
        wrapped_text = textwrap.fill(trend, width=30)
        
        # Рисуем текст
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        draw.text((x, y), wrapped_text, font=font, fill=(255, 215, 0))
        
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
            files = {'photo': ('image.png', image_bytes, 'image/png')}
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

def create_and_post():
    """Создание и публикация поста"""
    print(f"\n⏰ Запуск в {datetime.now().strftime('%H:%M:%S')}")
    
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
    else:
        print("⚠️ Завершено с ошибками.")

def main():
    """Основная функция"""
    print("🤖 Бот запущен!")
    print("⏰ Расписание: 8:00, 10:00, 14:00, 17:00, 19:00 (время Белграда)")
    
    # Настраиваем расписание
    schedule.every().day.at("08:00").do(create_and_post)
    schedule.every().day.at("10:00").do(create_and_post)
    schedule.every().day.at("14:00").do(create_and_post)
    schedule.every().day.at("17:00").do(create_and_post)
    schedule.every().day.at("19:00").do(create_and_post)
    
    # Первый запуск сразу
    print("🚀 Первый запуск...")
    create_and_post()
    
    # Бесконечный цикл
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверка каждую минуту

if __name__ == "__main__":
    # Установите зависимости:
    # pip install pytrends requests schedule Pillow
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
