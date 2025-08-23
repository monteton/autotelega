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
DEEPSEEK_API_KEY = "sk-7626d74465214867ad209d783d89d01d"  # Замените на реальный ключ

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
        "нейросети в маркетинге и рекламе",
        "email маркетинг для ecommerce",
        "вирусный контент в 2024",
        "брендинг стратегии для стартапов",
        "аналитика маркетинга и метрики"
    ]

def generate_text_with_deepseek(trend):
    """Генерация поста через DeepSeek API"""
    print("🧠 Генерация текста через DeepSeek...")
    
    # Улучшенный промпт
    prompt = f"""Создай профессиональный пост для Telegram-канала о маркетинге на тему: "{trend}"

Пост должен содержать:
1. Заголовок с эмодзи
2. 2-3 предложения полезной информации по теме
3. Конкретные цифры или факты (придумай реалистичные)
4. Вопрос к аудитории с призывом к обсуждению
5. 3-4 релевантных хештега

Стиль: профессиональный, но легкий. Длина: 200-350 символов."""

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
                    "content": "Ты эксперт по digital-маркетингу с 10-летним опытом. Создавай качественные, информативные посты с конкретными данными."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 400,
            "temperature": 0.7,
            "top_p": 0.8
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            print("✅ Текст успешно сгенерирован через DeepSeek")
            return generated_text.strip()
        else:
            print(f"❌ Ошибка DeepSeek API: {response.status_code} - {response.text}")
            return generate_quality_text(trend)
            
    except Exception as e:
        print(f"❌ Ошибка при запросе к DeepSeek: {e}")
        return generate_quality_text(trend)

def generate_quality_text(trend):
    """Качественная генерация текста без API"""
    print("🎨 Создаем качественный пост локально...")
    
    # Разные шаблоны для разных типов трендов
    trend_lower = trend.lower()
    
    if any(word in trend_lower for word in ['тренд', 'тренды', '2024', '2025']):
        templates = [
            f"🚀 {trend}\n\nСогласно исследованию, внедрение таких стратегий увеличивает конверсию на 35-40%! 📈\n\nКлючевые преимущества:\n• Рост вовлеченности на 60%\n• Снижение стоимости лида на 25%\n• Увеличение ROI до 300%\n\nУже тестируете в своих проектах? 💼\n\n#маркетинг #тренды #бизнес",
            
            f"🎯 {trend}\n\nИнновационный подход, который уже используют 67% успешных компаний! 💡\n\nРезультаты внедрения:\n📊 +45% к охвату аудитории\n💬 +80% к вовлеченности\n💰 -30% к стоимости привлечения\n\nКак вам такие показатели? 🤔\n\n#digital #стратегия #рост",
            
            f"🔥 {trend}\n\nНовое направление, которое меняет правила игры в digital! 🌐\n\nСтатистика показывает:\n✅ 89% маркетологов уже используют\n✅ ROI в среднем 450%\n✅ Время внедрения: 2-3 недели\n\nПланируете внедрять? 🚀\n\n#новости #инновации #маркетинг"
        ]
    
    elif any(word in trend_lower for word in ['новости', 'news', 'события']):
        templates = [
            f"📢 {trend}\n\nВажное обновление в мире digital! Компании уже сообщают о росте продаж на 50% после внедрения. 🎉\n\nОсновные изменения:\n• Новые алгоритмы платформ\n• Обновленные инструменты аналитики\n• Улучшенные возможности таргетинга\n\nКак это повлияет на вашу стратегию? 📈\n\n#новости #digital #обновления",
            
            f"🌟 {trend}\n\nСвежие данные от ведущих экспертов индустрии! 📊\n\nКлючевые инсайты:\n• Рынок вырос на 40% за квартал\n• Новые возможности для малого бизнеса\n• Изменения в потребительском поведении\n\nВаше мнение об этих изменениях? 💬\n\n#аналитика #бизнес #новости"
        ]
    
    elif any(word in trend_lower for word in ['социальн', 'smm', 'social', 'instagram', 'telegram', 'вконтакте']):
        templates = [
            f"📱 {trend}\n\nПрорыв в SMM! Лучшие практики показывают рост вовлеченности на 85%! 🚀\n\nТоп-платформы для реализации:\n• Instagram Reels +120% охвата\n• Telegram Channels +200% подписчиков\n• VK Клипы +150% просмотров\n\nКакие платформы используете вы? 🎯\n\n#smm #соцсети #продвижение",
            
            f"💫 {trend}\n\nНовая эра в социальных сетях! Компании сообщают о 3x росте конверсии. 📈\n\nОсновные тренды:\n🎬 Видеоконтент доминирует\n🤖 AI-генерация контента\n📊 Real-time аналитика\n\nКак адаптируете стратегию? 💼\n\n#соцсети #контент #тренды"
        ]
    
    else:
        templates = [
            f"🎯 {trend}\n\nПрофессиональный подход, который увеличивает эффективность кампаний на 65%! 📊\n\nКлючевые метрики улучшения:\n• CTR: +40-50%\n• CPC: -35%\n• Конверсия: +55%\n• ROI: до 400%\n\nУже есть опыт внедрения? Делитесь кейсами! 👇\n\n#маркетинг #реклама #результаты",
            
            f"🚀 {trend}\n\nСтратегия, которую используют 78% успешных брендов! 💡\n\nРезультаты внедрения:\n📈 Рост продаж на 45-60%\n👥 Увеличение лояльности на 70%\n🎯 Улучшение таргетинга на 80%\n\nКак оцениваете потенциал? 🤔\n\n#стратегия #бренд #growth",
            
            f"🔥 {trend}\n\nИнновация в digital-маркетинге! Ранние внедренцы сообщают о 2.5x ROI. 💰\n\nПреимущества подхода:\n✅ Быстрое внедрение (1-2 недели)\n✅ Низкий порог входа\n✅ Высокая масштабируемость\n✅ Подходит для малого бизнеса\n\nИнтересно попробовать? 🎯\n\n#инновации #маркетинг #стартап"
        ]
    
    return random.choice(templates)

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
            title_font = ImageFont.truetype("arialbd.ttf", 46)
            text_font = ImageFont.truetype("arial.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Заголовок
        title = "АКТУАЛЬНЫЙ ТРЕНД"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        draw.text(((width - title_width) // 2, 120), title, font=title_font, fill=(255, 215, 0))
        
        # Основной текст
        wrapped_text = textwrap.fill(trend, width=25)
        bbox = draw.textbbox((0, 0), wrapped_text, font=text_font)
        text_height = bbox[3] - bbox[1]
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
    
    # Генерируем текст
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
    exit_code = main()
    exit(exit_code)
