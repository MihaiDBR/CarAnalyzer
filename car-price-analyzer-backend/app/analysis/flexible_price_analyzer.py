"""
Flexible Price Analyzer - Funcționează pentru ORICE mașină
Folosește sistem de fallback pe 3 nivele + calcul generic
"""
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
from app.database import database, listings

class FlexiblePriceAnalyzer:
    """Analizor de prețuri flexibil cu fallback inteligent"""

    # Depreciation rates by brand category
    BRAND_CATEGORIES = {
        'luxury': {
            'brands': ['bmw', 'mercedes-benz', 'mercedes', 'audi', 'porsche', 'jaguar',
                      'maserati', 'bentley', 'rolls-royce', 'aston martin'],
            'depreciation': 0.18,  # 18% per year
            'avg_price_mult': 1.5   # Premium multiplier
        },
        'premium': {
            'brands': ['volvo', 'lexus', 'infiniti', 'acura', 'land rover', 'cadillac',
                      'lincoln', 'alfa romeo', 'genesis'],
            'depreciation': 0.13,
            'avg_price_mult': 1.3
        },
        'mass_market': {
            'brands': ['volkswagen', 'vw', 'toyota', 'honda', 'mazda', 'nissan',
                      'ford', 'chevrolet', 'hyundai', 'kia', 'peugeot', 'renault',
                      'citroen', 'seat', 'opel', 'fiat', 'mitsubishi', 'suzuki'],
            'depreciation': 0.11,
            'avg_price_mult': 1.0
        },
        'budget': {
            'brands': ['dacia', 'skoda', 'lada'],
            'depreciation': 0.09,
            'avg_price_mult': 0.8
        }
    }

    # Average new prices by vehicle category (EUR)
    CATEGORY_BASE_PRICES = {
        'sedan_small': 20000,      # A-segment, B-segment
        'sedan_medium': 30000,     # C-segment (Golf, Seria 3)
        'sedan_large': 45000,      # D-segment, E-segment
        'sedan_luxury': 80000,     # F-segment (Seria 7, S-Class)
        'suv_small': 25000,        # Compact SUV
        'suv_medium': 40000,       # Mid SUV (X3, Q5)
        'suv_large': 60000,        # Large SUV (X5, GLE)
        'suv_luxury': 100000,      # Luxury SUV (X7, GLS, Bentayga)
        'sport': 60000,            # Sports cars
        'supercar': 200000,        # Supercars
        'hatchback': 18000,        # Hatchbacks
        'wagon': 28000,            # Station wagons
        'coupe': 40000,            # Coupes
        'convertible': 50000       # Convertibles
    }

    def __init__(self):
        pass

    def get_brand_category(self, marca: str) -> str:
        """Determină categoria mărcii"""
        marca_lower = marca.lower().strip()

        for category, data in self.BRAND_CATEGORIES.items():
            if marca_lower in data['brands']:
                return category

        # Default to mass_market if unknown
        return 'mass_market'

    def estimate_vehicle_category(self, marca: str, model: str) -> str:
        """
        Estimează categoria vehiculului bazat pe marcă și model
        """
        model_lower = model.lower()
        marca_lower = marca.lower()

        # Luxury brands
        if marca_lower in ['bentley', 'rolls-royce', 'maserati']:
            return 'sedan_luxury'

        # SUVs
        if any(x in model_lower for x in ['x1', 'x2', 'q2', 'q3', 'gla', 'glb', 'xt', 'qx30']):
            return 'suv_small'
        if any(x in model_lower for x in ['x3', 'x4', 'q5', 'glc', 'tiguan', 'rav4', 'cr-v', 'sportage', 'tucson']):
            return 'suv_medium'
        if any(x in model_lower for x in ['x5', 'x6', 'q7', 'q8', 'gle', 'gls', 'cayenne', 'touareg', 'defender', 'range rover']):
            return 'suv_large'
        if any(x in model_lower for x in ['bentayga', 'cullinan', 'urus', 'dbx']):
            return 'suv_luxury'

        # Sports/Supercars
        if any(x in model_lower for x in ['911', 'cayman', 'boxster', 'corvette', 'mustang', 'camaro']):
            return 'sport'
        if any(x in model_lower for x in ['ferrari', 'lamborghini', 'mclaren', 'huracan', 'aventador']):
            return 'supercar'

        # Body types
        if any(x in model_lower for x in ['coupe', 'coup']):
            return 'coupe'
        if any(x in model_lower for x in ['cabrio', 'convertible', 'roadster']):
            return 'convertible'
        if any(x in model_lower for x in ['wagon', 'estate', 'touring', 'avant', 'kombi']):
            return 'wagon'
        if any(x in model_lower for x in ['golf', 'polo', 'fiesta', 'corsa', 'punto', 'yaris', 'jazz']):
            return 'hatchback'

        # Sedan sizes by series number
        if any(x in model_lower for x in ['1 series', 'seria 1', 'a1', 'a-class', 'clasa a']):
            return 'sedan_small'
        if any(x in model_lower for x in ['2 series', '3 series', 'seria 2', 'seria 3', 'a3', 'a4', 'c-class', 'clasa c']):
            return 'sedan_medium'
        if any(x in model_lower for x in ['5 series', 'seria 5', 'a6', 'e-class', 'clasa e']):
            return 'sedan_large'
        if any(x in model_lower for x in ['7 series', 'seria 7', 'a8', 's-class', 'clasa s']):
            return 'sedan_luxury'

        # Default based on brand category
        brand_cat = self.get_brand_category(marca)
        if brand_cat == 'luxury':
            return 'sedan_large'
        elif brand_cat == 'budget':
            return 'sedan_small'
        else:
            return 'sedan_medium'

    async def calculate_price_with_fallback(
        self,
        marca: str,
        model: str,
        an: int,
        km: int,
        dotari_list: List[str] = None
    ) -> Dict:
        """
        Calculează prețul cu sistem de fallback pe 3 nivele
        GARANTAT să returneze un preț, nu aruncă niciodată eroare!
        """
        if dotari_list is None:
            dotari_list = []

        sources = []

        # NIVEL 1: Try exact match in database
        try:
            db_result = await self.search_exact_database(marca, model, an, km)
            if db_result and db_result['count'] >= 3:
                sources.append({
                    'level': 1,
                    'source': 'database_exact',
                    'price': db_result['avg_price'],
                    'confidence': 95,
                    'sample_size': db_result['count'],
                    'description': f'Date reale din {db_result["count"]} anunțuri similare'
                })
        except Exception as e:
            print(f"Level 1 failed: {e}")

        # NIVEL 2: Try similar match (same brand, similar year, similar km)
        try:
            similar_result = await self.search_similar_database(marca, model, an, km)
            if similar_result and similar_result['count'] >= 5:
                sources.append({
                    'level': 2,
                    'source': 'database_similar',
                    'price': similar_result['avg_price'],
                    'confidence': 75,
                    'sample_size': similar_result['count'],
                    'description': f'Date din {similar_result["count"]} mașini similare'
                })
        except Exception as e:
            print(f"Level 2 failed: {e}")

        # NIVEL 3: Generic depreciation formula (ALWAYS works)
        generic_price = self.calculate_generic_depreciation(marca, model, an, km)
        sources.append({
            'level': 3,
            'source': 'generic_formula',
            'price': generic_price,
            'confidence': 60,
            'sample_size': 0,
            'description': 'Calcul bazat pe formula standard de depreciere'
        })

        # Use best available source (lowest level = highest confidence)
        best_source = min(sources, key=lambda x: x['level'])
        base_price = best_source['price']

        # Calculate equipment value
        equipment_value = self.calculate_equipment_value(dotari_list, datetime.now().year - an)

        # Final price
        final_price = base_price + equipment_value

        # Generate pricing strategies
        strategies = self.generate_pricing_strategies(final_price, best_source['confidence'])

        return {
            'pret_rapid': strategies['pret_rapid'],
            'pret_optim': strategies['pret_optim'],
            'pret_negociere': strategies['pret_negociere'],
            'pret_maxim': strategies['pret_maxim'],
            'valoare_dotari': round(equipment_value, 2),
            'market_data': {
                'source': best_source['source'],
                'confidence': best_source['confidence'],
                'description': best_source['description'],
                'sample_size': best_source['sample_size'],
                'all_sources': sources
            }
        }

    async def search_exact_database(self, marca: str, model: str, an: int, km: int) -> Optional[Dict]:
        """Search exact match in database"""
        query = listings.select().where(
            (listings.c.marca.ilike(f"%{marca}%")) &
            (listings.c.model.ilike(f"%{model}%")) &
            (listings.c.an.between(an - 1, an + 1)) &
            (listings.c.km.between(max(0, km - 20000), km + 20000)) &
            (listings.c.este_activ == True)
        )

        results = await database.fetch_all(query)

        if not results or len(results) < 3:
            return None

        prices = [r['pret'] for r in results]
        return {
            'avg_price': round(np.mean(prices), 2),
            'count': len(results)
        }

    async def search_similar_database(self, marca: str, model: str, an: int, km: int) -> Optional[Dict]:
        """Search similar vehicles (broader criteria)"""
        query = listings.select().where(
            (listings.c.marca.ilike(f"%{marca}%")) &
            (listings.c.an.between(an - 3, an + 3)) &
            (listings.c.km.between(max(0, km - 50000), km + 50000)) &
            (listings.c.este_activ == True)
        )

        results = await database.fetch_all(query)

        if not results or len(results) < 5:
            return None

        prices = [r['pret'] for r in results]
        return {
            'avg_price': round(np.mean(prices), 2),
            'count': len(results)
        }

    def calculate_generic_depreciation(self, marca: str, model: str, an: int, km: int) -> float:
        """
        Calculate price using generic depreciation formula
        ALWAYS returns a price - fallback guaranteed!
        """
        # Get brand category and depreciation rate
        brand_cat = self.get_brand_category(marca)
        depreciation_rate = self.BRAND_CATEGORIES[brand_cat]['depreciation']
        price_mult = self.BRAND_CATEGORIES[brand_cat]['avg_price_mult']

        # Estimate vehicle category
        vehicle_cat = self.estimate_vehicle_category(marca, model)
        base_price_new = self.CATEGORY_BASE_PRICES[vehicle_cat] * price_mult

        # Calculate age depreciation
        years_old = datetime.now().year - an
        age_depreciated = base_price_new * ((1 - depreciation_rate) ** years_old)

        # Calculate km depreciation
        expected_km = 15000 * years_old  # 15k km/year average
        km_diff = km - expected_km

        if km_diff > 0:
            # More km = penalty
            km_penalty = min((km_diff / 10000) * 0.005, 0.30)  # Max 30% penalty
            km_factor = 1 - km_penalty
        else:
            # Less km = bonus
            km_bonus = min((abs(km_diff) / 10000) * 0.003, 0.15)  # Max 15% bonus
            km_factor = 1 + km_bonus

        final_price = age_depreciated * km_factor

        # Ensure reasonable minimum (5% of new price)
        min_price = base_price_new * 0.05
        return round(max(final_price, min_price), -2)  # Round to nearest 100

    def calculate_equipment_value(self, equipment_list: List[str], car_age: int) -> float:
        """Calculate value of equipment with depreciation"""
        # Equipment values (EUR) and depreciation rates
        EQUIPMENT = {
            'piele': {'value': 1500, 'depr': 0.10},
            'navigatie': {'value': 1200, 'depr': 0.20},
            'xenon': {'value': 800, 'depr': 0.12},
            'senzori': {'value': 400, 'depr': 0.10},
            'camera': {'value': 600, 'depr': 0.15},
            'scaune': {'value': 500, 'depr': 0.12},
            'clima': {'value': 800, 'depr': 0.15},
            'jante': {'value': 1000, 'depr': 0.12},
            'cruise': {'value': 300, 'depr': 0.15},
            'keyless': {'value': 400, 'depr': 0.15},
            'trapa': {'value': 1500, 'depr': 0.15},
            'sport': {'value': 3000, 'depr': 0.12}
        }

        total_value = 0.0

        for eq in equipment_list:
            eq_lower = eq.lower()
            for key, data in EQUIPMENT.items():
                if key in eq_lower:
                    base_value = data['value']
                    depr_rate = data['depr']
                    current_value = base_value * ((1 - depr_rate) ** car_age)
                    total_value += current_value
                    break

        return total_value

    def generate_pricing_strategies(self, optimal_price: float, confidence: int) -> Dict:
        """Generate pricing strategies"""
        # Adjust aggressiveness based on confidence
        if confidence >= 90:
            rapid_discount = 0.09
            nego_markup = 0.05
            max_markup = 0.12
        elif confidence >= 70:
            rapid_discount = 0.10
            nego_markup = 0.04
            max_markup = 0.10
        else:
            rapid_discount = 0.12
            nego_markup = 0.03
            max_markup = 0.08

        return {
            'pret_rapid': {
                'valoare': round(optimal_price * (1 - rapid_discount)),
                'timp': '1-2 săptămâni',
                'probabilitate': 95,
                'descriere': 'Preț atractiv pentru vânzare rapidă garantată'
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
                'descriere': f'Pentru cumpărători dispuși să plătească premium (încredere: {confidence}%)'
            }
        }


# Global instance
flexible_analyzer = FlexiblePriceAnalyzer()
