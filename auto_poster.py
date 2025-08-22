import os
import random
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from pytrends.request import TrendReq

# Настройки
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyA4MDuek8WeQen2s09C5F_kDkkq8rgN2Bk"
TZ = "Europe/Belgrade"

POST_TIMES = ["08:00", "10:00", "14:00", "17:00", "19:00"]
NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]

def get_trends():
    pytrends = TrendReq(hl='ru-RU', tz=2)
    pytrends.build_payload(NISHA, timeframe='now 1-d', geo='RS')
    trends = pytrends.related_queries()
    all_trends = []
    for key in NISHA:
        if trends[key]['top'] is not None:
            all_trends += [row['query'] for row in trends[key]['top'].to_dict('records')]
    return list(set(all_trends))

def generate_text(trend):
    prompt = f"Напиши короткий (от 100 до 4096 символов) пост в легком, можно с юмором стиле по теме '{trend}' для Telegram-канала о маркетинге, рекламе, новостях или соцсетях."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, json=data, headers=headers)
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return text[:4096]

def generate_image(trend):
    # Используй сервис генерации изображений (например, Bing Image Creator или DALL·E)
    # Тут пример для Bing Image Creator (замени на свой API/метод)
    bing_api_key = os.getenv("BING_IMAGE_API_KEY")
    url = "https://api.bing.microsoft.com/v7.0/images/search"
    params = {"q": trend, "count": 1, "safeSearch": "Moderate"}
    headers = {"Ocp-Apim-Subscription-Key": bing_api_key}
    response = requests.get(url, headers=headers, params=params)
    img_url = response.json()["value"][0]["contentUrl"]
    return img_url

def post_to_telegram(text, img_url):
    # Скачаем картинку
    img_data = requests.get(img_url).content
    files = {"photo": ("image.jpg", img_data)}
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "caption": text,
        "parse_mode": "HTML"
    }
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    requests.post(url, data=data, files=files)

def job():
    print(f"[{datetime.now()}] Запуск задачи...")
    trends = get_trends()
    if not trends:
        print("Нет трендов.")
        return
    trend = random.choice(trends)
    text = generate_text(trend)
    img_url = generate_image(trend)
    post_to_telegram(text, img_url)
    print("Пост отправлен!")

def schedule_jobs():
    scheduler = BlockingScheduler(timezone=TZ)
    for t in POST_TIMES:
        hour, minute = map(int, t.split(":"))
        scheduler.add_job(job, "cron", hour=hour, minute=minute)
    print("Планировщик стартует...")
    scheduler.start()

if __name__ == "__main__":
    schedule_jobs()