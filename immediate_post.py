import os
import random
import requests
import urllib.parse
import time
from pytrends.request import TrendReq

# --- Настройки с вашими данными (НЕБЕЗОПАСНО!) ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

def get_google_trends():
    """Получает список актуальных поисковых запросов из Google Trends."""
    print("Запрос к Google Trends...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=120)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        
        all_trends = []
        for key in NISHA:
            if key in trends_data and trends_data[key]['top'] is not None:
                all_trends.extend([row['query'] for index, row in trends_data[key]['top'].iterrows()])
        
        return list(set(all_trends)) if all_trends else FALLBACK_TRENDS
    except Exception as e:
        print(f"Ошибка при работе с Google Trends: {e}")
        return FALLBACK_TRENDS

def generate_post_text(trend):
    """Генерирует текст поста с помощью бесплатного публичного API."""
    print(f"Генерация текста для тренда: '{trend}'...")
    prompt = (f"Напиши короткий пост для Telegram-канала о цифровом маркетинге. "
              f"Тема: '{trend}'. "
              f"Стиль: профессиональный, но легкий для чтения, можно с юмором. "
              f"Объем — от 200 до 1500 символов.")
    
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://free-unoficial-gpt4o-mini-api-g70n.onrender.com/chat/?query={encoded_prompt}"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "Не удалось сгенерировать текст.")
    except Exception as e:
        print(f"Ошибка при генерации текста: {e}")
        return "Ошибка при генерации текста."

def generate_image_from_text(post_text):
    """
    Генерирует изображение на основе готового текста поста, используя бесплатный API.
    """
    print("Генерация изображения из контекста поста...")
    
    # Создаем короткий промпт для картинки из первых предложений текста
    image_prompt = " ".join(post_text.split()[:30]) + ", digital art, vibrant colors, marketing concept"
    encoded_image_prompt = urllib.parse.quote(image_prompt)
    
    # URL бесплатного API для генерации изображений (на основе Stable Diffusion)
    url = f"https://ai-image-generator-api.justinjoy.workers.dev/?prompt={encoded_image_prompt}"
    
    try:
        response = requests.get(url, timeout=120) # Даем больше времени на генерацию картинки
        response.raise_for_status()
        
        # Этот API возвращает само изображение, а не ссылку на него
        print("Изображение успешно сгенерировано.")
        return response.content
    except Exception as e:
        print(f"Ошибка при генерации изображения: {e}. Использую заглушку.")
        # Если генерация не удалась, скачиваем картинку-заглушку
        return requests.get("https://via.placeholder.com/800x450.png?text=Image+Error").content

def post_to_telegram(text, image_data):
    """Отправляет пост с сгенерированным изображением в Telegram."""
    print("Отправка поста с картинкой в Telegram...")
    try:
        files = {"photo": ("post_image.jpg", image_data)}
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": text[:1024], "parse_mode": "HTML"}
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        print(f"Пост успешно отправлен! Ответ API: {response.json()}")
    except Exception as e:
        print(f"!!! Ошибка отправки в Telegram: {e}")

# --- Точка входа в скрипт ---
if __name__ == "__main__":
    print("--- ЗАПУСК ПОЛНОГО ЦИКЛА (ТЕКСТ + КАРТИНКА) ---")
    
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    
    post_text = generate_post_text(selected_trend)
    
    # Генерируем картинку уже после того, как получили текст
    image_data = generate_image_from_text(post_text)
    
    post_to_telegram(post_text, image_data)
    
    print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")
