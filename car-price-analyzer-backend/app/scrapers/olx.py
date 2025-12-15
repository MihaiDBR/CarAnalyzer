# ============================================
# BACKEND - app/scrapers/olx.py
# Scraper real pentru OLX.ro
# ============================================

import asyncio
import aiohttp
import re
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup

from app.scrapers.autovit import CarListing  # Refolosim dataclass-ul

class OLXScraper:
    """Scraper pentru OLX.ro"""
    
    BASE_URL = "https://www.olx.ro"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
        }
    
    async def search_cars(self, marca: str, model: str) -> List[CarListing]:
        """
        Caută mașini pe OLX
        
        Args:
            marca: Marca mașinii
            model: Modelul mașinii
            
        Returns:
            Lista de anunțuri găsite
        """
        # Construiește URL de căutare
        search_term = f"{marca}-{model}".lower().replace(' ', '-')
        search_url = f"{self.BASE_URL}/auto-masini-moto-ambarcatiuni/autoturisme/{search_term}/"
        
        print(f"🔍 Scraping OLX: {search_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=self.headers) as response:
                    if response.status != 200:
                        print(f"❌ OLX returned status {response.status}")
                        return []
                    
                    html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Găsește toate anunțurile
            listings = []
            
            # OLX folosește diferite structuri, încercăm ambele
            ads = soup.find_all('div', {'data-cy': 'l-card'})
            if not ads:
                ads = soup.find_all('div', {'class': 'css-1sw7q4x'})
            
            print(f"✓ Găsite {len(ads)} anunțuri pe OLX")
            
            for ad in ads:
                try:
                    listing = self._parse_listing(ad, marca, model)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    print(f"⚠ Eroare la parsare anunț OLX: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            print(f"❌ Eroare la scraping OLX: {e}")
            return []
    
    def _parse_listing(self, ad, marca: str, model: str) -> Optional[CarListing]:
        """
        Parsează un anunț OLX
        
        Args:
            ad: Element BeautifulSoup
            marca: Marca căutată
            model: Modelul căutat
            
        Returns:
            CarListing sau None
        """
        try:
            # Extract URL
            link = ad.find('a', {'class': ['css-rc5s2u', 'css-z3gu2d']})
            if not link:
                return None
            
            url = link.get('href', '')
            if not url:
                return None
            if not url.startswith('http'):
                url = self.BASE_URL + url
            
            # Extract preț
            price_elem = ad.find('p', {'data-testid': 'ad-price'})
            if not price_elem:
                price_elem = ad.find('span', {'class': 'css-10b0gli'})
            
            if not price_elem:
                return None
            
            price_text = price_elem.text.strip()
            price_text = price_text.replace(' ', '').replace('lei', '').replace('.', '').replace(',', '.')
            
            try:
                price_lei = float(price_text)
                # Conversie aproximativă lei -> EUR (1 EUR ≈ 4.95 lei)
                price = price_lei / 4.95
            except:
                return None
            
            # Extract titlu
            title_elem = ad.find('h6', {'class': ['css-16v5mdi', 'css-v3vynn']})
            if not title_elem:
                title_elem = link
            
            title = title_elem.text.strip() if title_elem else ""
            
            # Extract detalii din parametri
            params = ad.find_all('span', {'class': ['css-643j0o', 'css-1lkc37f']})
            
            an = None
            km = None
            combustibil = "Necunoscut"
            
            for param in params:
                text = param.text.strip()
                
                # Identifică anul
                if re.match(r'^\d{4}$', text):
                    an = int(text)
                
                # Identifică kilometrii
                elif 'km' in text.lower():
                    km_text = ''.join(filter(str.isdigit, text))
                    if km_text:
                        km = int(km_text)
                
                # Identifică combustibilul
                elif any(fuel in text.lower() for fuel in ['benzin', 'diesel', 'electric', 'hybrid', 'gpl']):
                    combustibil = text
            
            # Extract locație
            location_elem = ad.find('p', {'data-testid': 'location-date'})
            if not location_elem:
                location_elem = ad.find('span', {'class': 'css-1a4brun'})
            
            locatie = "Necunoscută"
            if location_elem:
                location_text = location_elem.text.strip()
                # Separă locația de dată (format: "București - Acum 2 zile")
                if '-' in location_text:
                    locatie = location_text.split('-')[0].strip()
                else:
                    locatie = location_text
            
            # Extract imagini
            imagini = []
            img_elem = ad.find('img', {'class': ['css-8wsg1m', 'css-1bmvjcs']})
            if img_elem and img_elem.get('src'):
                imagini.append(img_elem['src'])
            
            # Data publicării (OLX nu oferă întotdeauna această informație)
            data_publicare = datetime.now()
            
            return CarListing(
                source="olx",
                url=url,
                price=price,
                marca=marca.title(),
                model=model.title(),
                an=an or 0,
                km=km or 0,
                combustibil=combustibil,
                locatie=locatie,
                dotari=[],
                data_publicare=data_publicare,
                imagini=imagini,
                descriere=""
            )
            
        except Exception as e:
            print(f"Eroare parsare listing OLX: {e}")
            return None
    
    async def get_listing_details(self, url: str) -> dict:
        """
        Obține detalii complete despre un anunț OLX
        
        Args:
            url: URL-ul anunțului
            
        Returns:
            Dict cu dotări, imagini, descriere
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract descriere
            descriere = ""
            desc_elem = soup.find('div', {'class': 'css-1t507yq'})
            if desc_elem:
                descriere = desc_elem.text.strip()
            
            # Extract imagini
            imagini = []
            image_gallery = soup.find_all('img', {'class': 'css-1bmvjcs'})
            imagini = [img['src'] for img in image_gallery if img.get('src')]
            
            # Extract dotări din descriere (OLX nu are secțiune separată)
            dotari = []
            common_features = [
                'climatronic', 'clima', 'piele', 'xenon', 'led', 'senzori', 
                'camera', 'navigatie', 'gps', 'scaune încălzite', 'cruise control',
                'keyless', 'trapă', 'jante aliaj'
            ]
            
            descriere_lower = descriere.lower()
            for feature in common_features:
                if feature in descriere_lower:
                    dotari.append(feature.title())
            
            return {
                'dotari': dotari,
                'imagini': imagini,
                'descriere': descriere,
                'telefon': None  # OLX nu afișează telefon direct
            }
            
        except Exception as e:
            print(f"Eroare la obținere detalii OLX: {e}")
            return {
                'dotari': [],
                'imagini': [],
                'descriere': '',
                'telefon': None
            }