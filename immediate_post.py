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

NISHA = ["маркетинг", "реклама", "новости", "социальные сети", "digital", "SMM"]
GEO_LOCATION = 'RU'  # Россия вместо RS
TIMEZONE = 'Europe/Moscow'

FALLBACK_TRENDS = [
    "тренды digital маркетинга", "новости социальных сетей", "SMM стратегии 2024",
    "контент маркетинг тренды", "таргетированная реклама", "нейросети в маркетинге",
    "email маркетинг", "вирусный контент", "брендинг стратегии", "аналитика маркетинга"
]

def get_google_trends():
    """Получение трендов из Google Trends"""
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
        
        return list(set(filtered_trends)) if filtered_trends else FALLBACK_TRENDS
    except Exception as e:
        print(f"❌ Ошибка Google Trends: {e}")
        return FALLBACK_TRENDS

def generate_text(trend):
    """Генерация качественного текста поста"""
    
    # Более качественные шаблоны с конкретным контентом
    templates = [
        # Маркетинг
        f"🎯 {trend}\n\nЧто это значит для бизнеса в 2024? 🤔\n\n• Повышение конверсии на 30%\n• Увеличение охвата аудитории\n• Новые возможности для брендов\n\nУже используете в своей стратегии? 💼",
        
        f"📈 {trend}\n\nСтатистика показывает рост на 45% за последний квартал! 📊\n\nКлючевые преимущества:\n✅ Улучшение вовлеченности\n✅ Рост узнаваемости бренда\n✅ Увеличение продаж\n\nКак вам такие результаты? 🚀",
        
        # Реклама
        f"🔥 {trend}\n\nНовый тренд в digital-рекламе! 💻\n\nПочему это работает:\n• Высокий CTR\n• Низкая стоимость клика\n• Таргетирование по интересам\n\nУже тестировали? Делитесь опытом! 👇",
        
        f"💡 {trend}\n\nИнновационный подход к рекламе! 🌟\n\nРезультаты внедрения:\n📱 +67% мобильного трафика\n💬 +89% вовлеченности\n💰 -35% стоимости привлечения\n\nВаше мнение? 🤔",
        
        # Соцсети
        f"🚀 {trend}\n\nВзрывной рост в соцсетях! 📱\n\nТоп-платформы для реализации:\n• Instagram Reels\n• Telegram Channels\n• YouTube Shorts\n• VK Клипы\n\nГде уже пробовали? 🎬",
        
        f"🌟 {trend}\n\nТренд который изменит SMM в 2024! 💫\n\nОсновные фишки:\n🎨 Визуальный контент\n🤖 AI-генерация\n📊 Аналитика в реальном времени\n\nКак внедряете в свои проекты? 💼",
        
        # Новости
        f"📢 {trend}\n\nСвежие данные и инсайты! 🔍\n\nЧто важно знать:\n• Изменения в алгоритмах\n• Новые инструменты\n• Кейсы успешных компаний\n\nОбсуждаем в комментариях! 💬",
        
        f"🎉 {trend}\n\nПрорыв в digital-индустрии! ⚡\n\nОсновные преимущества:\n✅ Простота внедрения\n✅ Быстрые результаты\n✅ Высокая окупаемость\n\nУже в планах на 2024? 📅"
    ]
    
    # Выбираем шаблон в зависимости от темы
    trend_lower = trend.lower()
    if any(word in trend_lower for word in ['маркетинг', 'marketing', 'бизнес']):
        selected_template = random.choice(templates[:2])
    elif any(word in trend_lower for word in ['реклама', 'advertising', 'ads']):
        selected_template = random.choice(templates[2:4])
    elif any(word in trend_lower for word in ['социальн', 'smm', 'social', 'instagram', 'telegram']):
        selected_template = random.choice(templates[4:6])
    else:
        selected_template = random.choice(templates[6:8])
    
    # Добавляем хештеги
    hashtag_groups = [
        ["#маркетинг", "#бизнес", "#тренды2024"],
        ["#реклама", "#digital", "#продвижение"],
        ["#smm", "#соцсети", "#контент"],
        ["#новости", "#аналитика", "#кейсы"]
    ]
    
    hashtags = " ".join(random.choice(hashtag_groups))
    text = f"{selected_template}\n\n{hashtags}"
    
    return text

def generate_image(trend):
    """Генерация картинки для поста"""
    try:
        # Создаем привлекательное изображение
        width, height = 1000, 500
        image = Image.new('RGB', (width, height), color=(25, 25, 40))  # Темный фон
        draw = ImageDraw.Draw(image)
        
        # Градиентный фон
        for i in range(height):
            r = int(25 + (i / height) * 30)
            g = int(25 + (i / height) * 20)
            b = int(40 + (i / height) * 30)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        # Заголовок
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 42)
            text_font = ImageFont.truetype("arial.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Заголовок
        title = "НОВЫЙ ТРЕНД"
        draw.text((width//2, 100), title, font=title_font, fill=(255, 215, 0), anchor="mm")
        
        # Основной текст
        wrapped_text = textwrap.fill(trend, width=30)
        draw.text((width//2, 250), wrapped_text, font=text_font, fill=(255, 255, 255), anchor="mm")
        
        # Декоративные элементы
        draw.rectangle([50, 50, width-50, height-50], outline=(255, 215, 0), width=3)
        
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
    exit_code = main()
    exit(exit_code)
