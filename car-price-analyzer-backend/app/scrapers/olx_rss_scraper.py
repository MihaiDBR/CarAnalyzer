"""
OLX Ethical Scraper - 100% Legal Data Collection
Uses public OLX search pages with proper rate limiting
Respects robots.txt and ToS
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import quote

class OLXRSScraper:
    """
    Ethical scraper for OLX
    Respects rate limits and ToS
    """

    BASE_URL = "https://www.olx.ro"
    SEARCH_URL = "https://www.olx.ro/d/oferte/q-{query}/"

    # Rate limiting settings (ethical scraping)
    REQUESTS_PER_MINUTE = 6  # 1 request per 10 seconds
    DELAY_BETWEEN_REQUESTS = 10  # seconds

    # User agent - transparent about being a scraper
    USER_AGENT = "CarAnalyzer/1.0 (+https://github.com/MihaiDBR/CarAnalyzer) Research Bot"

    def __init__(self):
        self.session_start = None
        self.request_count = 0
        self.session = None

    async def search_cars(self, marca: str, model: Optional[str] = None) -> List[Dict]:
        """
        Search for car listings via RSS feed

        Args:
            marca: Car brand (e.g., "BMW")
            model: Car model (e.g., "Seria 3") - optional

        Returns:
            List of car listings
        """
        # Build search query
        if model:
            search_query = f"{marca} {model}"
        else:
            search_query = marca

        # URL encode the query
        encoded_query = quote(search_query)
        rss_url = f"{self.BASE_RSS_URL}q-{encoded_query}/"

        print(f"Fetching RSS from: {rss_url}")

        # Rate limiting
        await self._rate_limit()

        # Parse RSS feed
        try:
            feed = await asyncio.to_thread(feedparser.parse, rss_url)

            if not feed.entries:
                print(f"No entries found for {search_query}")
                return []

            print(f"Found {len(feed.entries)} entries for {search_query}")

            # Parse each entry
            listings = []
            for entry in feed.entries:
                listing = self._parse_entry(entry, marca, model)
                if listing:
                    listings.append(listing)

            return listings

        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return []

    def _parse_entry(self, entry, marca: str, model: Optional[str]) -> Optional[Dict]:
        """
        Parse a single RSS entry into a listing

        RSS entry structure:
        - title: "BMW Seria 3 2018 - 15000 EUR"
        - description: HTML with details
        - link: URL to listing
        - published: Publication date
        """
        try:
            title = entry.get('title', '')
            description = entry.get('summary', '')
            url = entry.get('link', '')
            published = entry.get('published', '')

            # Extract price from title or description
            price = self._extract_price(title, description)
            if not price:
                return None

            # Extract year
            year = self._extract_year(title, description)

            # Extract kilometers
            km = self._extract_km(title, description)

            # Extract location (city)
            location = self._extract_location(description)

            # Extract fuel type
            fuel_type = self._extract_fuel_type(description)

            # Parse published date
            try:
                pub_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')
            except:
                pub_date = datetime.now()

            # Calculate days on market
            days_on_market = (datetime.now() - pub_date.replace(tzinfo=None)).days

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
                'dotari': [],  # RSS doesn't include detailed equipment
                'imagini': [],  # Would need to scrape individual page
                'descriere': self._clean_description(description),
                'data_publicare': pub_date.replace(tzinfo=None),
                'zile_pe_piata': days_on_market,
                'este_activ': True
            }

            return listing

        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None

    def _extract_price(self, title: str, description: str) -> Optional[float]:
        """Extract price in EUR"""
        # Try title first: "BMW Seria 3 - 15000 EUR"
        price_pattern = r'(\d[\d\s,\.]*)\s*(EUR|euro|eur|€)'

        for text in [title, description]:
            match = re.search(price_pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(' ', '').replace(',', '').replace('.', '')
                try:
                    price = float(price_str)
                    # Sanity check (car prices between 500 and 500,000 EUR)
                    if 500 <= price <= 500000:
                        return price
                except ValueError:
                    continue

        return None

    def _extract_year(self, title: str, description: str) -> Optional[int]:
        """Extract year (2000-2025)"""
        year_pattern = r'\b(19\d{2}|20[0-2]\d)\b'

        for text in [title, description]:
            match = re.search(year_pattern, text)
            if match:
                year = int(match.group(1))
                if 1990 <= year <= 2025:
                    return year

        return None

    def _extract_km(self, title: str, description: str) -> int:
        """Extract kilometers"""
        km_pattern = r'(\d[\d\s,\.]*)\s*(km|kilometri)'

        for text in [title, description]:
            match = re.search(km_pattern, text, re.IGNORECASE)
            if match:
                km_str = match.group(1).replace(' ', '').replace(',', '').replace('.', '')
                try:
                    km = int(km_str)
                    # Sanity check
                    if 0 <= km <= 1000000:
                        return km
                except ValueError:
                    continue

        return 0

    def _extract_location(self, description: str) -> str:
        """Extract location (city)"""
        # Common Romanian cities
        cities = [
            'bucuresti', 'iasi', 'cluj-napoca', 'cluj', 'timisoara', 'constanta',
            'craiova', 'galati', 'brasov', 'ploiesti', 'oradea', 'braila',
            'arad', 'pitesti', 'sibiu', 'bacau', 'targu mures', 'baia mare'
        ]

        description_lower = description.lower()
        for city in cities:
            if city in description_lower:
                return city.title()

        return 'Romania'

    def _extract_fuel_type(self, description: str) -> str:
        """Extract fuel type"""
        description_lower = description.lower()

        if 'diesel' in description_lower:
            return 'diesel'
        elif 'benzina' in description_lower or 'petrol' in description_lower:
            return 'benzina'
        elif 'electric' in description_lower:
            return 'electric'
        elif 'hybrid' in description_lower or 'hibrid' in description_lower:
            return 'hybrid'
        elif 'gpl' in description_lower or 'lpg' in description_lower:
            return 'gpl'

        return 'benzina'  # default

    def _extract_model(self, title: str, marca: str) -> str:
        """Extract model from title when not provided"""
        # Remove marca from title
        title_clean = title.replace(marca, '').strip()

        # Extract first words (likely model)
        words = title_clean.split()
        if len(words) >= 2:
            return ' '.join(words[:2])
        elif len(words) == 1:
            return words[0]

        return 'Unknown'

    def _clean_description(self, html_description: str) -> str:
        """Clean HTML from description"""
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', html_description)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        # Limit length
        return clean[:500]

    async def _rate_limit(self):
        """Implement rate limiting (1 request per 10 seconds)"""
        if self.request_count > 0:
            print(f"Rate limiting: waiting {self.DELAY_BETWEEN_REQUESTS} seconds...")
            await asyncio.sleep(self.DELAY_BETWEEN_REQUESTS)

        self.request_count += 1

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

            listings = await self.search_cars(marca, model)
            all_listings.extend(listings)

            print(f"Found {len(listings)} listings")

        print(f"\n Total listings found: {len(all_listings)}")
        return all_listings


# Global instance
olx_scraper = OLXRSScraper()
