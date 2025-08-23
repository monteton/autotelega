import random
import requests
from pytrends.request import TrendReq
import google.generativeai as genai

# Токены (тестовые)
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
GOOGLE_API_KEY = "AIzaSyCuWBy5qkUMO5oTAcIivzYSC0R9xiZjoUU"

NISHA = ["маркетинг", "реклама", "социальные сети"]
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
        return list(set(all_trends)) if all_trends else FALLBACK_TRENDS
    except Exception as e:
        print(f"Ошибка Google Trends: {e}")
        return FALLBACK_TRENDS

def generate_post_text_gemini(prompt, api_key):
    print("Генерация текста через Google Gemini API...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def post_to_telegram(text):
    print("Отправка в Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("Пост успешно отправлен!")
        return True
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
        return False

if __name__ == "__main__":
    print("Начинаю работу...")
    
    # Получаем тренды
    trends = get_google_trends()
    print(f"Найдены тренды: {trends}")
    
    # Выбираем случайный тренд
    selected_trend = random.choice(trends)
    print(f"Выбран тренд: {selected_trend}")
    
    # Генерируем пост
    prompt = f"Напиши короткий остроумный пост для Telegram-канала на тему '{selected_trend}'. Пост должен быть интересным и engaging."
    try:
        text = generate_post_text_gemini(prompt, GOOGLE_API_KEY)
        print(f"Сгенерированный текст: {text}")
    except Exception as e:
        text = f"🚀 {selected_trend}\n\nК сожалению, не удалось сгенерировать креативный текст, но тема очень перспективная! Что думаете об этом?"
        print(f"Ошибка при генерации текста: {e}")
    
    # Отправляем в Telegram
    success = post_to_telegram(text)
    
    if success:
        print("Готово! Пост успешно опубликован.")
    else:
        print("Завершено с ошибками.")
