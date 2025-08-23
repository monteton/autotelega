import os
import random
import requests
import urllib.parse
from pytrends.request import TrendReq

# --- Настройки с вашими данными (НЕБЕЗОПАСНО!) ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"

# Настройки для поиска трендов
NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

def get_google_trends():
    """
    Получает список актуальных поисковых запросов из Google Trends.
    """
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

def generate_post_text_free_api(trend):
    """
    Генерирует текст поста с помощью бесплатного публичного API.
    Не требует ключа, но может быть менее стабилен.
    """
    print(f"Генерация текста через бесплатный API для тренда: '{trend}'...")
    
    # Формируем промпт для нейросети
    prompt = (f"Напиши короткий пост для Telegram-канала о цифровом маркетинге. "
              f"Тема: '{trend}'. "
              f"Стиль: профессиональный, но легкий для чтения, можно с юмором. "
              f"Объем — от 200 до 1500 символов.")
    
    # Кодируем промпт для безопасной передачи в URL
    encoded_prompt = urllib.parse.quote(prompt)
    
    # URL бесплатного API
    url = f"https://free-unoficial-gpt4o-mini-api-g70n.onrender.com/chat/?query={encoded_prompt}"
    
    try:
        response = requests.get(url, timeout=60) # Увеличим время ожидания до 60 секунд
        response.raise_for_status()
        
        response_data = response.json()
        
        if "response" in response_data:
            text = response_data["response"]
            print("Текст успешно сгенерирован через бесплатный API.")
            return text
        else:
            error_message = f"Бесплатный API вернул неожиданный ответ: {response_data}"
            print(f"[ERROR] {error_message}")
            return error_message

    except requests.exceptions.RequestException as e:
        error_message = f"Сетевая ошибка при обращении к бесплатному API: {e}"
        print(f"!!! {error_message}")
        return error_message

def post_to_telegram(text):
    """
    Отправляет текстовое сообщение в Telegram-канал.
    """
    print("Отправка текста в Telegram...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text, "parse_mode": "HTML"}
        response = requests.post(url, data=data)
        response.raise_for_status()
        print(f"Пост успешно отправлен! Ответ API: {response.json()}")
    except Exception as e:
        print(f"!!! Ошибка отправки в Telegram: {e}")

# --- Точка входа в скрипт ---
if __name__ == "__main__":
    print("--- ЗАПУСК ПУБЛИКАЦИИ (ТЕКСТ ЧЕРЕЗ НОВЫЙ API) ---")
    
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    
    post_text = generate_post_text_free_api(selected_trend)
    
    post_to_telegram(post_text)
    
    print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")

