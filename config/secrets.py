import os
from dotenv import load_dotenv

def load_secrets():
    """Загрузка секретов из .env файла или переменных окружения"""
    # Пробуем загрузить из .env файла (для локального запуска)
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    # Берем из переменных окружения (для GitHub Actions)
    secrets = {
        'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN'),
        'TELEGRAM_CHANNEL_ID': os.getenv('TELEGRAM_CHANNEL_ID'),
        'GROK_API_KEY': os.getenv('GROK_API_KEY')
    }
    
    # Проверяем что все секреты загружены
    missing_secrets = []
    for key, value in secrets.items():
        if not value:
            missing_secrets.append(key)
    
    if missing_secrets:
        raise ValueError(f"Missing required secrets: {', '.join(missing_secrets)}")
    
    return secrets
