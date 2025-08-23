import os
from dotenv import load_dotenv

def load_secrets():
    """Загрузка секретов из .env файла"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    
    secrets = {
        'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN'),
        'TELEGRAM_CHANNEL_ID': os.getenv('TELEGRAM_CHANNEL_ID'),
        'GROK_API_KEY': os.getenv('GROK_API_KEY')
    }
    
    # Проверяем что все секреты загружены
    for key, value in secrets.items():
        if not value:
            raise ValueError(f"Missing required secret: {key}")
    
    return secrets
