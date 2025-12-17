"""
Detailed OLX Scraper - Extracts complete car specifications
Includes: year, km, transmission, drivetrain, body type, power, variant (GTI, R, M, AMG)
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote, urljoin


class DetailedOLXScraper:
    """
    Advanced scraper that extracts detailed car specifications
    """

    BASE_URL = "https://www.olx.ro"
    SEARCH_URL = "https://www.olx.ro/d/oferte/q-{query}/"
    DELAY_BETWEEN_REQUESTS = 10  # seconds
    USER_AGENT = "CarAnalyzer/2.0 (+https://github.com/MihaiDBR/CarAnalyzer) Research Bot"

    # Performance variants by brand
    PERFORMANCE_VARIANTS = {
        'bmw': ['m', 'm3', 'm4', 'm5', 'm6', 'm2', 'x3m', 'x4m', 'x5m', 'x6m', 'm sport', 'competition'],
        'mercedes': ['amg', 'c63', 'e63', 's63', 'g63', 'a45', 'cla45', 'gla45', 'glc63'],
        'audi': ['rs', 'rs3', 'rs4', 'rs5', 'rs6', 'rs7', 'rsq3', 'rsq8', 's', 's3', 's4', 's5', 's6', 's7', 's8', 'sq5', 'sq7'],
        'volkswagen': ['r', 'gti', 'gtd', 'r-line', 'r line'],
        'golf': ['gti', 'gtd', 'r', 'r32'],
        'ford': ['st', 'rs', 'raptor'],
        'honda': ['type r', 'type-r', 'si'],
        'renault': ['rs', 'sport'],
        'seat': ['cupra', 'fr'],
        'skoda': ['rs', 'vrs'],
        'volvo': ['polestar', 'r-design'],
        'porsche': ['turbo', 'gt3', 'gt2', 'gts', 'carrera'],
    }

    def __init__(self):
        self.request_count = 0
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': self.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
                'DNT': '1',
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_cars(self, marca: str, model: Optional[str] = None, max_pages: int = 2) -> List[Dict]:
        """
        Search for detailed car listings

        Args:
            marca: Car brand
            model: Car model (optional)
            max_pages: Maximum pages to scrape

        Returns:
            List of detailed car listings
        """
        if model:
            search_query = f"{marca} {model}"
        else:
            search_query = marca

        encoded_query = quote(search_query.lower().replace(' ', '-'))
        url = self.SEARCH_URL.format(query=encoded_query)

        print(f"Searching: {search_query}")

        listings = []
        session = await self._get_session()

        try:
            for page in range(1, max_pages + 1):
                page_url = url if page == 1 else f"{url}?page={page}"

                if self.request_count > 0:
                    print(f"Rate limiting: {self.DELAY_BETWEEN_REQUESTS}s...")
                    await asyncio.sleep(self.DELAY_BETWEEN_REQUESTS)

                print(f"Fetching page {page}...")
                async with session.get(page_url) as response:
                    if response.status != 200:
                        print(f"Error: HTTP {response.status}")
                        break

                    html = await response.text()
                    self.request_count += 1

                page_listings = self._parse_search_page(html, marca, model)
                listings.extend(page_listings)

                print(f"Found {len(page_listings)} listings on page {page}")

                if not page_listings:
                    break

            print(f"Total: {len(listings)} listings")

        except Exception as e:
            print(f"Error: {e}")

        return listings

    def _parse_search_page(self, html: str, marca: str, model: Optional[str]) -> List[Dict]:
        """Parse search results page"""
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', {'data-cy': 'l-card'})

        listings = []
        for card in cards:
            try:
                listing = self._parse_listing_card(card, marca, model)
                if listing:
                    listings.append(listing)
            except Exception as e:
                continue

        return listings

    def _parse_listing_card(self, card, marca: str, model: Optional[str]) -> Optional[Dict]:
        """Parse detailed listing card"""
        try:
            # Extract URL
            link = card.find('a', href=True)
            if not link:
                return None
            url = urljoin(self.BASE_URL, link['href'])

            # Extract title and full text
            title_elem = card.find('h6') or card.find('h4')
            title = title_elem.get_text(strip=True) if title_elem else ""
            if not title:
                return None

            full_text = card.get_text()

            # Filter car parts
            if self._is_car_part(title):
                return None

            # Extract price
            price = self._extract_price_from_card(card)
            if not price or price < 3000:
                return None

            # Extract year (CRITICAL)
            year = self._extract_year(title, full_text)
            if not year:
                return None  # Skip if no year - can't calculate depreciation

            # Extract kilometers
            km = self._extract_km(title, full_text)

            # Extract model series and variant
            model_series, model_variant = self._extract_model_details(title, marca, model)

            # Extract technical specs
            fuel_type = self._extract_fuel_type(title, full_text)
            power_cp = self._extract_power(title, full_text)
            capacity_cc = self._extract_engine_capacity(title, full_text)
            transmission = self._extract_transmission(title, full_text)
            drivetrain = self._extract_drivetrain(title, full_text)
            body_type = self._extract_body_type(title, full_text, model_series)

            # Extract location
            location = self._extract_location(card)

            # Build detailed listing
            listing = {
                'source': 'olx',
                'url': url,
                'marca': marca.title(),
                'model': model.title() if model else model_series,
                'model_series': model_series,
                'model_variant': model_variant,
                'an': year,
                'km': km,
                'pret': price,
                'combustibil': fuel_type,
                'putere_cp': power_cp,
                'capacitate_cilindrica': capacity_cc,
                'transmisie': transmission,
                'tractiune': drivetrain,
                'caroserie': body_type,
                'locatie': location,
                'dotari': [],
                'imagini': [],
                'descriere': title[:500],
                'data_publicare': datetime.now(),
                'zile_pe_piata': 0,
                'este_activ': True
            }

            return listing

        except Exception as e:
            return None

    def _is_car_part(self, title: str) -> bool:
        """Check if listing is for a car part"""
        title_lower = title.lower()
        parts_keywords = [
            'jante', 'janta', 'roata', 'roti', 'anvelope',
            'stopuri', 'stop', 'faruri', 'far', 'oglinda',
            'bara', 'portiera', 'capota', 'haion',
            'volant', 'scaune', 'bord',
            'motor', 'cutie viteze', 'turbo', 'alternator',
            'carcasa', 'deflector', 'senzori',
            'perna', 'amortizor', 'suspensie',
            'radiator', 'intercooler', 'toba',
            'filtru', 'curea', 'ulei'
        ]

        for keyword in parts_keywords:
            if keyword in title_lower:
                # Exception: full car sale indicators
                if any(word in title_lower for word in ['vand ', 'schimb', 'urgent', 'full']):
                    has_year = re.search(r'\b20\d{2}\b', title)
                    has_km = re.search(r'\d+\s*km', title_lower)
                    if has_year and has_km and len(title.split()) > 6:
                        return False
                return True

        return False

    def _extract_model_details(self, title: str, marca: str, model: Optional[str]) -> tuple:
        """
        Extract model series and performance variant

        Examples:
        - "BMW 320d M Sport" → ("Seria 3", "M Sport")
        - "Golf 7 GTI" → ("Golf", "GTI")
        - "Mercedes C63 AMG" → ("C-Class", "C63 AMG")
        """
        title_lower = title.lower()
        marca_lower = marca.lower()

        # Extract variant (GTI, R, M, AMG, etc.)
        variant = None
        variants_to_check = self.PERFORMANCE_VARIANTS.get(marca_lower, [])
        variants_to_check += self.PERFORMANCE_VARIANTS.get(model.lower() if model else '', [])

        for perf_variant in variants_to_check:
            if perf_variant.lower() in title_lower:
                variant = perf_variant.upper() if len(perf_variant) <= 3 else perf_variant.title()
                break

        # Extract model series
        series = model if model else self._guess_model_from_title(title, marca)

        # For BMW: extract series number (320d → Seria 3)
        if marca_lower == 'bmw':
            series_match = re.search(r'\b([1-8])(\d{2})', title)
            if series_match:
                series_num = series_match.group(1)
                series = f"Seria {series_num}"

        # For Mercedes: C220 → C-Class
        elif marca_lower == 'mercedes' or 'mercedes' in marca_lower:
            class_match = re.search(r'\b([ABCEGLSV])\s*(\d{2,3})', title, re.IGNORECASE)
            if class_match:
                class_letter = class_match.group(1).upper()
                series = f"{class_letter}-Class"

        # For Audi: A4, A6, Q5, etc.
        elif marca_lower == 'audi':
            audi_match = re.search(r'\b([AQ]\d|TT|R8)', title, re.IGNORECASE)
            if audi_match:
                series = audi_match.group(0).upper()

        return (series, variant)

    def _guess_model_from_title(self, title: str, marca: str) -> str:
        """Guess model when not provided"""
        words = title.replace(marca, '').strip().split()
        if len(words) >= 1:
            return words[0]
        return "Unknown"

    def _extract_power(self, title: str, text: str) -> Optional[int]:
        """Extract power in CP"""
        # Look for "150 CP", "200cp", "180 cai"
        for pattern in [r'(\d{2,3})\s*cp', r'(\d{2,3})\s*cai', r'(\d{2,3})\s*hp']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                power = int(match.group(1))
                if 50 <= power <= 1000:  # Sanity check
                    return power
        return None

    def _extract_engine_capacity(self, title: str, text: str) -> Optional[int]:
        """Extract engine capacity in cm3"""
        # Look for "2.0", "1.6", "3.0L"
        for pattern in [r'(\d\.\d)\s*l', r'(\d\.\d)\s*tdi', r'(\d\.\d)\s*tsi']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                liters = float(match.group(1))
                return int(liters * 1000)  # Convert to cm3

        # Look for direct cm3 mention
        match = re.search(r'(\d{3,4})\s*cm', text, re.IGNORECASE)
        if match:
            return int(match.group(1))

        return None

    def _extract_transmission(self, title: str, text: str) -> str:
        """Extract transmission type"""
        text_lower = text.lower()

        # Keywords for automatic
        auto_keywords = ['automat', 'automata', 'dsg', 'cvt', 'tiptronic', 'steptronic', 's-tronic']
        if any(kw in text_lower for kw in auto_keywords):
            return 'automata'

        # Keywords for manual
        manual_keywords = ['manual', 'manuala', 'cutie manuala']
        if any(kw in text_lower for kw in manual_keywords):
            return 'manuala'

        return 'unknown'

    def _extract_drivetrain(self, title: str, text: str) -> str:
        """Extract drivetrain (fata, spate, 4x4)"""
        text_lower = text.lower()

        # 4WD / AWD
        if any(kw in text_lower for kw in ['4x4', '4wd', 'awd', 'quattro', 'xdrive', '4motion', '4matic']):
            return '4x4'

        # RWD
        if any(kw in text_lower for kw in ['rwd', 'propulsie', 'spate']):
            return 'spate'

        # FWD (most common)
        return 'fata'

    def _extract_body_type(self, title: str, text: str, model_series: str) -> str:
        """Extract body type"""
        text_lower = text.lower()

        # SUV / Crossover
        suv_keywords = ['suv', 'crossover', 'off-road', 'offroad']
        suv_models = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'q3', 'q5', 'q7', 'q8',
                      'gle', 'glc', 'gla', 'tiguan', 'touareg', 'cayenne', 'macan']

        if any(kw in text_lower for kw in suv_keywords):
            return 'suv'
        if model_series and any(mdl in model_series.lower() for mdl in suv_models):
            return 'suv'

        # Coupe
        if 'coupe' in text_lower or 'coupé' in text_lower:
            return 'coupe'

        # Cabrio / Convertible
        if any(kw in text_lower for kw in ['cabrio', 'cabriolet', 'convertible', 'descapotabil']):
            return 'cabrio'

        # Break / Wagon / Estate
        if any(kw in text_lower for kw in ['break', 'combi', 'touring', 'avant', 'estate', 'wagon']):
            return 'break'

        # Sedan / Limousine
        if any(kw in text_lower for kw in ['sedan', 'limuzina', 'berlina']):
            return 'sedan'

        # Hatchback (default for compact cars)
        return 'hatchback'

    def _extract_price_from_card(self, card) -> Optional[float]:
        """Extract and convert price"""
        price_elem = card.find('p', {'data-testid': 'ad-price'})
        if not price_elem:
            price_elem = card.find(string=re.compile(r'\d+.*(?:EUR|euro|lei)', re.I))

        if price_elem:
            price_text = price_elem.get_text(strip=True) if hasattr(price_elem, 'get_text') else str(price_elem)
            return self._parse_price(price_text)

        return None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price and convert to EUR"""
        original_text = price_text.lower()

        is_lei = 'lei' in original_text
        is_eur = 'eur' in original_text or 'euro' in original_text

        price_text = price_text.replace('EUR', '').replace('euro', '').replace('lei', '').replace('€', '')
        price_text = price_text.replace(' ', '').replace('.', '').replace(',', '')

        match = re.search(r'\d+', price_text)
        if match:
            try:
                price = float(match.group())

                if is_lei and not is_eur:
                    price = price / 4.97

                if 3000 <= price <= 500000:
                    return round(price, 2)
            except ValueError:
                pass

        return None

    def _extract_year(self, title: str, text: str) -> Optional[int]:
        """Extract year"""
        for source in [title, text]:
            match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', source)
            if match:
                year = int(match.group(1))
                if 1990 <= year <= 2025:
                    return year
        return None

    def _extract_km(self, title: str, text: str) -> int:
        """Extract kilometers"""
        for source in [title, text]:
            match = re.search(r'(\d+)[.\s]?(\d+)?\s*(km|mii\s*km)', source, re.IGNORECASE)
            if match:
                km_str = match.group(1) + (match.group(2) or '')
                try:
                    km = int(km_str)
                    if 'mii' in match.group(3).lower():
                        km *= 1000
                    if 0 <= km <= 1000000:
                        return km
                except ValueError:
                    pass
        return 0

    def _extract_fuel_type(self, title: str, text: str) -> str:
        """Extract fuel type"""
        text_lower = (title + ' ' + text).lower()

        if 'diesel' in text_lower or 'motorina' in text_lower:
            return 'diesel'
        elif 'benzina' in text_lower or 'petrol' in text_lower:
            return 'benzina'
        elif 'electric' in text_lower:
            return 'electric'
        elif 'hybrid' in text_lower or 'hibrid' in text_lower:
            return 'hybrid'
        elif 'gpl' in text_lower or 'lpg' in text_lower:
            return 'gpl'

        return 'benzina'

    def _extract_location(self, card) -> str:
        """Extract location"""
        location_elem = card.find('p', {'data-testid': 'location-date'})
        if location_elem:
            location = location_elem.get_text(strip=True)
            return location.split(',')[0].split('-')[0].strip()
        return "Romania"


    async def bulk_search(self, search_queries: List[Dict]) -> List[Dict]:
        """
        Bulk search for multiple car models

        Args:
            search_queries: List of dicts with 'marca' and 'model' keys

        Returns:
            Combined list of all listings
        """
        all_listings = []

        for i, query in enumerate(search_queries):
            marca = query.get('marca')
            model = query.get('model')

            print(f"\n[{i+1}/{len(search_queries)}] Searching: {marca} {model or ''}")

            listings = await self.search_cars(marca, model, max_pages=1)
            all_listings.extend(listings)

            print(f"Found {len(listings)} listings")

        print(f"\nTotal listings found: {len(all_listings)}")
        return all_listings


# Global instance
detailed_olx_scraper = DetailedOLXScraper()
