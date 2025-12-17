"""
Car Catalog Service - Hierarchical brand and model organization
Premium brands first (Audi, BMW, Mercedes, VW) + grouped models
"""
from typing import List, Dict, Optional
from app.database import database, listings


class CarCatalogService:
    """
    Manages car catalog with hierarchical structure
    """

    # Most searched brands in Romania (2024 data)
    TOP_BRANDS = [
        "Dacia",           # #1 cel mai popular în România
        "Volkswagen",      # #2 Golf, Passat
        "Skoda",           # #3 Octavia
        "Ford",            # #4 Focus
        "Renault",         # #5 Clio, Megane
        "Opel",            # #6 Astra
        "BMW",             # #7 Seria 3
        "Mercedes-Benz",   # #8 C-Class
        "Audi",            # #9 A4
        "Toyota",          # #10 Corolla
    ]

    # Other brands (alphabetical after top 10)
    OTHER_BRANDS = [
        "Alfa Romeo",
        "Chevrolet",
        "Citroen",
        "Fiat",
        "Honda",
        "Hyundai",
        "Kia",
        "Mazda",
        "Mitsubishi",
        "Nissan",
        "Peugeot",
        "Seat",
        "Suzuki",
        "Volvo",
    ]

    # Model series grouping patterns
    MODEL_SERIES_PATTERNS = {
        'bmw': {
            'Seria 1': [r'1\d{2}', r'seria 1', r'series 1'],
            'Seria 2': [r'2\d{2}', r'seria 2', r'series 2'],
            'Seria 3': [r'3\d{2}', r'seria 3', r'series 3'],
            'Seria 4': [r'4\d{2}', r'seria 4', r'series 4'],
            'Seria 5': [r'5\d{2}', r'seria 5', r'series 5'],
            'Seria 6': [r'6\d{2}', r'seria 6', r'series 6'],
            'Seria 7': [r'7\d{2}', r'seria 7', r'series 7'],
            'Seria 8': [r'8\d{2}', r'seria 8', r'series 8'],
            'X1': [r'x1'],
            'X2': [r'x2'],
            'X3': [r'x3'],
            'X4': [r'x4'],
            'X5': [r'x5'],
            'X6': [r'x6'],
            'X7': [r'x7'],
            'Z4': [r'z4'],
            'i3': [r'i3'],
            'i4': [r'i4'],
            'i8': [r'i8'],
        },
        'mercedes': {
            'A-Class': [r'a\s*\d{2,3}', r'a-class', r'clasa a'],
            'B-Class': [r'b\s*\d{2,3}', r'b-class', r'clasa b'],
            'C-Class': [r'c\s*\d{2,3}', r'c-class', r'clasa c'],
            'E-Class': [r'e\s*\d{2,3}', r'e-class', r'clasa e'],
            'S-Class': [r's\s*\d{2,3}', r's-class', r'clasa s'],
            'CLA': [r'cla'],
            'CLS': [r'cls'],
            'GLA': [r'gla'],
            'GLB': [r'glb'],
            'GLC': [r'glc'],
            'GLE': [r'gle'],
            'GLS': [r'gls'],
            'G-Class': [r'g\s*\d{2,3}', r'g-class'],
        },
        'audi': {
            'A1': [r'a1'],
            'A3': [r'a3'],
            'A4': [r'a4'],
            'A5': [r'a5'],
            'A6': [r'a6'],
            'A7': [r'a7'],
            'A8': [r'a8'],
            'Q2': [r'q2'],
            'Q3': [r'q3'],
            'Q5': [r'q5'],
            'Q7': [r'q7'],
            'Q8': [r'q8'],
            'TT': [r'tt'],
            'R8': [r'r8'],
            'e-tron': [r'e-tron', r'etron'],
        },
        'volkswagen': {
            'Golf': [r'golf'],
            'Polo': [r'polo'],
            'Passat': [r'passat'],
            'Jetta': [r'jetta'],
            'Tiguan': [r'tiguan'],
            'Touareg': [r'touareg'],
            'Arteon': [r'arteon'],
            'T-Roc': [r't-roc', r'troc'],
            'ID.3': [r'id\.?3'],
            'ID.4': [r'id\.?4'],
        },
        'dacia': {
            'Logan': [r'logan'],
            'Sandero': [r'sandero'],
            'Duster': [r'duster'],
            'Lodgy': [r'lodgy'],
            'Dokker': [r'dokker'],
            'Spring': [r'spring'],
            'Jogger': [r'jogger'],
        },
        'skoda': {
            'Fabia': [r'fabia'],
            'Octavia': [r'octavia'],
            'Superb': [r'superb'],
            'Rapid': [r'rapid'],
            'Scala': [r'scala'],
            'Kamiq': [r'kamiq'],
            'Karoq': [r'karoq'],
            'Kodiaq': [r'kodiaq'],
        },
        'ford': {
            'Fiesta': [r'fiesta'],
            'Focus': [r'focus'],
            'Mondeo': [r'mondeo'],
            'Kuga': [r'kuga'],
            'Puma': [r'puma'],
            'EcoSport': [r'ecosport'],
            'Mustang': [r'mustang'],
        },
        'renault': {
            'Clio': [r'clio'],
            'Megane': [r'megane'],
            'Captur': [r'captur'],
            'Kadjar': [r'kadjar'],
            'Talisman': [r'talisman'],
            'Zoe': [r'zoe'],
        },
        'opel': {
            'Corsa': [r'corsa'],
            'Astra': [r'astra'],
            'Insignia': [r'insignia'],
            'Mokka': [r'mokka'],
            'Crossland': [r'crossland'],
            'Grandland': [r'grandland'],
        }
    }

    async def get_brands(self) -> List[Dict]:
        """
        Get all brands with top brands first

        Returns:
            [
                {"value": "dacia", "label": "Dacia", "isTop": true},
                {"value": "volkswagen", "label": "Volkswagen", "isTop": true},
                ...
            ]
        """
        brands = []

        # Add ALL top brands first (most searched in Romania)
        for brand in self.TOP_BRANDS:
            brand_lower = brand.lower().replace('-', '').replace(' ', '')
            brands.append({
                'value': brand_lower,
                'label': brand,
                'isTop': True
            })

        # Add ALL other brands alphabetically
        for brand in self.OTHER_BRANDS:
            brand_lower = brand.lower().replace('-', '').replace(' ', '')
            brands.append({
                'value': brand_lower,
                'label': brand,
                'isTop': False
            })

        return brands

    async def get_model_series(self, marca: str) -> List[Dict]:
        """
        Get hierarchical model series for a brand

        For BMW: Returns ["Seria 1", "Seria 2", ...]
        For VW: Returns ["Golf", "Polo", "Passat", ...]

        Returns:
            [
                {"series": "Seria 3"},
                {"series": "Seria 5"},
                ...
            ]
        """
        marca_lower = marca.lower().replace('-', '').replace(' ', '')

        # Get patterns for this brand
        patterns = self.MODEL_SERIES_PATTERNS.get(marca_lower, {})

        if not patterns:
            # No patterns defined - return empty list
            # User can still type any model manually
            return []

        series_list = []

        # Return ALL series for this brand from patterns
        for series_name in patterns.keys():
            series_list.append({
                'series': series_name
            })

        return series_list

    async def _get_simple_models(self, marca: str) -> List[Dict]:
        """Get simple model list (for brands without series)"""
        query = """
            SELECT
                model_series as series,
                COUNT(*) as count,
                ARRAY_AGG(DISTINCT model_variant) as variants
            FROM listings
            WHERE
                LOWER(marca) LIKE :marca
                AND este_activ = true
                AND model_series IS NOT NULL
            GROUP BY model_series
            ORDER BY count DESC
        """

        result = await database.fetch_all(
            query,
            {'marca': f'%{marca.lower()}%'}
        )

        return [
            {
                'series': row['series'],
                'count': row['count'],
                'variants': [v for v in (row['variants'] or []) if v]
            }
            for row in result
        ]

    async def get_year_range(self, marca: str, model_series: str) -> Dict:
        """Get available year range for a model"""
        query = """
            SELECT
                MIN(an) as min_year,
                MAX(an) as max_year
            FROM listings
            WHERE
                LOWER(marca) LIKE :marca
                AND (model_series ILIKE :series OR model ILIKE :series)
                AND este_activ = true
                AND an IS NOT NULL
        """

        result = await database.fetch_one(
            query,
            {
                'marca': f'%{marca.lower()}%',
                'series': f'%{model_series}%'
            }
        )

        if result:
            return {
                'min': result['min_year'] or 1990,
                'max': result['max_year'] or 2025
            }

        return {'min': 1990, 'max': 2025}

    async def get_variants_for_series(self, marca: str, model_series: str) -> List[str]:
        """Get performance variants for a model series"""
        query = """
            SELECT DISTINCT model_variant
            FROM listings
            WHERE
                LOWER(marca) LIKE :marca
                AND (model_series ILIKE :series OR model ILIKE :series)
                AND este_activ = true
                AND model_variant IS NOT NULL
            ORDER BY model_variant
        """

        result = await database.fetch_all(
            query,
            {
                'marca': f'%{marca.lower()}%',
                'series': f'%{model_series}%'
            }
        )

        return [row['model_variant'] for row in result]


# Global instance
car_catalog_service = CarCatalogService()
