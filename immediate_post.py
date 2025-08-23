import os
import random
import requests
from pytrends.request import TrendReq

# --- Настройки с вашими данными (НЕБЕЗОПАСНО!) ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyA4MDuek8WeQen2s09C5F_kDkkq8rgN2Bk"

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

def get_google_trends():
    print("Запрос к Google Trends...")
    # ... (эта функция остается без изменений) ...
    try:
        pytrends = TrendReq(hl='ru-RU', tz=120)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        all_trends = []
        for key in NISHA:
            if key in trends_data and trends_data[key]['top'] is not None:
                all_trends.extend([row['query'] for index, row in trends_data[key]['top'].iterrows()])
        return list(set(all_trends)) if all_trends else FALLBACK_TRENDS
    except Exception:
        return FALLBACK_TRENDS

def generate_post_text(trend):
    """
    Генерирует текст поста с помощью Google Gemini API.
    Промпт изменен, чтобы быть более нейтральным.
    """
    print(f"Генерация текста для тренда: '{trend}'...")
    # ИЗМЕНЕНИЕ ЗДЕСЬ: более нейтральный и бизнес-ориентированный промпт
    prompt = (f"Напиши короткий обзорный пост для Telegram-канала о цифровом маркетинге. "
              f"Тема: '{trend}'. "
              f"Стиль: профессиональный, но легкий для чтения. Объясни, почему эта тема важна для специалистов. "
              f"Избегай спорных или политических оценок. Объем — от 200 до 1500 символов.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        response_data = response.json()
        
        # ИЗМЕНЕНИЕ ЗДЕСЬ: Проверяем, не заблокирован ли ответ по соображениям безопасности
        if "candidates" not in response_data:
            block_reason = response_data.get("promptFeedback", {}).get("blockReason")
            error_message = f"Текст не сгенерирован. Причина блокировки от Google: {block_reason}"
            print(f"[ERROR] {error_message}")
            return error_message
            
        text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except requests.exceptions.HTTPError as http_err:
        print(f"!!! HTTP ошибка при генерации текста: {http_err}")
        print(f"Ответ от сервера: {http_err.response.text}")
        return f"Ошибка API Google при генерации текста для тренда: '{trend}'."
    except Exception as e:
        print(f"!!! Неизвестная ошибка при генерации текста: {e}")
        return f"Не удалось сгенерировать текст для тренда: '{trend}'."


def post_to_telegram(text):
    print("Отправка текста в Telegram...")
    # ... (эта функция остается без изменений) ...
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text, "parse_mode": "HTML"}
        response = requests.post(url, data=data)
        response.raise_for_status()
        print(f"Пост успешно отправлен! Ответ API: {response.json()}")
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

# --- Точка входа в скрипт ---
if __name__ == "__main__":
    print("--- ЗАПУСК ПУБЛИКАЦИИ (ТОЛЬКО ТЕКСТ, ФИНАЛЬНАЯ ВЕРСИЯ) ---")
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    post_text = generate_post_text(selected_trend)
    post_to_telegram(post_text)
    print("--- РАБОТА ЗАВЕРШЕНА ---")

