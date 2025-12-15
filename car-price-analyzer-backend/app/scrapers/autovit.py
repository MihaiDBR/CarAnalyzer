# ============================================
# BACKEND - app/scrapers/autovit.py
# Scraper real pentru Autovit.ro
# ============================================

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

@dataclass
class CarListing:
    """Structură pentru un anunț de mașină"""
    source: str
    url: str
    price: float
    marca: str
    model: str
    an: int
    km: int
    combustibil: str
    locatie: str
    dotari: List[str]
    data_publicare: datetime
    imagini: List[str]
    descriere: str
    telefon: Optional[str] = None

class AutovitScraper:
    """Scraper pentru Autovit.ro"""
    
    BASE_URL = "https://www.autovit.ro"
    
    def __init__(self, headless: bool = True):
        """
        Inițializează scraper-ul
        
        Args:
            headless: Dacă True, browser-ul rulează fără UI
        """
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
    
    async def search_cars(
        self, 
        marca: str, 
        model: str,
        an_min: Optional[int] = None,
        an_max: Optional[int] = None
    ) -> List[CarListing]:
        """
        Caută mașini pe Autovit
        
        Args:
            marca: Marca mașinii
            model: Modelul mașinii
            an_min: An minim (opțional)
            an_max: An maxim (opțional)
            
        Returns:
            Lista de anunțuri găsite
        """
        # Construiește URL de căutare
        search_url = f"{self.BASE_URL}/autoturisme/{marca.lower().replace(' ', '-')}/{model.lower().replace(' ', '-')}"
        
        # Adaugă filtre pentru an
        params = []
        if an_min:
            params.append(f"search%5Bfilter_float_year%3Afrom%5D={an_min}")
        if an_max:
            params.append(f"search%5Bfilter_float_year%3Ato%5D={an_max}")
        
        if params:
            search_url += "?" + "&".join(params)
        
        print(f"🔍 Scraping Autovit: {search_url}")
        
        try:
            self.driver.get(search_url)
            await asyncio.sleep(2)  # Așteaptă încărcarea
            
            # Scroll pentru a încărca toate rezultatele (lazy loading)
            await self._scroll_to_bottom()
            
            # Parse HTML
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Găsește toate anunțurile
            listings = []
            articles = soup.find_all('article', {'data-testid': 'listing-ad'})
            
            print(f"✓ Găsite {len(articles)} anunțuri pe Autovit")
            
            for article in articles:
                try:
                    listing = self._parse_listing(article, marca, model)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    print(f"⚠ Eroare la parsare anunț: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            print(f"❌ Eroare la scraping Autovit: {e}")
            return []
    
    async def _scroll_to_bottom(self):
        """Scroll la sfârșitul paginii pentru a încărca toate rezultatele"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(1.5)
            
            # Calculează noua înălțime
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
    
    def _parse_listing(self, article, marca: str, model: str) -> Optional[CarListing]:
        """
        Parsează un anunț individual
        
        Args:
            article: Element BeautifulSoup
            marca: Marca căutată
            model: Modelul căutat
            
        Returns:
            CarListing sau None dacă parsarea eșuează
        """
        try:
            # Extract URL
            link = article.find('a', {'class': 'offer-title__link'})
            if not link:
                return None
            
            url = link.get('href', '')
            if not url.startswith('http'):
                url = self.BASE_URL + url
            
            # Extract preț
            price_elem = article.find('span', {'class': 'offer-price__number'})
            if not price_elem:
                return None
            
            price_text = price_elem.text.strip()
            price_text = price_text.replace(' ', '').replace('EUR', '').replace('.', '').replace(',', '.')
            
            try:
                price = float(price_text)
            except:
                return None
            
            # Extract titlu
            title = link.text.strip()
            
            # Extract detalii (an, km, combustibil)
            details = article.find_all('li', {'class': 'offer-item__params-item'})
            
            an = None
            km = None
            combustibil = "Necunoscut"
            
            for detail in details:
                text = detail.text.strip()
                
                # Identifică anul (4 cifre)
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
            location_elem = article.find('span', {'class': 'offer-item__location'})
            locatie = location_elem.text.strip() if location_elem else "Necunoscută"
            
            # Extract data publicării
            date_elem = article.find('span', {'class': 'offer-item__add-date'})
            data_publicare = self._parse_date(date_elem.text.strip()) if date_elem else datetime.now()
            
            # Extract imagini (prima imagine)
            imagini = []
            img_elem = article.find('img', {'class': 'offer-item__photo'})
            if img_elem and img_elem.get('src'):
                imagini.append(img_elem['src'])
            
            return CarListing(
                source="autovit",
                url=url,
                price=price,
                marca=marca.title(),
                model=model.title(),
                an=an or 0,
                km=km or 0,
                combustibil=combustibil,
                locatie=locatie,
                dotari=[],  # Se completează la scraping detaliat
                data_publicare=data_publicare,
                imagini=imagini,
                descriere=""
            )
            
        except Exception as e:
            print(f"Eroare parsare listing: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parsează data de publicare din text
        
        Args:
            date_str: Text cu data (ex: "Astăzi", "Ieri", "Acum 3 zile")
            
        Returns:
            Obiect datetime
        """
        date_str = date_str.lower()
        
        if 'astăzi' in date_str or 'today' in date_str:
            return datetime.now()
        elif 'ieri' in date_str or 'yesterday' in date_str:
            return datetime.now() - timedelta(days=1)
        else:
            # Încearcă să extragă numărul de zile
            match = re.search(r'(\d+)', date_str)
            if match:
                days = int(match.group(1))
                return datetime.now() - timedelta(days=days)
        
        return datetime.now()
    
    async def get_listing_details(self, url: str) -> dict:
        """
        Obține detalii complete despre un anunț
        
        Args:
            url: URL-ul anunțului
            
        Returns:
            Dict cu dotări, imagini, descriere, telefon
        """
        try:
            self.driver.get(url)
            await asyncio.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract dotări
            dotari = []
            equipment_section = soup.find('div', {'class': 'offer-features'})
            if equipment_section:
                items = equipment_section.find_all('li')
                dotari = [item.text.strip() for item in items]
            
            # Extract imagini
            imagini = []
            image_gallery = soup.find_all('img', {'class': 'photo-item'})
            imagini = [img['src'] for img in image_gallery if img.get('src')]
            
            # Extract descriere
            descriere = ""
            desc_elem = soup.find('div', {'class': 'offer-description'})
            if desc_elem:
                descriere = desc_elem.text.strip()
            
            # Extract telefon (dacă e vizibil)
            telefon = None
            phone_elem = soup.find('a', {'class': 'phone-number'})
            if phone_elem:
                telefon = phone_elem.text.strip()
            
            return {
                'dotari': dotari,
                'imagini': imagini,
                'descriere': descriere,
                'telefon': telefon
            }
            
        except Exception as e:
            print(f"Eroare la obținere detalii: {e}")
            return {
                'dotari': [],
                'imagini': [],
                'descriere': '',
                'telefon': None
            }
    
    def close(self):
        """Închide browser-ul"""
        try:
            self.driver.quit()
        except:
            pass