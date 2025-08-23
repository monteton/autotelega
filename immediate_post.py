import os
import random
import requests
from pytrends.request import TrendReq

# --- Настройки ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyAhzC4PY_RyFN7DqjQWUG5ftkIZk0DWNrM"  # Ваш ключ Google Generative Language API

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

def get_google_trends():
    print("Запрос к Google Trends...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=120)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        all_trends = []
        for key in NISHA:
            if key in trends_data and trends_data[key]['top'] is not None:
                all_trends.extend([row['query'] for _, row in trends_data[key]['top'].iterrows()])
        if all_trends:
            print(f"Найдено {len(set(all_trends))} уникальных трендов.")
            return list(set(all_trends))
        else:
            print("Google Trends не вернул результатов. Используем запасные темы.")
            return FALLBACK_TRENDS
    except Exception as e:
        print(f"Ошибка Google Trends: {e}. Использую запасные темы.")
        return FALLBACK_TRENDS

def generate_post_text(trend):
    print(f"Генерация текста для тренда: '{trend}'...")
    prompt = (
        f"Ты — остроумный и легкий в общении SMM-менеджер для Telegram-канала о маркетинге.\n"
        f"Напиши короткий пост по теме '{trend}' в неформальном, юмористическом стиле, объемом от 200 до 1500 символов."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"]["text"]
        print("Текст успешно сгенерирован.")
        return text
    except Exception as e:
        print(f"Ошибка генерации текста: {e}")
        return f"Не удалось сгенерировать текст для тренда '{trend}'."

def post_to_telegram(text):
    print("Отправка поста в Telegram...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML"  # Позволяет использовать HTML-разметку (жирный шрифт, ссылки и т.п.)
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        print(f"Пост успешно отправлен! Ответ Telegram: {response.json()}")
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

if __name__ == "__main__":
    print("--- Запуск генерации и публикации поста ---")
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    post_text = generate_post_text(selected_trend)
    post_to_telegram(post_text)
    print("--- Работа скрипта завершена ---")
