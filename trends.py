from datetime import datetime
import random

class TrendsManager:
    def __init__(self):
        self.nisha = ["маркетинг", "реклама", "новости", "социальные сети", "digital", "SMM"]
    
    def get_google_trends(self):
        """Получение актуальных трендов (упрощенная версия)"""
        print("📊 Генерация актуальных трендов...")
        
        current_year = datetime.now().strftime("%Y")
        current_month = datetime.now().strftime("%B")
        
        # Создаем реалистичные тренды на основе ниши и текущей даты
        trends = []
        
        for niche in self.nisha:
            trends.extend([
                f"{niche} тренды {current_year}",
                f"новости {niche} {current_month}",
                f"{niche} стратегии",
                f"{niche} для бизнеса",
                f"новые технологии в {niche}",
                f"{niche} кейсы успеха"
            ])
        
        # Добавляем общие тренды
        trends.extend([
            f"digital маркетинг {current_year}",
            f"SMM тренды {current_year}",
            "нейросети в маркетинге",
            "видео контент стратегии",
            "мобильный маркетинг",
            "email маркетинг обновления",
            "брендинг в соцсетях",
            "контент стратегия",
            "аналитика маркетинга",
            "ROI оптимизация"
        ])
        
        # Перемешиваем и возвращаем
        random.shuffle(trends)
        return trends[:10]  # Возвращаем первые 10 трендов
