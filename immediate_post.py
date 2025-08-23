import random
import requests
from pytrends.request import TrendReq

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

def generate_post_text_gemini_flash(prompt, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    print("Полный ответ API:", result)  # Для отладки

    candidate = result['candidates'][0]
    content = candidate.get('content')

    # content — список или словарь
    if isinstance(content, list):
        part = content
    else:
        part = content

    # parts — список, берем первый элемент
    if isinstance(part, dict) and 'parts' in part:
        parts_list = part['parts']
        if isinstance(parts_list, list) and len(parts_list) > 0:
            text = parts_list.get('text', '')
        else:
            text = ''
    elif isinstance(part, dict):
        text = part.get('text', '')
    else:
        text = ''

    return text

def post_to_telegram(text):
    print("Отправка поста в Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    print("Пост успешно отправлен!")

if __name__ == "__main__":
    print("Начинаю работу...")
    trends = get_google_trends()
    selected_trend = random.choice(trends)
    prompt = f"Напиши короткий остроумный пост для Telegram-канала на тему '{selected_trend}'."
    try:
        text = generate_post_text_gemini_flash(prompt, GOOGLE_API_KEY)
    except Exception as e:
        text = f"Ошибка при генерации текста: {e}"
        print(text)
    post_to_telegram(text)
    print("Готово.")
