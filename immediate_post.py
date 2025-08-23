import os
import random
import requests
from pytrends.request import TrendReq

# --- Настройки с вашими данными (НЕБЕЗОПАСНО!) ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyA4MDuek8WeQen2s09C5F_kDkkq8rgN2Bk"
BING_API_KEY = None 

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram для бизнеса", "AI в рекламе"]

# --- Все функции остаются без изменений ---

def get_google_trends():
    print("[DEBUG] Шаг 1: Запрашиваю тренды из Google...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=120)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        
        all_trends = []
        for key in NISHA:
            if key in trends_data and trends_data[key]['top'] is not None:
                all_trends.extend([row['query'] for index, row in trends_data[key]['top'].iterrows()])
        
        if all_trends:
            unique_trends = list(set(all_trends))
            print(f"[DEBUG] Найдено {len(unique_trends)} трендов. Пример: {unique_trends[0]}")
            return unique_trends
        else:
            print("[DEBUG] Google Trends ничего не вернул. Использую запасные темы.")
            return FALLBACK_TRENDS
    except Exception as e:
        print(f"[DEBUG] ОШИБКА в Google Trends: {e}. Использую запасные темы.")
        return FALLBACK_TRENDS

def generate_post_text(trend):
    print(f"[DEBUG] Шаг 2: Генерирую текст для тренда: '{trend}'...")
    prompt = (f"Ты — остроумный SMM-менеджер. Напиши пост для Telegram-канала о маркетинге на тему '{trend}'. "
              "Стиль — легкий, ироничный, с юмором и эмодзи. Объем — от 200 до 1500 символов.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            text = response.json()["candidates"]["content"]["parts"]["text"]
            print("[DEBUG] Текст успешно сгенерирован.")
            return text
        else:
            print(f"[DEBUG] ОШИБКА от Google API. Статус: {response.status_code}, Ответ: {response.text}")
            return f"Не удалось сгенерировать текст для '{trend}'."
    except Exception as e:
        print(f"[DEBUG] КРИТИЧЕСКАЯ ОШИБКА при генерации текста: {e}")
        return f"Ошибка сети при генерации текста."

def get_image_url(trend):
    print(f"[DEBUG] Шаг 3: Ищу изображение для '{trend}'...")
    if not BING_API_KEY:
        print("[DEBUG] Ключ Bing не найден, использую заглушку.")
        return "https://via.placeholder.com/800x450.png?text=Marketing+News"
    # Логика для Bing остаётся прежней
    return "https://via.placeholder.com/800x450.png?text=Image+Search"

def post_to_telegram(text, image_url):
    print("[DEBUG] Шаг 4: Отправляю пост в Telegram...")
    print(f"[DEBUG] ID канала: {TELEGRAM_CHANNEL_ID}")
    print(f"[DEBUG] Токен бота: ...{TELEGRAM_TOKEN[-4:]}") # Показываем только последние 4 символа для безопасности
    
    try:
        image_data = requests.get(image_url).content
        print("[DEBUG] Изображение успешно скачано.")
        
        files = {"photo": ("image.jpg", image_data)}
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": text[:1024], "parse_mode": "HTML"}
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        
        response = requests.post(url, data=data, files=files)
        
        # ЭТО САМАЯ ВАЖНАЯ ЧАСТЬ: мы выводим ответ от Telegram, даже если он кажется успешным
        print(f"[DEBUG] Ответ от сервера Telegram. Статус код: {response.status_code}")
        print(f"[DEBUG] Полный ответ от Telegram: {response.text}")

        if response.json().get("ok"):
            print("[SUCCESS] Telegram подтвердил успешную отправку!")
        else:
            print("[ERROR] Telegram вернул ошибку в ответе!")
            
    except Exception as e:
        print(f"[DEBUG] КРИТИЧЕСКАЯ ОШИБКА при отправке в Telegram: {e}")

# --- Точка входа в скрипт ---
if __name__ == "__main__":
    print("--- ЗАПУСК ОТЛАДОЧНОЙ ВЕРСИИ ---")
    post_to_telegram("Это тестовое сообщение для проверки связи с Telegram.", "https://via.placeholder.com/800x450.png?text=Test+Message")
    print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")

