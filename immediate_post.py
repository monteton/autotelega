import os
import random
import requests
import urllib.parse
from pytrends.request import TrendReq

# --- Настройки ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

# --- Функции ---

def get_google_trends():
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

def generate_text_from_api(prompt, api_url_template):
    """Универсальная функция для запроса к текстовому API."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = api_url_template.format(encoded_prompt)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json().get("response", "API не вернул текст.")

def generate_post_text(trend):
    """Генерирует текст, пробуя два разных бесплатных API."""
    prompt = (f"Напиши короткий пост для Telegram-канала о цифровом маркетинге. Тема: '{trend}'. "
              f"Стиль: профессиональный, но легкий, можно с юмором. Объем 200-1500 символов.")
    
    # Список API для попыток
    api_urls = [
        "https://free-unoficial-gpt4o-mini-api-g70n.onrender.com/chat/?query={}",
        "https://api.logan.oveo.workers.dev/?message={}" # Запасной API
    ]
    
    for i, api_url in enumerate(api_urls):
        try:
            print(f"Попытка №{i+1}: генерация текста через API {api_url.split('/')[2]}...")
            text = generate_text_from_api(prompt, api_url)
            if "API не вернул текст" not in text:
                print("Текст успешно сгенерирован.")
                return text
        except Exception as e:
            print(f"API №{i+1} не ответил. Ошибка: {e}")
            
    return f"Не удалось сгенерировать текст для тренда '{trend}', все API недоступны."

def generate_image_from_text(post_text):
    """Генерирует изображение на основе текста."""
    print("Генерация изображения из контекста поста...")
    image_prompt = " ".join(post_text.split()[:30]) + ", digital art, vibrant colors"
    encoded_image_prompt = urllib.parse.quote(image_prompt)
    url = f"https://ai-image-generator-api.justinjoy.workers.dev/?prompt={encoded_image_prompt}"
    
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        print("Изображение успешно сгенерировано.")
        return response.content
    except Exception as e:
        print(f"Ошибка генерации изображения: {e}. Использую встроенную заглушку.")
        # Встроенная заглушка: прозрачный GIF 1x1 пиксель. Не требует сети.
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
    print("--- ЗАПУСК НАДЕЖНОЙ ВЕРСИИ (ТЕКСТ + КАРТИНКА) ---")
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    post_text = generate_post_text(selected_trend)
    image_data = generate_image_from_text(post_text)
    post_to_telegram(post_text, image_data)
    print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")

