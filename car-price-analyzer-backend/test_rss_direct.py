"""
Direct RSS Feed Test - Check if OLX RSS works
"""
import feedparser

# Test different OLX RSS URLs
test_urls = [
    "https://www.olx.ro/rss/oferte/q-bmw/",
    "https://www.olx.ro/rss/oferte/q-bmw-seria-3/",
    "https://www.olx.ro/d/oferte/q-bmw/feed/",
]

print("\n=== Testing OLX RSS Feeds ===\n")

for url in test_urls:
    print(f"Testing: {url}")
    try:
        feed = feedparser.parse(url)

        print(f"  Status: {feed.get('status', 'unknown')}")
        print(f"  Entries: {len(feed.entries)}")

        if feed.entries:
            print(f"  First entry title: {feed.entries[0].get('title', 'N/A')}")
            print(f"  First entry link: {feed.entries[0].get('link', 'N/A')}")

        print()

    except Exception as e:
        print(f"  ERROR: {e}\n")

print("="*60)
