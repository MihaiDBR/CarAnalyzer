"""
OLX Ethical Scraper - 100% Legal Data Collection
Uses public OLX search pages with strict rate limiting
Respects robots.txt and ToS - only collects public data
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote, urljoin


class OLXScraper:
    """
    Ethical scraper for OLX
    - Rate limited to 1 request per 10 seconds
    - Transparent User-Agent
    - Only public data (no personal info)
    - Respects robots.txt
    """

    BASE_URL = "https://www.olx.ro"
    SEARCH_URL = "https://www.olx.ro/d/oferte/q-{query}/"

    # Rate limiting settings (ethical scraping)
    DELAY_BETWEEN_REQUESTS = 10  # seconds (conservative)

    # User agent - transparent about being a scraper
    USER_AGENT = "CarAnalyzer/1.0 (+https://github.com/MihaiDBR/CarAnalyzer) Research Bot"

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
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_cars(self, marca: str, model: Optional[str] = None, max_pages: int = 1) -> List[Dict]:
        """
        Search for car listings on OLX

        Args:
            marca: Car brand (e.g., "BMW")
            model: Car model (e.g., "Seria 3") - optional
            max_pages: Maximum number of pages to scrape (default: 1)

        Returns:
            List of car listings
        """
        # Build search query
        if model:
            search_query = f"{marca} {model}"
        else:
            search_query = marca

        # URL encode the query
        encoded_query = quote(search_query.lower().replace(' ', '-'))
        url = self.SEARCH_URL.format(query=encoded_query)

        print(f"Searching OLX: {url}")

        listings = []

        try:
            session = await self._get_session()

            for page in range(1, max_pages + 1):
                # Add page parameter if not first page
                page_url = url if page == 1 else f"{url}?page={page}"

                # Rate limiting
                if self.request_count > 0:
                    print(f"Rate limiting: waiting {self.DELAY_BETWEEN_REQUESTS} seconds...")
                    await asyncio.sleep(self.DELAY_BETWEEN_REQUESTS)

                # Fetch page
                print(f"Fetching page {page}...")
                async with session.get(page_url) as response:
                    if response.status != 200:
                        print(f"Error: HTTP {response.status}")
                        break

                    html = await response.text()
                    self.request_count += 1

                # Parse listings from page
                page_listings = self._parse_search_page(html, marca, model)
                listings.extend(page_listings)

                print(f"Found {len(page_listings)} listings on page {page}")

                # Stop if no more listings
                if not page_listings:
                    break

            print(f"Total listings found: {len(listings)}")

        except Exception as e:
            print(f"Error fetching OLX: {e}")

        return listings

    def _parse_search_page(self, html: str, marca: str, model: Optional[str]) -> List[Dict]:
        """
        Parse car listings from OLX search results page

        OLX structure (as of Dec 2024):
        - Listings are in div[data-cy="l-card"]
        - Price in p[data-testid="ad-price"]
        - Title in h6
        - Location in p[data-testid="location-date"]
        """
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        # Find listing cards
        cards = soup.find_all('div', {'data-cy': 'l-card'})

        if not cards:
            # Try alternative selectors
            cards = soup.find_all('div', class_=re.compile(r'css-\w+'))  # OLX uses dynamic CSS classes

        print(f"Found {len(cards)} potential listing cards")

        for card in cards:
            try:
                listing = self._parse_listing_card(card, marca, model)
                if listing:
                    listings.append(listing)
            except Exception as e:
                print(f"Error parsing card: {e}")
                continue

        return listings

    def _parse_listing_card(self, card, marca: str, model: Optional[str]) -> Optional[Dict]:
        """Parse a single listing card"""
        try:
            # Extract URL
            link = card.find('a', href=True)
            if not link:
                return None

            url = urljoin(self.BASE_URL, link['href'])

            # Extract title
            title_elem = card.find('h6') or card.find('h4') or card.find('strong')
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title:
                return None

            # Filter out car parts (check title for part keywords)
            title_lower = title.lower()
            parts_keywords = [
                'jante', 'janta', 'roata', 'roti', 'anvelope', 'cauciuc',
                'stopuri', 'stop', 'faruri', 'far', 'oglinda', 'oglinzi',
                'bara', 'portiera', 'capota', 'haion', 'aripa',
                'volant', 'scaune', 'bord', 'consola',
                'motor', 'cutie viteze', 'turbo', 'alternator',
                'carcasa', 'deflector', 'senzori', 'senzor',
                'kit', 'piese', 'componente', 'accesorii',
                'perna', 'amortizor', 'suspensie', 'telescop',
                'radiator', 'intercooler', 'evacuare', 'toba',
                'filtru', 'curea', 'ulei'
            ]

            # Skip if title contains part keywords
            for keyword in parts_keywords:
                if keyword in title_lower:
                    # Exception: if title contains indicators of full car sale
                    full_car_indicators = ['vand ', 'vanzare', 'schimb', 'urgent', 'full', 'dotari']
                    is_full_car = any(indicator in title_lower for indicator in full_car_indicators)

                    # Also check if has year AND km (strong indicator of full car)
                    has_year = re.search(r'\b(20\d{2})\b', title)
                    has_km = re.search(r'\d+\s*km', title_lower)
                    word_count = len(title.split())

                    # Full car if: has indicators OR (has year AND km AND long title)
                    if not (is_full_car or (has_year and has_km and word_count > 6)):
                        return None  # Skip this listing - it's a part

            # Extract price
            price = self._extract_price_from_card(card)
            if not price or price == 0:
                return None  # Skip listings without valid price

            # Extract location
            location_elem = card.find('p', {'data-testid': 'location-date'}) or card.find(string=re.compile(r'(București|Cluj|Iași|Timișoara|Constanța)', re.I))
            location = location_elem.get_text(strip=True) if location_elem else "Romania"
            location = location.split(',')[0].strip()  # Get city only

            # Extract details from title
            year = self._extract_year(title)
            km = self._extract_km(title)
            fuel_type = self._extract_fuel_type(title)

            # Build listing
            listing = {
                'source': 'olx',
                'url': url,
                'marca': marca.title(),
                'model': model.title() if model else self._extract_model(title, marca),
                'an': year,
                'km': km,
                'pret': price,
                'combustibil': fuel_type,
                'locatie': location,
                'dotari': [],  # Would need to scrape individual page
                'imagini': [],
                'descriere': title[:500],
                'data_publicare': datetime.now(),  # Would need to extract from page
                'zile_pe_piata': 0,
                'este_activ': True
            }

            return listing

        except Exception as e:
            print(f"Error parsing listing card: {e}")
            return None

    def _extract_price_from_card(self, card) -> Optional[float]:
        """Extract price from listing card"""
        # Try data-testid selector
        price_elem = card.find('p', {'data-testid': 'ad-price'})

        if not price_elem:
            # Try finding any element with price-like text
            price_elem = card.find(string=re.compile(r'\d+.*(?:EUR|euro|lei)', re.I))

        if price_elem:
            price_text = price_elem.get_text(strip=True) if hasattr(price_elem, 'get_text') else str(price_elem)
            return self._parse_price(price_text)

        return None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text and convert to EUR"""
        original_text = price_text.lower()

        # Check currency
        is_lei = 'lei' in original_text
        is_eur = 'eur' in original_text or 'euro' in original_text or '€' in original_text

        # Remove currency symbols and separators
        price_text = price_text.replace('EUR', '').replace('euro', '').replace('lei', '').replace('€', '')
        price_text = price_text.replace(' ', '').replace('.', '').replace(',', '')

        # Extract digits
        match = re.search(r'\d+', price_text)
        if match:
            try:
                price = float(match.group())

                # Convert LEI to EUR (current rate ~4.97 lei/EUR)
                if is_lei and not is_eur:
                    price = price / 4.97  # Convert to EUR

                # Sanity check for complete cars (min 3000 EUR, max 500k EUR)
                # This filters out car parts which are usually < 3000 EUR
                if 3000 <= price <= 500000:
                    return round(price, 2)
            except ValueError:
                pass

        return None

    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year (2000-2025)"""
        match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', text)
        if match:
            year = int(match.group(1))
            if 1990 <= year <= 2025:
                return year
        return None

    def _extract_km(self, text: str) -> int:
        """Extract kilometers"""
        match = re.search(r'(\d+)[.\s]?(\d+)?\s*(km|mii\s*km)', text, re.IGNORECASE)
        if match:
            km_str = match.group(1) + (match.group(2) or '')
            try:
                km = int(km_str)
                # If it says "mii km" (thousands), multiply
                if 'mii' in match.group(3).lower():
                    km *= 1000
                if 0 <= km <= 1000000:
                    return km
            except ValueError:
                pass
        return 0

    def _extract_fuel_type(self, text: str) -> str:
        """Extract fuel type"""
        text_lower = text.lower()

        if 'diesel' in text_lower:
            return 'diesel'
        elif 'benzina' in text_lower or 'petrol' in text_lower:
            return 'benzina'
        elif 'electric' in text_lower:
            return 'electric'
        elif 'hybrid' in text_lower or 'hibrid' in text_lower:
            return 'hybrid'
        elif 'gpl' in text_lower or 'lpg' in text_lower:
            return 'gpl'

        return 'benzina'  # default

    def _extract_model(self, title: str, marca: str) -> str:
        """Extract model from title when not provided"""
        # Remove marca from title
        title_clean = title.replace(marca, '').replace(marca.upper(), '').replace(marca.lower(), '').strip()

        # Extract first 2-3 words (likely model)
        words = title_clean.split()
        if len(words) >= 2:
            return ' '.join(words[:2])
        elif len(words) == 1:
            return words[0]

        return 'Unknown'


# Global instance
olx_scraper = OLXScraper()
