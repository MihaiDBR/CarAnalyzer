"""
Debug OLX HTML Structure
Check what the actual HTML looks like
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def debug():
    url = "https://www.olx.ro/d/oferte/q-bentley-bentayga/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()

            # Save HTML to file for inspection
            with open('olx_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)

            print("HTML saved to olx_debug.html")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Find all div elements with data-cy="l-card"
            cards = soup.find_all('div', {'data-cy': 'l-card'})
            print(f"\nFound {len(cards)} cards with data-cy='l-card'")

            if cards:
                print("\n=== First Card Details ===")
                card = cards[0]
                print(f"Card HTML:\n{card.prettify()[:1000]}\n")

                # Try to find price
                price_elem = card.find('p', {'data-testid': 'ad-price'})
                print(f"Price element (data-testid='ad-price'): {price_elem}")

                # Try alternative price selectors
                all_p = card.find_all('p')
                print(f"\nAll <p> tags in card ({len(all_p)}):")
                for i, p in enumerate(all_p[:5]):
                    print(f"  {i+1}. {p.get_text(strip=True)[:100]}")

                # Find links
                link = card.find('a', href=True)
                print(f"\nLink: {link['href'] if link else 'None'}")

                # Find title
                h6 = card.find('h6')
                print(f"Title (h6): {h6.get_text(strip=True) if h6 else 'None'}")


if __name__ == "__main__":
    asyncio.run(debug())
