import random
import requests
from pytrends.request import TrendReq
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os
from datetime import datetime
import json
import googlesearch
from bs4 import BeautifulSoup
import time

# Конфигурация
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
DEEPSEEK_API_KEY = "sk-7626d74465214867ad209d783d89d01d"

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
        
        return list(set(filtered_trends)) if filtered_trends else []
        
    except Exception as e:
        print(f"❌ Ошибка Google Trends: {e}")
        return []

def search_trend_info(trend):
    """Поиск информации о тренде в интернете"""
    print(f"🔍 Поиск информации о: {trend}")
    
    try:
        # Ищем новости по теме
        search_results = []
        for url in googlesearch.search(f"{trend} новости 2024", num=3, stop=3, pause=2):
            search_results.append(url)
        
        # Парсим информацию с первых двух страниц
        trend_info = []
        for url in search_results[:2]:
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Извлекаем заголовки и первые абзацы
                paragraphs = soup.find_all('p')
                for p in paragraphs[:5]:
                    text = p.get_text().strip()
                    if len(text) > 100 and any(keyword in text.lower() for keyword in ['маркетинг', 'реклама', 'социальн', 'digital', 'smm']):
                        trend_info.append(text)
                        if len(trend_info) >= 3:
                            break
                
                if len(trend_info) >= 3:
                    break
                    
            except Exception as e:
                continue
        
        return " ".join(trend_info) if trend_info else ""
        
    except Exception as e:
        print(f"❌ Ошибка поиска информации: {e}")
        return ""

def generate_text_with_deepseek(trend, context=""):
    """Генерация поста через DeepSeek API с контекстом"""
    print("🧠 Генерация текста через DeepSeek...")
    
    if context:
        prompt = f"""На основе этой информации о тренде "{trend}":
{context}

Создай профессиональный пост для Telegram-канала о маркетинге.

Требования:
- Используй ТОЛЬКО информацию из предоставленного контекста
- Добавь конкретные цифры и факты если они есть
- Сделай пост информативным и интересным
- Длина: 250-400 символов
- Стиль: профессиональный, но доступный
- Добавь эмодзи и призыв к обсуждению
- Не придумывай информацию которой нет в контексте"""
    else:
        prompt = f"""Создай профессиональный пост для Telegram-канала о маркетинге на тему: "{trend}"

Основа пост на реальных данных и трендах 2024 года. 
Добавь конкретные цифры, факты и полезную информацию.
Длина: 250-400 символов. Стиль: профессиональный с элементами легкости."""

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
                    "content": "Ты эксперт по digital-маркетингу. Создавай только фактчекинг посты на основе предоставленной информации. Не придумывай факты."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.8
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            print("✅ Текст успешно сгенерирован через DeepSeek")
            return generated_text.strip()
        else:
            print(f"❌ Ошибка DeepSeek API: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при запросе к DeepSeek: {e}")
        return None

def generate_image(trend):
    """Генерация картинки для поста"""
    try:
        width, height = 1000, 500
        image = Image.new('RGB', (width, height), color=(20, 30, 40))
        draw = ImageDraw.Draw(image)
        
        # Градиентный фон
        for i in range(height):
            r = int(20 + (i / height) * 25)
            g = int(30 + (i / height) * 20)
            b = int(40 + (i / height) * 25)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 42)
            text_font = ImageFont.truetype("arial.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Заголовок
        title = "АКТУАЛЬНЫЙ ТРЕНД"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        draw.text(((width - title_width) // 2, 100), title, font=title_font, fill=(255, 215, 0))
        
        # Основной текст
        wrapped_text = textwrap.fill(trend, width=25)
        bbox = draw.textbbox((0, 0), wrapped_text, font=text_font)
        text_height = bbox[3] - bbox[1]
        draw.text((width // 2, 280), wrapped_text, font=text_font, fill=(255, 255, 255), anchor="mm")
        
        # Декоративные элементы
        draw.rectangle([40, 40, width-40, height-40], outline=(255, 215, 0), width=3)
        
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
    if not trends:
        print("❌ Не удалось получить тренды")
        return 1
        
    print(f"📊 Найдены тренды: {trends}")
    
    # Выбираем случайный тренд
    selected_trend = random.choice(trends)
    print(f"🎯 Выбран тренд: {selected_trend}")
    
    # Ищем информацию о тренде
    trend_info = search_trend_info(selected_trend)
    
    # Генерируем текст через DeepSeek
    text = generate_text_with_deepseek(selected_trend, trend_info)
    
    # Если генерация не удалась, пробуем без контекста
    if not text:
        print("🔄 Повторная попытка генерации без контекста...")
        text = generate_text_with_deepseek(selected_trend)
    
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
    # Установите зависимости: 
    # pip install pytrends requests Pillow beautifulsoup4 google-search-results
    
    exit_code = main()
    exit(exit_code)
