import os
import random
import requests
import urllib.parse
from pytrends.request import TrendReq

# --- Настройки (без API ключей) ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
NISHA = ["маркетинг", "реклама", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

# --- Функции ---

def get_google_trends():
    """Получает список актуальных поисковых запросов из Google Trends."""
    print("Запрос к Google Trends...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=120)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        all_trends = [row['query'] for key in NISHA if key in trends_data and trends_data[key]['top'] is not None for index, row in trends_data[key]['top'].iterrows()]
        return list(set(all_trends)) if all_trends else FALLBACK_TRENDS
    except Exception as e:
        print(f"Ошибка Google Trends: {e}. Использую запасные темы.")
        return FALLBACK_TRENDS

def generate_post_text(trend):
    """
    Генерирует текст поста с помощью надежного народного API.
    """
    print(f"Генерация текста для тренда: '{trend}'...")
    prompt = (f"Напиши короткий, остроумный пост для Telegram-канала о цифровом маркетинге. "
              f"Тема: '{trend}'. "
              f"Стиль: профессиональный, но легкий и с юмором. "
              f"Объем 200-1500 символов.")
    
    url = "https://api.logan.oveo.workers.dev/"
    params = {"message": prompt}
    
    try:
        response = requests.get(url, params=params, timeout=90)
        response.raise_for_status()
        # Этот API возвращает текст в поле 'response'
        text = response.json().get("response", "API не вернул текст.")
        print("Текст успешно сгенерирован.")
        return text
    except Exception as e:
        error_message = f"Ошибка при генерации текста: {e}"
        print(f"!!! {error_message}")
        return error_message

def generate_image_data(post_text):
    """
    Генерирует изображение на основе текста, используя бесплатный API от Pollinations.ai.
    """
    print("Генерация изображения из контекста поста...")
    # Создаем короткий, но емкий промпт для картинки
    image_prompt = " ".join(post_text.split()[:25]) + ", cinematic, hyper-detailed, marketing, digital art"
    encoded_prompt = urllib.parse.quote(image_prompt)
    
    # URL API, который генерирует изображение по текстовому описанию
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    
    print(f"Запрос к Pollinations.ai с промптом: {image_prompt[:50]}...")
    
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        print("Изображение успешно сгенерировано.")
        return response.content
    except Exception as e:
        print(f"Ошибка генерации изображения: {e}. Использую встроенную заглушку.")
        # Надежная встроенная заглушка, которая не требует сети
        return b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'

def post_to_telegram(text, image_data):
    """Отправляет пост с изображением в Telegram."""
    print("Отправка поста в Telegram...")
    try:
        files = {"photo": ("post_image.jpg", image_data)}
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": text[:1024], "parse_mode": "HTML"}
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        print(f"Пост успешно отправлен! Ответ API: {response.json()}")
    except Exception as e:
        print(f"!!! Ошибка отправки в Telegram: {e}")

# --- Точка входа ---
if __name__ == "__main__":
    print("--- ЗАПУСК С НАРОДНЫМИ API (ТЕКСТ + КАРТИНКА) ---")
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    post_text = generate_post_text(selected_trend)
    image_data = generate_image_data(post_text)
    post_to_telegram(post_text, image_data)
    print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")

