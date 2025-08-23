import os
import random
import requests
from pytrends.request import TrendReq

# --- 1. Настройки с вашими данными (НЕБЕЗОПАСНО!) ---
TELEGRAM_TOKEN = "8461091151:AAEd-mqGswAijmwFB0teeXeZFe-gtHfD-PI"
TELEGRAM_CHANNEL_ID = "-1002201089739"
PERPLEXITY_API_KEY = "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"
# !!! ВАЖНО: Вставьте сюда ваш настоящий ключ от OpenAI !!!
OPENAI_API_KEY = "sk-........................................" 

NISHA = ["маркетинг", "реклама", "новости", "социальные сети"]
GEO_LOCATION = 'RS'
FALLBACK_TRENDS = ["тренды в маркетинге 2025", "новые функции Telegram", "AI в рекламе"]

# --- 2. Функции ---

def get_google_trends():
    print("Запрос к Google Trends...")
    try:
        pytrends = TrendReq(hl='ru-RU', tz=120)
        pytrends.build_payload(NISHA, timeframe='now 1-d', geo=GEO_LOCATION)
        trends_data = pytrends.related_queries()
        all_trends = [row['query'] for key in NISHA if key in trends_data and trends_data[key]['top'] is not None for index, row in trends_data[key]['top'].iterrows()]
        return list(set(all_trends)) if all_trends else FALLBACK_TRENDS
    except Exception as e:
        print(f"Ошибка Google Trends: {e}. Использую запасные темы.")
        return FALLBACK_TRENDS

def generate_text_with_perplexity(trend):
    """
    Генерирует текст поста с помощью Perplexity API.
    """
    print(f"Генерация текста через Perplexity для тренда: '{trend}'...")
    
    prompt = (f"Ты — AI-ассистент для Telegram-канала о маркетинге. "
              f"Напиши короткий, легкий и остроумный пост на тему: '{trend}'. "
              f"Стиль: профессиональный, но с юмором, используй эмодзи. Объем 200-1500 символов.")
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-small-online",
        "messages": [
            {"role": "system", "content": "You are an AI assistant for a marketing Telegram channel."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        text = response.json()['choices'][0]['message']['content']
        print("Текст успешно сгенерирован через Perplexity.")
        return text
    except Exception as e:
        print(f"!!! Ошибка Perplexity API: {e}")
        return f"Не удалось сгенерировать текст для '{trend}'."

def generate_image_with_openai(post_text):
    """
    Генерирует изображение на основе текста поста с помощью OpenAI DALL-E 3.
    """
    image_prompt = " ".join(post_text.split()[:30]) + ", digital art, vibrant colors, marketing concept illustration"
    print(f"Генерация изображения через OpenAI с промптом: '{image_prompt[:50]}...'")
    
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "dall-e-3", "prompt": image_prompt, "n": 1, "size": "1024x1024", "quality": "standard"}
    
    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()['data'][0]['url']
        return requests.get(image_url).content
    except Exception as e:
        print(f"!!! Ошибка OpenAI (изображение): {e}. Использую заглушку.")
        return b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'

def post_to_telegram(text, image_data):
    """Отправляет пост с изображением в Telegram."""
    print("Отправка поста в Telegram...")
    try:
        files = {"photo": ("post_image.jpg", image_data)}
        data = {"chat_id": TELEGRAM_CHANNEL_ID, "caption": text[:1024], "parse_mode": "HTML"}
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        print(f"Пост успешно отправлен! Ответ Telegram: {response.json()}")
    except Exception as e:
        print(f"!!! Ошибка отправки в Telegram: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Ответ от сервера: {response.text}")

# --- Точка входа ---
if __name__ == "__main__":
    if "sk-" not in OPENAI_API_KEY:
        print("!!! КРИТИЧЕСКАЯ ОШИБКА: Вы не вставили ваш OpenAI API ключ в код. !!!")
        print("Пожалуйста, замените 'sk-........................................' на ваш настоящий ключ.")
    else:
        print("--- ЗАПУСК ФИНАЛЬНОГО ТЕСТА С PERPLEXITY + OPENAI ---")
        trends = get_google_trends()
        selected_trend = random.choice(trends)
        
        post_text = generate_text_with_perplexity(selected_trend)
        
        if "Не удалось сгенерировать" not in post_text:
            image_data = generate_image_with_openai(post_text)
            post_to_telegram(post_text, image_data)
        else:
            # Если текст не сгенерирован, отправляем только текст ошибки
            post_to_telegram(post_text, b'') 
            
        print("--- РАБОТА СКРИПТА ЗАВЕРШЕНА ---")
