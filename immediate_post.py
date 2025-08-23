import os
import random
import requests
from pytrends.request import TrendReq

# --- Настройки с вашими данными (НЕБЕЗОПАСНО!) ---
# Используйте этот код только для теста, затем вернитесь к GitHub Secrets
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyA4MDuek8WeQen2s09C5F_kDkkq8rgN2Bk"

# Настройки для поиска трендов
NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram для бизнеса", "AI в рекламе"]

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
        
        if all_trends:
            return list(set(all_trends))
        else:
            return FALLBACK_TRENDS
    except Exception as e:
        print(f"Ошибка при работе с Google Trends: {e}")
        return FALLBACK_TRENDS

def generate_post_text(trend):
    """
    Генерирует текст поста с помощью Google Gemini API.
    """
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

def post_to_telegram(text):
    """
    Отправляет ТОЛЬКО текстовое сообщение в Telegram-канал.
    """
    print("Отправка текста в Telegram...")
    try:
        # Используем метод sendMessage вместо sendPhoto
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML"  # Позволяет использовать <b>жирный</b> и <i>курсивный</i> текст
        }
        response = requests.post(url, data=data)
        response.raise_for_status() # Проверка на ошибки HTTP
        
        print(f"Пост успешно отправлен! Ответ API: {response.json()}")
    except Exception as e:
        print(f"!!! Ошибка отправки в Telegram: {e}")
        # Выводим ответ сервера для отладки
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Ответ от сервера: {response.text}")

# --- Точка входа в скрипт ---
if __name__ == "__main__":
    print("--- ЗАПУСК ПУБЛИКАЦИИ (ТОЛЬКО ТЕКСТ) ---")
    
    # 1. Получаем тренды
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    print(f"Выбран тренд: {selected_trend}")
    
    # 2. Генерируем текст
    post_text = generate_post_text(selected_trend)
    print("Текст сгенерирован.")
    
    # 3. Отправляем в Telegram
    post_to_telegram(post_text)
    
    print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")
