# ============================================
# BACKEND - app/analysis/price_analyzer.py
# Motor de analiză prețuri cu ML
# ============================================

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sklearn.linear_model import LinearRegression

from app.database import database, listings, car_models, dotari

class PriceAnalyzer:
    """Analizează prețurile folosind date reale și ML"""
    
    def __init__(self):
        self.model = LinearRegression()
    
    async def calculate_optimal_price(
        self,
        marca: str,
        model: str,
        an: int,
        km: int,
        dotari_list: List[str]
    ) -> Dict:
        """
        Calculează prețul optim bazat pe date reale
        
        Args:
            marca: Marca mașinii
            model: Modelul mașinii
            an: Anul fabricației
            km: Kilometri parcurși
            dotari_list: Lista dotărilor
            
        Returns:
            Dict cu strategii de pricing și date piață
        """
        # 1. Obține date piață
        market_data = await self.analyze_market(marca, model, an, km)
        
        # 2. Calculează prețul de bază
        base_price = await self._calculate_base_price(marca, model, an, km, market_data)
        
        # 3. Calculează valoarea dotărilor
        dotari_value = await self._calculate_dotari_value(dotari_list, an)
        
        # 4. Calculează factorul premium
        premium_factor = await self._calculate_premium_factor(dotari_list)
        
        # 5. Preț final ajustat
        final_price = (base_price + dotari_value) * premium_factor
        
        # 6. Generează strategii de pricing
        strategies = self._generate_pricing_strategies(final_price, market_data)
        
        return {
            'pret_rapid': strategies['pret_rapid'],
            'pret_optim': strategies['pret_optim'],
            'pret_negociere': strategies['pret_negociere'],
            'pret_maxim': strategies['pret_maxim'],
            'valoare_dotari': dotari_value,
            'market_data': market_data
        }
    
    async def analyze_market(
        self,
        marca: str,
        model: str,
        an: int,
        km: int
    ) -> Dict:
        """
        Analizează piața pentru o mașină specifică
        
        Returns:
            Dict cu statistici piață
        """
        # Obține anunțuri similare (±2 ani, ±30k km)
        query = listings.select().where(
            (listings.c.marca == marca) &
            (listings.c.model == model) &
            (listings.c.an.between(an - 2, an + 2)) &
            (listings.c.km.between(max(0, km - 30000), km + 30000)) &
            (listings.c.este_activ == True)
        )
        
        results = await database.fetch_all(query)
        
        if not results:
            raise ValueError(f"Nu s-au găsit suficiente date pentru {marca} {model}")
        
        # Calculează statistici
        prices = [r['pret'] for r in results]
        kms = [r['km'] for r in results]
        anos = [r['an'] for r in results]
        
        # Statistici de bază
        total_listings = len(prices)
        price_mean = np.mean(prices)
        price_median = np.median(prices)
        price_std = np.std(prices)
        price_min = np.min(prices)
        price_max = np.max(prices)
        
        # Percentile
        percentile_25 = np.percentile(prices, 25)
        percentile_75 = np.percentile(prices, 75)
        
        # Calculează zile pe piață
        days_on_market = []
        now = datetime.now()
        for r in results:
            if r['data_publicare']:
                days = (now - r['data_publicare']).days
                days_on_market.append(days)
        
        days_on_market_avg = np.mean(days_on_market) if days_on_market else 0
        
        # Distribuție regională
        regional_distribution = {}
        for r in results:
            loc = r['locatie']
            regional_distribution[loc] = regional_distribution.get(loc, 0) + 1
        
        return {
            'total_listings': total_listings,
            'price_mean': round(price_mean, 2),
            'price_median': round(price_median, 2),
            'price_std': round(price_std, 2),
            'price_min': round(price_min, 2),
            'price_max': round(price_max, 2),
            'percentile_25': round(percentile_25, 2),
            'percentile_75': round(percentile_75, 2),
            'days_on_market_avg': round(days_on_market_avg, 1),
            'regional_distribution': regional_distribution
        }
    
    async def _calculate_base_price(
        self,
        marca: str,
        model: str,
        an: int,
        km: int,
        market_data: Dict
    ) -> float:
        """Calculează prețul de bază folosind depreciere și date piață"""
        
        # Încearcă să obții prețul de bază din DB
        query = car_models.select().where(
            (car_models.c.marca == marca) &
            (car_models.c.model == model)
        )
        car_data = await database.fetch_one(query)
        
        if car_data:
            # Calculează depreciere standard
            years_old = datetime.now().year - an
            base_price = car_data['pret_baza_nou']
            depreciation_rate = car_data['depreciere_an']
            
            # Aplicăm depreciere compusă
            depreciated_price = base_price * ((1 - depreciation_rate) ** years_old)
            
            # Ajustare pentru kilometri (scade ~0.5% per 10,000 km)
            km_factor = 1 - (km / 10000) * 0.005
            final_price = depreciated_price * km_factor
            
        else:
            # Fallback: folosește mediana pieței
            final_price = market_data['price_median']
            
            # Ajustare pentru kilometri
            avg_km = 15000 * (datetime.now().year - an)  # 15k km/an medie
            km_diff = km - avg_km
            
            if km_diff > 0:
                # Mai mulți km = scădere preț
                final_price *= (1 - (km_diff / 100000) * 0.05)
            else:
                # Mai puțini km = creștere preț
                final_price *= (1 + abs(km_diff) / 100000 * 0.03)
        
        return max(final_price, market_data['price_min'] * 0.8)
    
    async def _calculate_dotari_value(
        self,
        dotari_list: List[str],
        an: int
    ) -> float:
        """Calculează valoarea dotărilor cu depreciere"""
        total_value = 0.0
        years_old = datetime.now().year - an
        
        for dotare_nume in dotari_list:
            query = dotari.select().where(
                dotari.c.nume == dotare_nume
            )
            dotare_data = await database.fetch_one(query)
            
            if dotare_data:
                base_value = dotare_data['valoare_medie']
                depreciation = dotare_data['depreciere_an']
                
                # Dotările se depreciază mai încet decât mașina
                current_value = base_value * ((1 - depreciation) ** years_old)
                total_value += current_value
        
        return round(total_value, 2)
    
    async def _calculate_premium_factor(self, dotari_list: List[str]) -> float:
        """Calculează factorul premium bazat pe dotări"""
        
        # Dotări premium care adaugă valoare semnificativă
        premium_features = {
            'interior piele': 0.02,
            'trapă panoramic': 0.025,
            'pachet sport': 0.03,
            'sistem audio premium': 0.02,
            'faruri matrix led': 0.015
        }
        
        premium_factor = 1.0
        
        for dotare in dotari_list:
            dotare_lower = dotare.lower()
            for premium, factor in premium_features.items():
                if premium in dotare_lower:
                    premium_factor += factor
                    break
        
        # Cap la +15%
        return min(premium_factor, 1.15)
    
    def _generate_pricing_strategies(
        self,
        optimal_price: float,
        market_data: Dict
    ) -> Dict:
        """Generează strategii de pricing"""
        
        # Analizează volatilitatea pieței
        volatility = market_data['price_std'] / market_data['price_mean']
        
        # Ajustează agresivitatea strategiilor bazat pe volatilitate
        if volatility > 0.3:
            # Piață volatilă - strategii mai conservatoare
            rapid_discount = 0.12
            nego_markup = 0.03
            max_markup = 0.08
        else:
            # Piață stabilă - strategii mai agresive
            rapid_discount = 0.09
            nego_markup = 0.05
            max_markup = 0.12
        
        return {
            'pret_rapid': {
                'valoare': round(optimal_price * (1 - rapid_discount)),
                'timp': '1-2 săptămâni',
                'probabilitate': 95,
                'descriere': 'Preț atractiv pentru vânzare garantată rapid'
            },
            'pret_optim': {
                'valoare': round(optimal_price),
                'timp': '3-5 săptămâni',
                'probabilitate': 85,
                'descriere': 'Cel mai bun raport calitate-preț-timp'
            },
            'pret_negociere': {
                'valoare': round(optimal_price * (1 + nego_markup)),
                'timp': '5-8 săptămâni',
                'probabilitate': 70,
                'descriere': 'Lasă spațiu pentru negociere'
            },
            'pret_maxim': {
                'valoare': round(optimal_price * (1 + max_markup)),
                'timp': '2-4 luni',
                'probabilitate': 50,
                'descriere': 'Pentru cumpărători dispuși să plătească premium'
            }
        }
    
    async def get_market_overview(self, marca: str, model: str) -> Dict:
        """Obține o privire de ansamblu asupra pieței"""
        
        query = listings.select().where(
            (listings.c.marca == marca) &
            (listings.c.model == model) &
            (listings.c.este_activ == True)
        )
        
        results = await database.fetch_all(query)
        
        if not results:
            return {
                'total_listings': 0,
                'message': 'Nu există date pentru această mașină'
            }
        
        prices = [r['pret'] for r in results]
        anos = [r['an'] for r in results]
        
        return {
            'total_listings': len(results),
            'avg_price': round(np.mean(prices), 2),
            'median_price': round(np.median(prices), 2),
            'min_price': round(np.min(prices), 2),
            'max_price': round(np.max(prices), 2),
            'avg_year': round(np.mean(anos), 1),
            'newest_year': max(anos),
            'oldest_year': min(anos)
        }
    
    async def get_price_trends(
        self,
        marca: str,
        model: str,
        days: int = 30
    ) -> Dict:
        """Obține tendințe de preț în timp"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = listings.select().where(
            (listings.c.marca == marca) &
            (listings.c.model == model) &
            (listings.c.data_scraping >= cutoff_date) &
            (listings.c.este_activ == True)
        ).order_by(listings.c.data_scraping.asc())
        
        results = await database.fetch_all(query)
        
        if not results:
            return {'message': 'Nu există date suficiente pentru tendințe'}
        
        # Grupează pe săptămână
        weekly_prices = {}
        for r in results:
            week = r['data_scraping'].isocalendar()[1]
            if week not in weekly_prices:
                weekly_prices[week] = []
            weekly_prices[week].append(r['pret'])
        
        # Calculează medie pe săptămână
        trends = []
        for week, prices in sorted(weekly_prices.items()):
            trends.append({
                'week': week,
                'avg_price': round(np.mean(prices), 2),
                'count': len(prices)
            })
        
        return {
            'trends': trends,
            'overall_trend': 'up' if trends[-1]['avg_price'] > trends[0]['avg_price'] else 'down'
        }