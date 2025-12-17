"""
OLX Filtered Scraper - Uses native OLX filters from URL parameters
Much more accurate than text parsing!
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlencode


class OLXFilteredScraper:
    """
    Scraper that uses OLX's native filtering system
    """

    BASE_URL = "https://www.olx.ro"
    SEARCH_BASE = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/"

    DELAY_BETWEEN_REQUESTS = 10  # seconds
    USER_AGENT = "CarAnalyzer/2.0 (+https://github.com/MihaiDBR/CarAnalyzer) Research Bot"

    # Map our fields to OLX filter parameters
    OLX_FILTERS = {
        'marca': 'make',  # Not used in URL, part of path
        'model': 'filter_enum_model',
        'year_from': 'filter_float_year:from',
        'year_to': 'filter_float_year:to',
        'price_from': 'filter_float_price:from',
        'price_to': 'filter_float_price:to',
        'km_from': 'filter_float_rulaj_pana:from',
        'km_to': 'filter_float_rulaj_pana:to',
        'engine_from': 'filter_float_enginesize:from',
        'engine_to': 'filter_float_enginesize:to',
        'power_from': 'filter_float_engine_power:from',
        'power_to': 'filter_float_engine_power:to',
        'fuel_type': 'filter_enum_petrol',
        'body_type': 'filter_enum_car_body',
        'transmission': 'filter_enum_gearbox',
    }

    # OLX values for filters
    FUEL_TYPES = {
        'benzina': 'petrol',
        'diesel': 'diesel',
        'electric': 'electric',
        'hybrid': 'hybrid',
        'gpl': 'lpg',
    }

    BODY_TYPES = {
        'sedan': 'sedan',
        'hatchback': 'small',
        'break': 'kombi',
        'coupe': 'coupe',
        'suv': 'suv',
        'cabrio': 'cabrio',
        'van': 'van',
    }

    TRANSMISSIONS = {
        'manuala': 'manual',
        'automata': 'automatic',
    }

    # BMW model series mapping
    BMW_MODELS = {
        'Seria 1': '1-as-sorozat',
        'Seria 2': '2-as-sorozat',
        'Seria 3': '3-as-sorozat',
        'Seria 4': '4-as-sorozat',
        'Seria 5': '5-as-sorozat',
        'Seria 6': '6-as-sorozat',
        'Seria 7': '7-as-sorozat',
        'Seria 8': '8-as-sorozat',
        'X1': 'x1',
        'X2': 'x2',
        'X3': 'x3',
        'X4': 'x4',
        'X5': 'x5',
        'X6': 'x6',
        'X7': 'x7',
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

    def _build_search_url(self, marca: str, filters: Dict) -> str:
        """
        Build OLX search URL with filters

        Example:
        https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/bmw/?
        currency=EUR&
        search[filter_float_year:from]=2012&
        search[filter_float_year:to]=2015&
        search[filter_enum_model][0]=3-as-sorozat&
        search[filter_enum_petrol][0]=diesel
        """
        # Base URL with marca
        marca_lower = marca.lower().replace(' ', '-').replace('mercedes-benz', 'mercedes')
        url = f"{self.SEARCH_BASE}{marca_lower}/"

        # Build query parameters
        params = {
            'currency': 'EUR',
            'search[order]': 'relevance:desc'
        }

        # Add model (array parameter)
        if 'model' in filters and filters['model']:
            model_value = filters['model']
            # For BMW, convert "Seria 3" to "3-as-sorozat"
            if marca.lower() == 'bmw' and filters['model'] in self.BMW_MODELS:
                model_value = self.BMW_MODELS[filters['model']]
            params['search[filter_enum_model][0]'] = model_value

        # Add year range
        if 'year_from' in filters:
            params['search[filter_float_year:from]'] = filters['year_from']
        if 'year_to' in filters:
            params['search[filter_float_year:to]'] = filters['year_to']

        # Add price range
        if 'price_from' in filters:
            params['search[filter_float_price:from]'] = filters['price_from']
        if 'price_to' in filters:
            params['search[filter_float_price:to]'] = filters['price_to']

        # Add km range
        if 'km_from' in filters:
            params['search[filter_float_rulaj_pana:from]'] = filters['km_from']
        if 'km_to' in filters:
            params['search[filter_float_rulaj_pana:to]'] = filters['km_to']

        # Add engine size range (cm3)
        if 'engine_from' in filters:
            params['search[filter_float_enginesize:from]'] = filters['engine_from']
        if 'engine_to' in filters:
            params['search[filter_float_enginesize:to]'] = filters['engine_to']

        # Add power range (CP)
        if 'power_from' in filters:
            params['search[filter_float_engine_power:from]'] = filters['power_from']
        if 'power_to' in filters:
            params['search[filter_float_engine_power:to]'] = filters['power_to']

        # Add fuel type (array parameter)
        if 'fuel_type' in filters and filters['fuel_type']:
            fuel_olx = self.FUEL_TYPES.get(filters['fuel_type'].lower(), filters['fuel_type'])
            params['search[filter_enum_petrol][0]'] = fuel_olx

        # Add body type (array parameter)
        if 'body_type' in filters and filters['body_type']:
            body_olx = self.BODY_TYPES.get(filters['body_type'].lower(), filters['body_type'])
            params['search[filter_enum_car_body][0]'] = body_olx

        # Add transmission (array parameter)
        if 'transmission' in filters and filters['transmission']:
            trans_olx = self.TRANSMISSIONS.get(filters['transmission'].lower(), filters['transmission'])
            params['search[filter_enum_gearbox][0]'] = trans_olx

        # Build final URL
        query_string = urlencode(params)
        return f"{url}?{query_string}"

    async def search_cars_filtered(
        self,
        marca: str,
        model: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        km_from: Optional[int] = None,
        km_to: Optional[int] = None,
        fuel_type: Optional[str] = None,
        body_type: Optional[str] = None,
        transmission: Optional[str] = None,
        price_from: Optional[int] = None,
        price_to: Optional[int] = None,
        max_pages: int = 2
    ) -> List[Dict]:
        """
        Search with native OLX filters (much more accurate!)

        Args:
            marca: Brand (BMW, Mercedes, etc.)
            model: Model series (Seria 3, Golf, etc.)
            year_from: Min year
            year_to: Max year
            km_from: Min km
            km_to: Max km
            fuel_type: benzina, diesel, electric, hybrid, gpl
            body_type: sedan, hatchback, break, coupe, suv, cabrio
            transmission: manuala, automata
            price_from: Min price EUR
            price_to: Max price EUR
            max_pages: Max pages to scrape

        Returns:
            List of car listings
        """
        # Build filters dict
        filters = {}
        if model:
            filters['model'] = model
        if year_from:
            filters['year_from'] = year_from
        if year_to:
            filters['year_to'] = year_to
        if km_from:
            filters['km_from'] = km_from
        if km_to:
            filters['km_to'] = km_to
        if fuel_type:
            filters['fuel_type'] = fuel_type
        if body_type:
            filters['body_type'] = body_type
        if transmission:
            filters['transmission'] = transmission
        if price_from:
            filters['price_from'] = price_from
        if price_to:
            filters['price_to'] = price_to

        # Build search URL
        url = self._build_search_url(marca, filters)

        print(f"Searching OLX with filters: {marca} {model or ''}")
        print(f"Filters: Year {year_from}-{year_to}, KM {km_from}-{km_to}")
        print(f"URL: {url[:100]}...")

        listings = []
        session = await self._get_session()

        try:
            for page in range(1, max_pages + 1):
                page_url = url if page == 1 else f"{url}&page={page}"

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

                page_listings = self._parse_search_page(html, marca, model, filters)
                listings.extend(page_listings)

                print(f"Found {len(page_listings)} listings on page {page}")

                if not page_listings:
                    break

            print(f"Total: {len(listings)} listings")

        except Exception as e:
            print(f"Error: {e}")

        return listings

    def _parse_search_page(self, html: str, marca: str, model: Optional[str], filters: Dict) -> List[Dict]:
        """Parse search results page"""
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', {'data-cy': 'l-card'})

        listings = []
        for card in cards:
            try:
                listing = self._parse_listing_card(card, marca, model, filters)
                if listing:
                    listings.append(listing)
            except Exception as e:
                continue

        return listings

    def _parse_listing_card(self, card, marca: str, model: Optional[str], filters: Dict) -> Optional[Dict]:
        """Parse listing card - extract from OLX filtered results"""
        try:
            from urllib.parse import urljoin

            # Extract URL
            link = card.find('a', href=True)
            if not link:
                return None
            url = urljoin(self.BASE_URL, link['href'])

            # Extract title
            title_elem = card.find('h6') or card.find('h4')
            title = title_elem.get_text(strip=True) if title_elem else ""
            if not title:
                return None

            full_text = card.get_text()

            # Extract price
            price = self._extract_price_from_card(card)
            if not price or price < 3000:
                return None

            # Since we used filters, we can trust the filter values!
            # But still extract from text as backup
            year = self._extract_year(title, full_text) or filters.get('year_from')
            km = self._extract_km(title, full_text) or filters.get('km_from', 0)

            # Use filter values as primary source
            fuel_type = filters.get('fuel_type', 'benzina')
            body_type = filters.get('body_type', 'hatchback')
            transmission = filters.get('transmission', 'unknown')

            # Extract location
            location = self._extract_location(card)

            # Build listing
            listing = {
                'source': 'olx_filtered',
                'url': url,
                'marca': marca.title(),
                'model': model or marca,
                'model_series': model,
                'model_variant': None,  # Would need individual page scrape
                'an': year,
                'km': km,
                'pret': price,
                'combustibil': fuel_type,
                'putere_cp': None,  # Would need individual page scrape
                'capacitate_cilindrica': None,
                'transmisie': transmission,
                'tractiune': 'fata',  # Default
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

    def _extract_price_from_card(self, card) -> Optional[float]:
        """Extract and convert price - multiple methods for robustness"""
        # Method 1: data-testid attribute (most reliable)
        price_elem = card.find('p', {'data-testid': 'ad-price'})

        # Method 2: CSS class css-1j840l6 (user found this!)
        if not price_elem:
            price_elem = card.find('p', class_='css-1j840l6')

        # Method 3: CSS class css-blr5zl (user found this too!)
        if not price_elem:
            price_elem = card.find('p', class_='css-blr5zl')

        # Method 4: Any element with similar CSS class pattern
        if not price_elem:
            price_elem = card.find('p', class_=re.compile(r'css-[\w]+'))
            if price_elem and not re.search(r'\d+.*(?:EUR|euro|lei)', price_elem.get_text(), re.I):
                price_elem = None

        # Method 5: Regex search in text (fallback)
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
            match = re.search(r'\b(20\d{2})\b', source)
            if match:
                year = int(match.group(1))
                if 2000 <= year <= 2025:
                    return year
        return None

    def _extract_km(self, title: str, text: str) -> int:
        """Extract kilometers"""
        for source in [title, text]:
            match = re.search(r'(\d+)[.\s]?(\d+)?\s*km', source, re.IGNORECASE)
            if match:
                km_str = match.group(1) + (match.group(2) or '')
                try:
                    km = int(km_str)
                    if 0 <= km <= 1000000:
                        return km
                except ValueError:
                    pass
        return 0

    def _extract_location(self, card) -> str:
        """Extract location"""
        location_elem = card.find('p', {'data-testid': 'location-date'})
        if location_elem:
            location = location_elem.get_text(strip=True)
            return location.split(',')[0].split('-')[0].strip()
        return "Romania"


# Global instance
olx_filtered_scraper = OLXFilteredScraper()
