import os
import random
import requests
from pytrends.request import TrendReq

# Настройки (получаем из секретов GitHub Actions)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]

def get_trends():
    pytrends = TrendReq(hl='ru-RU', tz=360) # tz 360 - это Москва (UTC+3), близко к Белграду
    pytrends.build_payload(NISHA, timeframe='now 1-d', geo='RS') # RS - Сербия
    trends = pytrends.related_queries()
    all_trends = []
    for key in NISHA:
        if trends[key] is not None and trends[key]['top'] is not None:
            all_trends.extend([row['query'] for index, row in trends[key]['top'].iterrows()])
    return list(set(all_trends)) if all_trends else ["тренды в маркетинге 2025"] # Запасной вариант

def generate_text(trend):
    prompt = f"Напиши короткий (от 100 до 4096 символов) пост в легком, можно с юмором стиле по теме '{trend}' для Telegram-канала о маркетинге, рекламе, новостях или соцсетях."
    # ... (код для генерации текста остается прежним)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200 and "candidates" in response.json():
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Не удалось сгенерировать текст для тренда: {trend}. Ошибка API."


def generate_image_url(trend):
    bing_api_key = os.getenv("BING_IMAGE_API_KEY")
    if not bing_api_key:
        return "https://via.placeholder.com/600x400.png?text=Image+Generation+Failed" # Заглушка
    url = "https://api.bing.microsoft.com/v7.0/images/search"
    params = {"q": f"{trend} digital art illustration", "count": 1, "safeSearch": "Moderate"}
    headers = {"Ocp-Apim-Subscription-Key": bing_api_key}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200 and response.json().get("value"):
        return response.json()["value"]["contentUrl"]
    else:
        return "https://via.placeholder.com/600x400.png?text=Image+Not+Found" # Заглушка

def post_to_telegram(text, img_url):
    img_data = requests.get(img_url).content
    files = {"photo": ("image.jpg", img_data)}
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "caption": text[:1024], # У Telegram есть лимит на подпись к фото
        "parse_mode": "HTML"
    }
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    response = requests.post(url, data=data, files=files)
    return response.json()

# Основная логика, которая будет выполняться при каждом запуске GitHub Actions
if __name__ == "__main__":
    print("Запуск задачи...")
    trends = get_trends()
    if not trends:
        print("Тренды не найдены. Используем тему по умолчанию.")
        trends = ["новые функции Telegram для бизнеса"]
    
    trend = random.choice(trends)
    print(f"Выбран тренд: {trend}")
    
    text = generate_text(trend)
    print("Текст сгенерирован.")
    
    img_url = generate_image_url(trend)
    print(f"URL изображения: {img_url}")

    result = post_to_telegram(text, img_url)
    print("Пост отправлен!")
    print(f"Ответ от Telegram API: {result}")

