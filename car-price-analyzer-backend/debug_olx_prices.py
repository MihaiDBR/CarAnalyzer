"""
Debug OLX Price Extraction
Check all cards and their prices
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re


async def debug():
    url = "https://www.olx.ro/d/oferte/q-bmw-seria-3/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            cards = soup.find_all('div', {'data-cy': 'l-card'})
            print(f"Found {len(cards)} cards\n")

            for i, card in enumerate(cards[:10], 1):  # First 10 cards
                print(f"=== Card {i} ===")

                # Find link
                link = card.find('a', href=True)
                if link:
                    print(f"URL: {link['href'][:80]}")

                # Find all text that might be price
                all_text = card.get_text()

                # Find price pattern
                price_match = re.search(r'([\d\.,\s]+)\s*(EUR|euro|lei)', all_text, re.IGNORECASE)
                if price_match:
                    print(f"Price text: {price_match.group(0)}")
                else:
                    print("No price found in text")

                # Check for "Pret in consultare"
                if "consultare" in all_text.lower():
                    print("Contains 'Pret in consultare' - skip this")

                # Find title/description
                h6 = card.find('h6')
                if h6:
                    print(f"Title: {h6.get_text(strip=True)[:80]}")

                print()


if __name__ == "__main__":
    asyncio.run(debug())
