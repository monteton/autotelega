import os
import random
import requests
from pytrends.request import TrendReq

# --- Настройки с вашими данными для немедленного теста ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyA4MDuek8WeQen2s09C5F_kDkkq8rgN2Bk"
BING_API_KEY = None # Замените на ваш ключ или оставьте для получения картинки-заглушки

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram для бизнеса", "AI в рекламе"]

def get_google_trends():
    print("Запрос к Google Trends...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=120)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        
        all_trends = []
        for key in NISHA:
            if key in trends_data and trends_data[key]['top'] is not None:
                all_trends.extend([row['query'] for index, row in trends_data[key]['top'].iterrows()])
        
        if all_trends:
            return list(set(all_trends))
        else:
            return FALLBACK_TRENDS
    except Exception as e:
        print(f"Ошибка при работе с Google Trends: {e}")
        return FALLBACK_TRENDS

def generate_post_text(trend):
    print(f"Генерация текста для тренда: '{trend}'...")
    prompt = (f"Ты — остроумный SMM-менеджер. Напиши пост для Telegram-канала о маркетинге на тему '{trend}'. "
              "Стиль — легкий, ироничный, с юмором и эмодзи. Объем — от 200 до 1500 символов.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except Exception as e:
        print(f"Ошибка при генерации текста: {e}")
        return f"Не удалось сгенерировать текст для тренда: '{trend}'."

def get_image_url(trend):
    if not BING_API_KEY:
        return "https://via.placeholder.com/800x450.png?text=Marketing+News"
    # Логика для Bing API
    return "https://via.placeholder.com/800x450.png?text=Image+Search"

def post_to_telegram(text, image_url):
    print("Отправка в Telegram...")
    try:
        image_data = requests.get(image_url).content
        files = {"photo": ("image.jpg", image_data)}
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": text[:1024], "parse_mode": "HTML"}
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        print(f"Пост успешно отправлен! Ответ API: {response.json()}")
    except Exception as e:
        print(f"!!! Ошибка отправки в Telegram: {e}")

if __name__ == "__main__":
    print("--- ЗАПУСК НЕМЕДЛЕННОЙ ПУБЛИКАЦИИ ---")
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    post_text = generate_post_text(selected_trend)
    image_url = get_image_url(selected_trend)
    post_to_telegram(post_text, image_url)
    print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")

