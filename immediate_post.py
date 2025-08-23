import os
import random
import requests
from pytrends.request import TrendReq

# --- 1. Настройки (безопасное получение из секретов) ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Новый ключ

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

# --- 2. Функции ---

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

def generate_content_with_openai(trend):
    """
    Генерирует текст и промпт для картинки с помощью OpenAI API.
    """
    print(f"Генерация контента через OpenAI для тренда: '{trend}'...")
    
    # Промпт для создания текста и идеи для картинки одним запросом
    prompt = (f"Ты — AI-ассистент для Telegram-канала о маркетинге. "
              f"1. Напиши короткий, легкий и остроумный пост на тему: '{trend}'. "
              f"2. После текста, с новой строки, напиши краткий, яркий промпт на английском языке для генератора изображений (DALL-E), который иллюстрирует пост. "
              f"Формат: IMAGE_PROMPT: [your prompt here]")
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini", # Самая быстрая и дешевая модель
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Разделяем текст и промпт для картинки
        parts = content.split("IMAGE_PROMPT:")
        post_text = parts[0].strip()
        image_prompt = parts[1].strip() if len(parts) > 1 else f"digital art for the topic: {trend}"
        
        return post_text, image_prompt
    except Exception as e:
        print(f"Ошибка OpenAI (текст): {e}")
        return f"Не удалось сгенерировать текст для '{trend}'.", "abstract marketing concept, digital art"

def generate_image_with_openai(prompt):
    """
    Генерирует изображение с помощью DALL-E 3.
    """
    print(f"Генерация изображения с промптом: '{prompt}'...")
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard" # Дешевле, чем hd
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()['data']['url']
        return requests.get(image_url).content
    except Exception as e:
        print(f"Ошибка OpenAI (изображение): {e}. Использую заглушку.")
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
        print("Пост успешно отправлен!")
    except Exception as e:
        print(f"!!! Ошибка отправки в Telegram: {e}")

# --- Точка входа ---
if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("Критическая ошибка: не найден OPENAI_API_KEY в секретах.")
    else:
        print("--- ЗАПУСК СТАБИЛЬНОЙ ВЕРСИИ С OPENAI ---")
        trends = get_google_trends()
        selected_trend = random.choice(trends)
        
        post_text, image_prompt = generate_content_with_openai(selected_trend)
        image_data = generate_image_with_openai(image_prompt)
        
        post_to_telegram(post_text, image_data)
        print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")
