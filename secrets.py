import os

def load_secrets():
    """Загрузка секретов из переменных окружения"""
    print("🔍 Загрузка секретов из environment variables...")
    
    secrets = {
        'TELEGRAM_TOKEN': os.environ.get('TELEGRAM_TOKEN'),
        'TELEGRAM_CHANNEL_ID': os.environ.get('TELEGRAM_CHANNEL_ID'),
        'GROK_API_KEY': os.environ.get('GROK_API_KEY')
    }
    
    # Выводим информацию о загруженных секретах (без значений)
    for key in secrets:
        if secrets[key]:
            print(f"✅ {key}: loaded (length: {len(secrets[key])})")
        else:
            print(f"❌ {key}: missing")
    
    # Проверяем что все секреты загружены
    missing_secrets = []
    for key, value in secrets.items():
        if not value:
            missing_secrets.append(key)
    
    if missing_secrets:
        raise ValueError(f"Missing required secrets: {', '.join(missing_secrets)}")
    
    return secrets
