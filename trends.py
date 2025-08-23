from pytrends.request import TrendReq

class TrendsManager:
    def __init__(self):
        self.nisha = ["маркетинг", "реклама", "новости", "социальные сети", "digital", "SMM"]
        self.geo_location = 'RU'
    
    def get_google_trends(self):
        """Получение актуальных трендов из Google Trends"""
        print("📊 Запрос к Google Trends...")
        try:
            pytrends = TrendReq(hl='ru-RU', tz=180)
            pytrends.build_payload(self.nisha, timeframe='now 1-d', geo=self.geo_location)
            trends_data = pytrends.related_queries()
            
            all_trends = []
            for key in self.nisha:
                if key in trends_data and trends_data[key]['top'] is not None:
                    all_trends.extend([row['query'] for _, row in trends_data[key]['top'].iterrows()])
            
            # Фильтруем только релевантные тренды
            filtered_trends = [t for t in all_trends if any(niche in t.lower() for niche in self.nisha)]
            
            return list(set(filtered_trends)) if filtered_trends else self.get_fallback_trends()
            
        except Exception as e:
            print(f"❌ Ошибка Google Trends: {e}")
            return self.get_fallback_trends()
    
    def get_fallback_trends(self):
        """Резервные тренды если Google Trends не работает"""
        from datetime import datetime
        current_year = datetime.now().strftime("%Y")
        
        return [
            f"тренды digital маркетинга {current_year}",
            f"новости социальных сетей {current_year}",
            "SMM стратегии для малого бизнеса",
            "контент маркетинг для привлечения клиентов",
            "таргетированная реклама в соцсетях",
            "нейросети в маркетинге и рекламе"
        ]
