import random
from datetime import datetime
from secrets import load_secrets
from trends import TrendsManager
from ai_generator import AIGenerator
from telegram_client import TelegramClient

def main():
    print("🤖 Запуск генерации поста...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Загрузка секретов
        print("🔧 Инициализация системы...")
        secrets = load_secrets()
        
        # Инициализация клиентов
        print("🔧 Инициализация клиентов...")
        telegram_client = TelegramClient(secrets['TELEGRAM_TOKEN'], secrets['TELEGRAM_CHANNEL_ID'])
        ai_generator = AIGenerator(secrets['GROK_API_KEY'])
        trends_manager = TrendsManager()
        
        # Проверка credentials
        print("🔧 Проверка учетных данных...")
        if not telegram_client.verify_credentials():
            print("❌ Проблема с Telegram credentials")
            return 1
        
        # Получаем тренды
        print("🔧 Получение трендов...")
        trends = trends_manager.get_google_trends()
        print(f"📊 Найдены тренды: {trends}")
        
        if not trends:
            print("❌ Не удалось получить тренды")
            return 1
        
        # Выбираем тренд
        selected_trend = random.choice(trends)
        print(f"🎯 Выбран тренд: {selected_trend}")
        
        # Генерируем текст
        print("🔧 Генерация текста...")
        text = ai_generator.generate_text(selected_trend)
        if not text:
            print("❌ Не удалось сгенерировать текст")
            return 1
        
        print(f"📝 Текст поста:\n{text}")
        print(f"📏 Длина текста: {len(text)} символов")
        
        # Генерируем изображение
        print("🔧 Генерация изображения...")
        image_bytes = ai_generator.generate_image(selected_trend)
        
        # Отправляем пост
        print("🔧 Отправка поста...")
        success = telegram_client.send_post(text, image_bytes)
        
        if success:
            print("🎉 Пост успешно опубликован!")
            return 0
        else:
            print("⚠️ Завершено с ошибками.")
            return 1
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
