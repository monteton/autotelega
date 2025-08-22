import os
import random
import requests
from pytrends.request import TrendReq

# --- 1. Настройки с вашими данными (НЕБЕЗОПАСНО!) ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyA4MDuek8WeQen2s09C5F_kDkkq8rgN2Bk"
# Для теста изображений я использую заглушку, т.к. у вас нет BING_API_KEY
# Если у вас есть ключ, вставьте его сюда, иначе будет картинка-заглушка.
BING_API_KEY = None 

# Настройки для поиска трендов
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
            print(f"Найдено {len(set(all_trends))} уникальных трендов.")
            return list(set(all_trends))
        else:
            print("Google Trends не вернул результатов. Используем запасные темы.")
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
        candidates = response.json().get("candidates")
        if candidates and candidates[0].get("content"):
            text = candidates["content"]["parts"]["text"]
            print("Текст успешно сгенерирован.")
            return text
        else:
            print(f"API не вернул контент. Ответ: {response.json()}")
            return f"Не удалось сгенерировать текст для тренда: '{trend}'."
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при генерации текста: {e}")
        return f"Сетевая ошибка при генерации текста для '{trend}'."

def get_image_url(trend):
    print(f"Поиск изображения для тренда: '{trend}'...")
    if not BING_API_KEY:
        print("API-ключ для Bing не найден. Используется изображение-заглушка.")
        return "https://via.placeholder.com/800x450.png?text=Marketing+News"
    
    # ... (логика поиска изображения остаётся прежней) ...
    return "https://via.placeholder.com/800x450.png?text=Image+Search"


def post_to_telegram(text, image_url):
    print("Подготовка к отправке в Telegram...")
    try:
        image_data = requests.get(image_url).content
        files = {"photo": ("image.jpg", image_data)}
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "caption": text[:1024],
            "parse_mode": "HTML"
        }
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        
        print("Пост успешно отправлен в Telegram!")
        print(f"Ответ от Telegram API: {response.json()}")
    except Exception as e:
        print(f"!!! НЕ УДАЛОСЬ ОТПРАВИТЬ ПОСТ В TELEGRAM. Ошибка: {e}")
        # Печатаем ответ от Telegram API для отладки
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Ответ от сервера: {response.text}")


if __name__ == "__main__":
    if not all([TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID, GOOGLE_API_KEY]):
        print("Критическая ошибка: один из ключей не указан в коде.")
    else:
        print("Все ключи вписаны в код. Начинаем тестовый запуск.")
        trends_list = get_google_trends()
        selected_trend = random.choice(trends_list)
        
        post_text = generate_post_text(selected_trend)
        post_image_url = get_image_url(selected_trend)
        
        post_to_telegram(post_text, post_image_url)
        print("Тестовый запуск завершен.")
